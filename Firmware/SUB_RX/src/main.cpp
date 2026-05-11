#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <driver/i2s.h>
#include <freertos/FreeRTOS.h>
#include <freertos/ringbuf.h>
#include <Preferences.h>
#include <WebServer.h>

#define FW_VERSION "1.0.0"

// --- PIN DEFINITIONS ---
#define PIN_LED           4
#define PIN_I2S_BCLK      14
#define PIN_I2S_LRCK      26
#define PIN_I2S_DOUT      27
#define PIN_MUTE_CTRL     32
#define PIN_XSMT_SDZ_CTRL 33
#define PIN_FAULT_IN      34

// --- AUDIO CONFIGURATION ---
#define SAMPLE_RATE       11025
#define I2S_PORT          I2S_NUM_0
#define JITTER_BUFFER_MS  50
#define BYTES_PER_SEC     (SAMPLE_RATE * 2) // 16-bit Mono = 2 bytes per sample
#define BUFFER_SIZE_BYTES (BYTES_PER_SEC * JITTER_BUFFER_MS / 1000 * 4) // 4x factor for headroom

// --- SYSTEM STATE ---
RingbufHandle_t audio_buffer;
volatile uint32_t last_packet_time = 0;
bool is_muted = true;
bool stream_active = false;
bool is_buffering = true;
unsigned long last_led_blink = 0;
bool led_state = false;
size_t dynamic_fill_threshold = (BYTES_PER_SEC * JITTER_BUFFER_MS / 1000);

// --- PAIRING & SETUP STATE ---
enum SystemState {
    STATE_SETUP_AP,
    STATE_PAIRING,
    STATE_AUDIO_RX
};
SystemState current_state = STATE_AUDIO_RX;

// --- PROTOCOL STRUCTURES ---
typedef struct {
    uint8_t type; // 1 = Request, 2 = ACK
} __attribute__((packed)) pairing_packet_t;

typedef struct {
    uint8_t buf_delay;
    int16_t audio_data[120];
} __attribute__((packed)) audio_packet_t;

Preferences preferences;
WebServer server(80);
uint8_t master_mac[6] = {0};
bool has_master_mac = false;
unsigned long pairing_start_time = 0;

