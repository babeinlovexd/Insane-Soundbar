#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <driver/i2s.h>
#include <freertos/FreeRTOS.h>
#include <freertos/ringbuf.h>

// --- PIN DEFINITIONS ---
#define PIN_LED           4
#define PIN_I2S_BCLK      14
#define PIN_I2S_LRCK      26
#define PIN_I2S_DOUT      27
#define PIN_MUTE_CTRL     32
#define PIN_XSMT_SDZ_CTRL 33
#define PIN_FAULT_IN      34

// --- AUDIO CONFIGURATION ---
#define SAMPLE_RATE       16000
#define I2S_PORT          I2S_NUM_0
#define JITTER_BUFFER_MS  50
#define BYTES_PER_SEC     (SAMPLE_RATE * 2) // 16-bit Mono = 2 bytes per sample
#define BUFFER_SIZE_BYTES (BYTES_PER_SEC * JITTER_BUFFER_MS / 1000 * 4) // 4x factor for headroom
#define BUFFER_FILL_THRESHOLD (BYTES_PER_SEC * JITTER_BUFFER_MS / 1000)

// --- SYSTEM STATE ---
RingbufHandle_t audio_buffer;
volatile uint32_t last_packet_time = 0;
bool is_muted = true;
bool stream_active = false;
bool is_buffering = true;
unsigned long last_led_blink = 0;
bool led_state = false;

// --- ESP-NOW CALLBACK ---
void onDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
    if (data_len > 0) {
        last_packet_time = millis();
        // Send data to ring buffer. Wait max 0 ticks to not block ESP-NOW task
        xRingbufferSend(audio_buffer, (void *)data, data_len, 0);
    }
}

// --- INITIALIZATION ---
void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = true
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = PIN_I2S_BCLK,
        .ws_io_num = PIN_I2S_LRCK,
        .data_out_num = PIN_I2S_DOUT,
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
    i2s_zero_dma_buffer(I2S_PORT);
}

void setup() {
    // 1. Hardware Initialization (Mute ASAP to prevent pop)
    pinMode(PIN_MUTE_CTRL, OUTPUT);
    digitalWrite(PIN_MUTE_CTRL, LOW); // Mute immediately

    pinMode(PIN_XSMT_SDZ_CTRL, OUTPUT);
    digitalWrite(PIN_XSMT_SDZ_CTRL, LOW); // Shutdown TPA & DAC

    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);

    pinMode(PIN_FAULT_IN, INPUT_PULLUP);

    // 2. Initialize RingBuffer (byte buffer)
    audio_buffer = xRingbufferCreate(BUFFER_SIZE_BYTES, RINGBUF_TYPE_BYTEBUF);

    // 3. Setup I2S (Clock starts here)
    setupI2S();

    // Give DAC/TPA some time with stable clock before enabling them out of shutdown
    delay(50);
    // Bring them out of shutdown, but keep mute active via MUTE_CTRL
    digitalWrite(PIN_XSMT_SDZ_CTRL, HIGH);

    // 4. Setup ESP-NOW
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();

    if (esp_now_init() != ESP_OK) {
        // ESP-NOW init failed
        return;
    }

    esp_now_register_recv_cb(onDataRecv);
}

void loop() {
    uint32_t now = millis();

    // -- 1. Stream Status Logic --
    // Check if stream is alive (>100ms means stream interrupted)
    if (now - last_packet_time > 100) {
        stream_active = false;
    } else {
        stream_active = true;
    }

    // -- 2. Mute & Buffer Status Logic --
    size_t bytes_waiting = xRingbufferGetCurFreeSize(audio_buffer);
    size_t bytes_filled = BUFFER_SIZE_BYTES - bytes_waiting;

    if (!stream_active) {
        // Stream interrupted
        if (!is_muted) {
            is_muted = true;
            digitalWrite(PIN_MUTE_CTRL, LOW); // Mute
        }
        // Force back into buffering state so we accumulate data when stream restarts
        is_buffering = true;

        // Optionally drain the buffer entirely when stream is lost
        size_t size;
        void *drain = xRingbufferReceive(audio_buffer, &size, 0);
        while(drain != NULL) {
            vRingbufferReturnItem(audio_buffer, drain);
            drain = xRingbufferReceive(audio_buffer, &size, 0);
        }
    } else {
        // Stream is active
        if (is_buffering) {
            if (bytes_filled >= BUFFER_FILL_THRESHOLD) {
                is_buffering = false; // Buffer filled enough, start playing
                if (is_muted) {
                    is_muted = false;
                    digitalWrite(PIN_MUTE_CTRL, HIGH); // Unmute
                }
            }
        }
    }

    // -- 3. Jitter Buffer & I2S Feeder --
    if (!is_buffering) {
        size_t item_size;
        // Try to receive from ringbuffer without blocking
        uint8_t *item = (uint8_t *)xRingbufferReceiveUpTo(audio_buffer, &item_size, 0, 512);

        if (item != NULL) {
            // We have mono data, we need to convert it to stereo.
            // item points to an array of 16-bit samples (little endian usually)
            // 1 sample = 2 bytes.
            int num_samples = item_size / 2;
            int16_t *mono_samples = (int16_t *)item;

            // Max item_size is 512 bytes (256 samples).
            // We need up to 256 stereo samples (512 int16_t elements).
            int16_t stereo_samples[512];

            for (int i = 0; i < num_samples && i < 256; i++) {
                stereo_samples[i * 2] = mono_samples[i];     // Left channel
                stereo_samples[i * 2 + 1] = mono_samples[i]; // Right channel
            }

            size_t stereo_bytes = num_samples * 4; // 2 channels * 2 bytes
            size_t bytes_written;
            // Write to I2S (this will block if DMA is full, effectively pacing our loop to the sample rate)
            i2s_write(I2S_PORT, stereo_samples, stereo_bytes, &bytes_written, portMAX_DELAY);

            // Return item to ring buffer
            vRingbufferReturnItem(audio_buffer, (void *)item);
        } else {
            // Buffer is empty (underrun!). Write zeros to keep I2S clock stable.
            // In a strict implementation, we might fall back to is_buffering = true here,
            // but for now, tx_desc_auto_clear = true will handle sending zeros.
            // We'll write small blocks of zeros to pace the loop.
            int16_t zeros[128] = {0};
            size_t bytes_written;
            i2s_write(I2S_PORT, zeros, sizeof(zeros), &bytes_written, portMAX_DELAY);
        }
    } else {
        // We are pre-buffering. Feed zeros to I2S to keep the clock active.
        int16_t zeros[128] = {0};
        size_t bytes_written;
        i2s_write(I2S_PORT, zeros, sizeof(zeros), &bytes_written, portMAX_DELAY);
    }

    // -- 4. LED Status Logic --

    // -- 3. LED Status Logic --
    if (stream_active && !is_muted) {
        // Solid light
        digitalWrite(PIN_LED, HIGH);
    } else {
        // Blinking
        if (now - last_led_blink >= 500) {
            led_state = !led_state;
            digitalWrite(PIN_LED, led_state ? HIGH : LOW);
            last_led_blink = now;
        }
    }
}
