# I2C Kommunikation und APIs

Der ESP32-S3 Master ist die zentrale Instanz des Systems und steuert alle Module über I2C.

## I2C Master Register (MAIN-CTRL)
* SDA: GPIO 8, SCL: GPIO 9.
* Um I2C-FIFO-Pufferüberläufe auf den Arduino-basierten ESP32 Slaves zu vermeiden, werden Slave-Antworten in einem lokalen Puffer konstruiert und in einem einzelnen Block (`Wire.write(buf, len)`) gesendet.
* Der Master fragt zyklisch die Versionen (`0xF0`-`0xF2`) der Slaves ab und agiert als **Version Broker**, um die Daten über einen Webserver auf Port 80 (ESPHome) als JSON bereitzustellen.
* IR Codes (NEC/RC5) für Fernbedienungen (inklusive Play/Pause/Prev/Next) werden auf dem Master gelernt und persistent im NVS gespeichert.

## I2C Register Map Übersicht
Die volle Übersicht der Register befindet sich in den Plänen, hier die wichtigsten Adressen:

### RP2354 DSP (`0x20`)
* `0x05`: Interne Chiptemperatur.
* `0x06`: Night Mode (DRC Kompression ein/aus).
* `0x07`: Clear Voice (Sprach-EQ Biquad-Presets ein/aus).
* `0x20`, `0x21`, `0x22`: Kanal-Trims für Sub, Mid und High (Wertebereich 0-20, wobei 10 = 0dB).

### Bluetooth Receiver (`0x21`)
Schnittstelle für Smartphones. Unterstützt zwingend das AAC-Codec-Profil.

### Subwoofer Transmitter (`0x22`)
* `0x01`: SUB_STATE (Verbunden/Getrennt).
* `0x02`: SUB_RSSI.
* `0x03`: BUF_DELAY (Latenzausgleich).
* `0x04`: PAIR_CMD (Startet das Pairing).
