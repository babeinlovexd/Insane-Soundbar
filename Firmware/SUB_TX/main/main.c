#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"
#include "driver/i2c.h"
#include "driver/gpio.h"
#include "esp_now.h"
#include "esp_wifi.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "esp_log.h"
#include "esp_mac.h"

#define I2C_SLAVE_SCL_IO 22
#define I2C_SLAVE_SDA_IO 21
#define I2C_SLAVE_NUM I2C_NUM_0
#define I2C_SLAVE_TX_BUF_LEN 256
#define I2C_SLAVE_RX_BUF_LEN 256
#define I2C_SLAVE_ADDRESS 0x22

#define INT_PIN 23

#define I2S_BCLK_PIN 25
#define I2S_LRCK_PIN 26
#define I2S_DIN_PIN 27

#define SAMPLE_RATE 16000

static const char *TAG = "SUB_TX";

static volatile uint8_t reg_sub_state = 0;
static volatile uint8_t reg_sub_rssi = 0;
static volatile uint8_t reg_buf_delay = 0;

static uint8_t peer_mac[ESP_NOW_ETH_ALEN] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
static bool is_unicast = false;
static int failed_acks = 0;
#define MAX_FAILED_ACKS 20

static i2s_chan_handle_t rx_chan;

#define AUDIO_PAYLOAD_SIZE 240
typedef struct {
    uint8_t buf_delay;
    int16_t audio_data[AUDIO_PAYLOAD_SIZE / 2];
} __attribute__((packed)) audio_packet_t;

static void trigger_interrupt(void) {
    gpio_set_level(INT_PIN, 1);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level(INT_PIN, 0);
}

static void esp_now_send_cb(const uint8_t *mac_addr, esp_now_send_status_t status) {
    if (status == ESP_NOW_SEND_SUCCESS) {
        failed_acks = 0;
        if (reg_sub_state == 0 && is_unicast) {
            reg_sub_state = 1;
        }
    } else {
        if (is_unicast) {
            failed_acks++;
            if (failed_acks > MAX_FAILED_ACKS) {
                if (reg_sub_state == 1) {
                    reg_sub_state = 0;
                    reg_sub_rssi = 0;
                    trigger_interrupt();
                }

                // Fallback to broadcast
                esp_now_del_peer(peer_mac);
                memset(peer_mac, 0xFF, ESP_NOW_ETH_ALEN);
                esp_now_peer_info_t peerInfo = {};
                memcpy(peerInfo.peer_addr, peer_mac, ESP_NOW_ETH_ALEN);
                peerInfo.channel = 1;
                peerInfo.ifidx = WIFI_IF_STA;
                peerInfo.encrypt = false;
                esp_now_add_peer(&peerInfo);

                is_unicast = false;
                failed_acks = 0;
            }
        }
    }
}

static void esp_now_recv_cb(const esp_now_recv_info_t *esp_now_info, const uint8_t *data, int data_len) {
    if (esp_now_info == NULL || esp_now_info->rx_ctrl == NULL) {
        return;
    }

    int rssi = esp_now_info->rx_ctrl->rssi;
    int rssi_mapped = rssi + 100;
    if (rssi_mapped < 0) rssi_mapped = 0;
    if (rssi_mapped > 255) rssi_mapped = 255;
    reg_sub_rssi = (uint8_t)rssi_mapped;

    if (reg_sub_state == 0) {
        reg_sub_state = 1;
    }
    failed_acks = 0;

    if (!is_unicast) {
        esp_now_del_peer(peer_mac);
        memcpy(peer_mac, esp_now_info->src_addr, ESP_NOW_ETH_ALEN);
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, peer_mac, ESP_NOW_ETH_ALEN);
        peerInfo.channel = 1;
        peerInfo.ifidx = WIFI_IF_STA;
        peerInfo.encrypt = false;
        esp_now_add_peer(&peerInfo);

        is_unicast = true;
    }
}

