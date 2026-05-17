# System Architektur

Die **Insane Soundbar** ist ein Multi-Modul-System mit einer klaren Trennung zwischen Steuerung, Signalverarbeitung und Verstärkung.

## Übersicht der Kernkomponenten

1. **MAIN-CTRL (Master):** Ein ESP32-S3-N16R8 (16MB Flash, 8MB Octal PSRAM), der als zentraler Steuerungsknoten fungiert. Er kommuniziert mit Home Assistant via ESPHome, verwaltet die I2C-Kommunikation als Master und ist das Gateway für OTA-Updates (Flash-Hub).
2. **Audio DSP:** Ein RP2354 (Dual-Core), der die gesamte digitale Signalverarbeitung (Frequenzweichen, Biquad-EQs) übernimmt und als primärer Taktgeber (Clock Master) für das I2S-Audiosystem agiert (außer für Bluetooth).
3. **Bluetooth Receiver (BT-RX):** Ein ESP32-WROOM-32UE, der Smartphone-Signale empfängt und per I2S an den DSP übergibt.
4. **Subwoofer Link (SUB-TX & SUB-RX):** Zwei ESP32-Module, die für die verzögerungsarme Übertragung des Subwoofer-Audiosignals via ESP-NOW zuständig sind.

## Takt-Domänen (I2S)

Obwohl der RP2354 DSP als primärer I2S Master Clock für die DA-Wandler agiert, übernimmt das **BT-RX Modul die Rolle des I2S Master TX** für seine direkte Verbindung zum DSP, um einen sauberen Stream für eingehendes Bluetooth-Audio (mit AAC-Codec) zu garantieren.