// --- HTML FOR CAPTIVE PORTAL ---
const char* setup_html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #222; color: #fff; }
    button { padding: 20px 40px; font-size: 24px; background-color: #007BFF; color: white; border: none; border-radius: 10px; cursor: pointer; }
    button:active { background-color: #0056b3; }
  </style>
</head>
<body>
  <h2>Insane Sound Bar - Subwoofer Setup</h2>
  <form action="/pair" method="POST">
    <button type="submit">Mit Soundbar koppeln</button>
  </form>
</body>
</html>
)rawliteral";

// --- WEBSERVER HANDLERS ---
void handleRoot() {
    server.send(200, "text/html", setup_html);
}

void handlePair() {
    server.send(200, "text/html", "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{background:#222;color:#fff;text-align:center;font-family:sans-serif;margin-top:50px;}</style></head><body><h2>Pairing gestartet!</h2><p>Bitte warten...</p></body></html>");
    // State change is handled in main loop by setting flag or changing state directly
    current_state = STATE_PAIRING;
    pairing_start_time = millis();
}

// --- ESP-NOW CALLBACK ---
#if defined(ESP_IDF_VERSION) && ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
void onDataRecv(const esp_now_recv_info_t *esp_now_info, const uint8_t *data, int data_len) {
    const uint8_t *mac_addr = esp_now_info->src_addr;
#else
void onDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
#endif
    if (current_state == STATE_AUDIO_RX) {
        if (data_len > 1 && data_len <= sizeof(audio_packet_t)) { // Header (1 byte buf_delay) + Audio Data
            last_packet_time = millis();
            audio_packet_t *packet = (audio_packet_t *)data;

            // Update dynamic threshold based on header (buf_delay is in ms)
            if (packet->buf_delay > 0) {
                dynamic_fill_threshold = (BYTES_PER_SEC * packet->buf_delay) / 1000;
            }

            // Send raw audio data to ring buffer. Wait max 0 ticks to not block ESP-NOW task
            int audio_bytes = data_len - 1;
            xRingbufferSend(audio_buffer, (void *)packet->audio_data, audio_bytes, 0);
        }
    } else if (current_state == STATE_PAIRING) {
        // Look for pairing ACK from master
        if (data_len == sizeof(pairing_packet_t)) {
            pairing_packet_t *packet = (pairing_packet_t *)data;
            if (packet->type == 2) {
                memcpy(master_mac, mac_addr, 6);
                has_master_mac = true;
            }
        }
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
    Serial.begin(115200);
    Serial.print("SUB_RX FW_VERSION: ");
    Serial.println(FW_VERSION);

    // 1. Hardware Initialization (Mute ASAP to prevent pop)
    pinMode(PIN_MUTE_CTRL, OUTPUT);
    digitalWrite(PIN_MUTE_CTRL, HIGH); // Mute immediately (Active HIGH for TPA3116D2)

    pinMode(PIN_XSMT_SDZ_CTRL, OUTPUT);
    digitalWrite(PIN_XSMT_SDZ_CTRL, LOW); // Shutdown TPA & DAC (Active LOW)

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

    // 4. Check NVS for existing Master MAC
    preferences.begin("isb", false);
    size_t mac_len = preferences.getBytesLength("master_mac");
    if (mac_len == 6) {
        preferences.getBytes("master_mac", master_mac, 6);
        has_master_mac = true;
        current_state = STATE_AUDIO_RX;
    } else {
        current_state = STATE_SETUP_AP;
    }
    preferences.end();

    // 5. Setup Network & ESP-NOW based on state
    if (current_state == STATE_AUDIO_RX) {
        WiFi.mode(WIFI_STA);
        WiFi.disconnect();

        if (esp_now_init() != ESP_OK) {
            return;
        }

        esp_now_register_recv_cb(onDataRecv);

        // Add master to peer list (to receive correctly, and in case we need to send)
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, master_mac, 6);
        peerInfo.channel = 0; // use current channel
        peerInfo.encrypt = false;
        esp_now_add_peer(&peerInfo);

    } else if (current_state == STATE_SETUP_AP) {
        WiFi.mode(WIFI_AP);
        WiFi.softAP("Insane_Subwoofer");

        IPAddress IP = WiFi.softAPIP();

        server.on("/", HTTP_GET, handleRoot);
        server.on("/pair", HTTP_POST, handlePair);
        server.begin();
    }
}

void loop() {
    // --- TPA RUNTIME FAULT PROTECTION ---
    static unsigned long last_fault_blink = 0;
    static bool fault_led_state = false;
    static bool was_in_fault = false;

    // Fault Pin ist Active-Low (LOW = Überhitzung oder Kurzschluss)
    bool current_fault = (digitalRead(PIN_FAULT_IN) == LOW);

    if (current_fault) {
        // 1. Notabschaltung (nur einmalig triggern)
        if (!was_in_fault) {
            Serial.println("CRITICAL FAULT: Subwoofer TPA Fehler! Endstufe wird abgeschaltet.");

            // TPA und DAC stummschalten / in den Shutdown zwingen
            digitalWrite(PIN_MUTE_CTRL, HIGH); // Mute
            digitalWrite(PIN_XSMT_SDZ_CTRL, LOW); // Shutdown

            was_in_fault = true;
        }

        // 2. LED extrem schnell blinken lassen (50ms Intervall)
        if (millis() - last_fault_blink > 50) {
            fault_led_state = !fault_led_state;
            digitalWrite(PIN_LED, fault_led_state ? HIGH : LOW);
            last_fault_blink = millis();
        }

        // WICHTIG: Early Return, damit der normale ESP-NOW Status-Code in der Loop
        // nicht das Blinken oder die Mute-Pins überschreibt!
        return;
    } else {
        // Fehler ist behoben oder gar nicht erst aufgetreten
        if (was_in_fault) {
            Serial.println("FAULT BEHOBEN: Subwoofer TPA arbeitet wieder normal.");

            // Endstufe wieder aufwecken
            digitalWrite(PIN_XSMT_SDZ_CTRL, HIGH); // Wake up
            delay(50); // Stabilize
            digitalWrite(PIN_MUTE_CTRL, LOW); // Unmute

            was_in_fault = false;
        }
    }

    uint32_t now = millis();

    if (current_state == STATE_SETUP_AP) {
        server.handleClient();

        // Slow pulse for AP mode
        if (now - last_led_blink >= 1000) {
            led_state = !led_state;
            digitalWrite(PIN_LED, led_state ? HIGH : LOW);
            last_led_blink = now;
        }
        return; // Don't run audio logic in setup mode
    }

    if (current_state == STATE_PAIRING) {
        static bool pairing_inited = false;
        static uint32_t last_pair_tx = 0;

        if (!pairing_inited) {
            server.stop();
            WiFi.mode(WIFI_STA);
            WiFi.disconnect();
            if (esp_now_init() == ESP_OK) {
                esp_now_register_recv_cb(onDataRecv);

                // Add broadcast peer
                esp_now_peer_info_t peerInfo = {};
                for (int i=0; i<6; i++) peerInfo.peer_addr[i] = 0xFF;
                peerInfo.channel = 0;
                peerInfo.encrypt = false;
                esp_now_add_peer(&peerInfo);
            }
            pairing_inited = true;
        }

        // Fast blink for pairing
        if (now - last_led_blink >= 100) {
            led_state = !led_state;
            digitalWrite(PIN_LED, led_state ? HIGH : LOW);
            last_led_blink = now;
        }

        // Send Broadcast every 500ms
        if (now - last_pair_tx >= 500) {
            uint8_t broadcast_mac[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
            pairing_packet_t pair_req;
            pair_req.type = 1; // 1 = Request
            esp_now_send(broadcast_mac, (uint8_t*)&pair_req, sizeof(pairing_packet_t));
            last_pair_tx = now;
        }

        if (has_master_mac) {
            // Save to NVS
            preferences.begin("isb", false);
            preferences.putBytes("master_mac", master_mac, 6);
            preferences.end();

            // Add actual master peer
            esp_now_peer_info_t peerInfo = {};
            memcpy(peerInfo.peer_addr, master_mac, 6);
            peerInfo.channel = 0;
            peerInfo.encrypt = false;
            esp_now_add_peer(&peerInfo);

            digitalWrite(PIN_LED, HIGH);
            current_state = STATE_AUDIO_RX;
        } else if (now - pairing_start_time > 60000) {
            // Timeout after 60 seconds, reboot to go back to AP
            ESP.restart();
        }

        return; // Don't run audio logic in pairing mode
    }

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
            digitalWrite(PIN_MUTE_CTRL, HIGH); // Mute (Active HIGH)
            digitalWrite(PIN_XSMT_SDZ_CTRL, LOW); // Shut down DAC/TPA totally to avoid any noise on long drops
        }
        // Force back into buffering state so we accumulate data when stream restarts
        is_buffering = true;

        // ZWINGEND (Mandatory): drain the buffer entirely when stream is lost to prevent old artifacts
        size_t size;
        void *drain = xRingbufferReceive(audio_buffer, &size, 0);
        while(drain != NULL) {
            vRingbufferReturnItem(audio_buffer, drain);
            drain = xRingbufferReceive(audio_buffer, &size, 0);
        }
    } else {
        // Stream is active
        if (is_buffering) {
            if (bytes_filled >= dynamic_fill_threshold) {
                is_buffering = false; // Buffer filled enough, start playing
                if (is_muted) {
                    is_muted = false;
                    digitalWrite(PIN_XSMT_SDZ_CTRL, HIGH); // Enable DAC/TPA
                    delay(50); // Give it a tiny bit of time before unmuting
                    digitalWrite(PIN_MUTE_CTRL, LOW); // Unmute (Active HIGH -> LOW means Play)
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
