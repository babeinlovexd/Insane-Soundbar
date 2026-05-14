#include <Arduino.h>
#include <Wire.h>
#include "BluetoothA2DPSink.h"
#include "nvs_flash.h"
#include "esp_bt.h"

#define I2C_SLAVE_ADDR 0x21
#define I2C_SDA_PIN 16
#define I2C_SCL_PIN 17
#define INT_PIN 23

#define I2S_BCK_PIN 19
#define I2S_WS_PIN 18
#define I2S_DATA_PIN 21

// I2C Registers
volatile uint8_t reg_bt_state = 1;
volatile uint8_t reg_bt_rssi = 0;
volatile uint8_t reg_sync_vol = 50;
volatile uint8_t reg_media_cmd = 0;
char reg_dev_name[33] = "";
volatile uint8_t current_reg = 0x00;

unsigned long last_audio_time = 0;
volatile bool is_connected = false;
volatile bool is_playing = false;

// INT Pin Management
volatile bool int_pending = false;
unsigned long int_start_time = 0;

// Subclass to enforce AAC Codec Support
class AACSink : public BluetoothA2DPSink {
public:
    virtual esp_a2d_mct_t get_audio_type() override {
        return ESP_A2D_MCT_M24; // Enforce AAC
    }
};

AACSink a2dp_sink;

// Function declarations
void trigger_int();
void receiveEvent(int howMany);
void requestEvent();

void trigger_int() {
    int_pending = true;
    int_start_time = millis();
    digitalWrite(INT_PIN, HIGH);
}

void connection_state_cb(esp_a2d_connection_state_t state, void *ptr) {
    if (state == ESP_A2D_CONNECTION_STATE_CONNECTED) {
        is_connected = true;
        reg_bt_state = 2; // Connected
        // Reset the audio timer when a connection occurs so it doesn't immediately disconnect
        last_audio_time = millis();

        // Get device name
        const char * peer_name = a2dp_sink.get_peer_name();
        if (peer_name != nullptr) {
             strncpy(reg_dev_name, peer_name, sizeof(reg_dev_name) - 1);
        }
    } else if (state == ESP_A2D_CONNECTION_STATE_DISCONNECTED) {
        is_connected = false;
        reg_bt_state = 1; // Disconnected, Visible/Search
        reg_dev_name[0] = '\0';
        last_audio_time = millis(); // Reset just in case
    }
    trigger_int();
}

void audio_state_cb(esp_a2d_audio_state_t state, void *ptr) {
    if (state == ESP_A2D_AUDIO_STATE_STARTED) {
        is_playing = true;
        reg_bt_state = 3; // Playing
    } else if (state == ESP_A2D_AUDIO_STATE_REMOTE_SUSPEND || state == ESP_A2D_AUDIO_STATE_STOPPED) {
        is_playing = false;
        reg_bt_state = 2; // Connected
        last_audio_time = millis(); // Reset when audio stops
    }
    trigger_int();
}

void volume_change_cb(int volume) {
    // volume is 0-127, map to 0-100
    reg_sync_vol = (uint8_t)((volume * 100) / 127);
    trigger_int();
}

void setup() {
    Serial.begin(115200);

    // Initialize NVS
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    pinMode(INT_PIN, OUTPUT);
    digitalWrite(INT_PIN, LOW);

    // I2C Slave Setup
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);
    Wire.begin((uint8_t)I2C_SLAVE_ADDR, I2C_SDA_PIN, I2C_SCL_PIN, 100000);

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_DATA_PIN,
        .data_in_num = I2S_PIN_NO_CHANGE
    };
    a2dp_sink.set_pin_config(pin_config);

    a2dp_sink.set_on_connection_state_changed(connection_state_cb);
    a2dp_sink.set_on_audio_state_changed(audio_state_cb);
    a2dp_sink.set_on_volumechange(volume_change_cb);

    a2dp_sink.start("ISB_Bluetooth");

    // Auto reconnect to previously connected devices
    a2dp_sink.set_auto_reconnect(true);
}

void loop() {
    // Auto-Disconnect logic: 5 minutes = 300000 ms
    if (is_connected && !is_playing) {
        if (millis() - last_audio_time > 300000) {
            a2dp_sink.disconnect();
            last_audio_time = millis(); // Reset
        }
    } else if (is_playing || !is_connected) {
        last_audio_time = millis(); // Constantly reset when playing or disconnected
    }

    // Handle INT Pin pulse (5 ms non-blocking)
    if (int_pending && (millis() - int_start_time >= 5)) {
        digitalWrite(INT_PIN, LOW);
        int_pending = false;
    }

    // Read RSSI
    if (is_connected) {
        reg_bt_rssi = 200; // Dummy value for now
    } else {
        reg_bt_rssi = 0;
    }

    delay(1); // Reduce delay to 1ms to make the 5ms INT pulse more accurate
}

void receiveEvent(int howMany) {
    if (howMany > 0) {
        current_reg = Wire.read();
        if (howMany > 1) {
            uint8_t val = Wire.read();
            if (current_reg == 0x0A) { // MEDIA_CMD
                if (val == 1) {
                    if (is_playing) a2dp_sink.pause();
                    else a2dp_sink.play();
                } else if (val == 2) {
                    a2dp_sink.next();
                } else if (val == 3) {
                    a2dp_sink.previous();
                }
            }
        }
    }
}

void requestEvent() {
    // If a request comes in, we reply starting from current_reg.
    // If it's the DEV_NAME (0x10 to 0x2F), we send the rest of the string block.

    if (current_reg >= 0x10 && current_reg <= 0x2F) {
        uint8_t index = current_reg - 0x10;
        int len = strlen(reg_dev_name);

        // Write the remaining part of the string starting from 'index'
        // Wire.write can take an array and length
        if (index < len) {
            Wire.write((const uint8_t*)(reg_dev_name + index), len - index);
        }

        // Fill the rest with 0
        for (int i = len; i <= (0x2F - 0x10); i++) {
            if (i >= index) {
                Wire.write(0);
            }
        }
    } else {
        switch (current_reg) {
            case 0x01: // BT_STATE
                Wire.write(reg_bt_state);
                break;
            case 0x02: // BT_RSSI
                Wire.write(reg_bt_rssi);
                break;
            case 0x03: // SYNC_VOL
                Wire.write(reg_sync_vol);
                break;
            case 0xF0: // Major Version
                Wire.write(1);
                break;
            case 0xF1: // Minor Version
                Wire.write(0);
                break;
            case 0xF2: // Patch Version
                Wire.write(0);
                break;
            default:
                Wire.write(0);
                break;
        }
    }
}