static void i2c_slave_task(void *arg) {
    uint8_t rx_data[32];
    uint8_t current_reg = 0;

    while (1) {
        int size = i2c_slave_read_buffer(I2C_SLAVE_NUM, rx_data, sizeof(rx_data), pdMS_TO_TICKS(10));
        if (size > 0) {
            current_reg = rx_data[0];

            if (size > 1) {
                // Write command with data
                for (int i = 1; i < size; i++) {
                    if (current_reg == 0x03) {
                        reg_buf_delay = rx_data[i];
                    }
                    current_reg++;
                }
            } else {
                // Register select command
                i2c_reset_tx_fifo(I2C_SLAVE_NUM);
                uint8_t vals[3] = {0};
                int tx_len = 0;

                if (current_reg == 0x01) {
                    vals[0] = reg_sub_state;
                    vals[1] = reg_sub_rssi;
                    vals[2] = reg_buf_delay;
                    tx_len = 3;
                }
                else if (current_reg == 0x02) {
                    vals[0] = reg_sub_rssi;
                    vals[1] = reg_buf_delay;
                    tx_len = 2;
                }
                else if (current_reg == 0x03) {
                    vals[0] = reg_buf_delay;
                    tx_len = 1;
                }

                if (tx_len > 0) {
                    i2c_slave_write_buffer(I2C_SLAVE_NUM, vals, tx_len, pdMS_TO_TICKS(10));
                }
            }
        }
    }
}

static void audio_task(void *arg) {
    #define FRAME_COUNT (AUDIO_PAYLOAD_SIZE / 2)
    size_t bytes_read;
    int16_t stereo_buf[FRAME_COUNT * 2]; // I2S stereo buffer
    audio_packet_t packet;

    while (1) {
        if (i2s_channel_read(rx_chan, stereo_buf, sizeof(stereo_buf), &bytes_read, portMAX_DELAY) == ESP_OK) {
            int frames = bytes_read / 4; // 2 bytes per sample, 2 channels = 4 bytes per frame
            for (int i = 0; i < frames; i++) {
                // Extract only the left channel
                packet.audio_data[i] = stereo_buf[i * 2];
            }
            packet.buf_delay = reg_buf_delay;

            esp_now_send(peer_mac, (uint8_t *)&packet, 1 + frames * 2);
        }
    }
}

void app_main(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Initialize INT Pin
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_DISABLE,
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = (1ULL << INT_PIN),
        .pull_down_en = 0,
        .pull_up_en = 0,
    };
    gpio_config(&io_conf);
    gpio_set_level(INT_PIN, 0);

    // Initialize I2C Slave
    i2c_config_t conf = {
        .mode = I2C_MODE_SLAVE,
        .sda_io_num = I2C_SLAVE_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_SLAVE_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .slave.addr_10bit_en = 0,
        .slave.slave_addr = I2C_SLAVE_ADDRESS,
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_SLAVE_NUM, &conf));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_SLAVE_NUM, conf.mode, I2C_SLAVE_RX_BUF_LEN, I2C_SLAVE_TX_BUF_LEN, 0));

    xTaskCreate(i2c_slave_task, "i2c_slave_task", 4096, NULL, 5, NULL);

    // Initialize WiFi and ESP-NOW
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    wifi_init_config_t wifi_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&wifi_cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE));

    ESP_ERROR_CHECK(esp_now_init());
    ESP_ERROR_CHECK(esp_now_register_send_cb(esp_now_send_cb));
    ESP_ERROR_CHECK(esp_now_register_recv_cb(esp_now_recv_cb));

    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, peer_mac, ESP_NOW_ETH_ALEN);
    peerInfo.channel = 1;
    peerInfo.ifidx = WIFI_IF_STA;
    peerInfo.encrypt = false;
    ESP_ERROR_CHECK(esp_now_add_peer(&peerInfo));

    // Initialize I2S in Slave RX Mode
    i2s_chan_config_t rx_chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_SLAVE);
    ESP_ERROR_CHECK(i2s_new_channel(&rx_chan_cfg, NULL, &rx_chan));

    i2s_std_config_t rx_std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_BCLK_PIN,
            .ws   = I2S_LRCK_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din  = I2S_DIN_PIN,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv   = false,
            },
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_chan, &rx_std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(rx_chan));

    // Start Audio Processing Task
    xTaskCreate(audio_task, "audio_task", 4096, NULL, 5, NULL);
}
