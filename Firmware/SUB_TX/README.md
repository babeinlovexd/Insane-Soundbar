# Insane Sound Bar - SUB-TX (Subwoofer Sender)

Dieses Modul ist die Firmware für den ESP32-WROOM-32UE-N4 auf dem Mainboard der Insane Sound Bar. Es fungiert als Sender für das kabellose Subwoofer-Signal.

## Systemübersicht

* **MCU:** ESP32-WROOM-32UE-N4
* **Audio-Eingang:** I2S Slave RX (Taktgeber ist der RP2354 DSP)
* **Audio-Ausgang:** ESP-NOW (zum SUB-RX Modul)
* **Steuerung:** I2C Slave (0x22) vom ESP32-S3 Master + INT-Pin
* **Audio-Spezifikationen:** 16.000 Hz (16 kHz), 16-Bit Mono (nur der linke Kanal wird gefunkt, um Bandbreite zu sparen)

## I2C-Register (Adresse 0x22)

Das Modul verarbeitet folgende Register im Hintergrund für den ESP32-S3:

* `0x01` (**SUB_STATE** - Read Only): 0 = Subwoofer getrennt, 1 = Subwoofer verbunden.
* `0x02` (**SUB_RSSI** - Read Only): 0-255 (Aktuelle Signalstärke der ESP-NOW Verbindung).
* `0x03` (**BUF_DELAY** - Read/Write): 0-255 ms. (Latenzausgleich, wird via ESP-NOW Metadaten an den Subwoofer gesendet).
* `0x04` (**PAIR_CMD** - Read/Write): 0 = Normal, 1 = Pairing-Modus aktivieren (wartet max. 60s auf Broadcast vom Subwoofer).
* `0xF0` (**FW_VERSION_MAJOR** - Read Only): Major Version der Firmware.
* `0xF1` (**FW_VERSION_MINOR** - Read Only): Minor Version der Firmware.
* `0xF2` (**FW_VERSION_PATCH** - Read Only): Patch Version der Firmware.

## Funktionsweise

1. **Audio-Empfang:** Das I2S-Interface empfängt ein gefiltertes Subwoofer-Signal vom RP2354 DSP. Es nutzt nur den linken Kanal der Stereo-Daten.
2. **Datenübertragung:** Die Audio-Pakete werden zusammen mit dem `BUF_DELAY` Wert über ESP-NOW gesendet.
3. **Verbindungsüberwachung:** Das Modul trackt eingehende ESP-NOW ACKs. Bleiben diese mehrfach aus, wird der Status auf *Getrennt* (0) gesetzt und der Interrupt-Pin (GPIO 23) wird kurz auf HIGH gezogen, um den Master-Controller (ESP32-S3) zu benachrichtigen.

## Pin-Belegung (Auszug)

| Funktion | Pin (ESP32) | Verbunden mit |
| :--- | :--- | :--- |
| I2S_BCLK | GPIO 25 | RP2354 (GPIO 20) |
| I2S_LRCK | GPIO 26 | RP2354 (GPIO 21) |
| I2S_DIN | GPIO 27 | RP2354 (GPIO 22) |
| I2C_SDA | GPIO 21 | I2C Bus |
| I2C_SCL | GPIO 22 | I2C Bus |
| INT_OUT | GPIO 23 | ESP32-S3 (GPIO 18) |