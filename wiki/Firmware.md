# Firmware und Build-Systeme

Die Software des Systems ist aufgeteilt auf mehrere Plattformen:

## ESPHome Master (MAIN-CTRL)
Das ESP32-S3 Master-Modul nutzt ESPHome auf Basis des ESP-IDF Frameworks.
* **Kompilieren:** Lokal mittels ESPHome CLI (z.B. `esphome compile Firmware/Master/insane_soundbar.yaml`).
* **Custom Components:** Der alte `custom_component` YAML-Block ist veraltet. Eigene C++ Komponenten (wie `isb_orchestrator` und `stream_server`) werden über Lambdas im `on_boot` (z.B. `priority: 800`) instanziiert.
* **Externe Komponenten:** Sie werden direkt via `type: git` (Remote Repository `babeinlovexd/Insane-Soundbar`) bezogen (mit `refresh: 0s`).

## RP2354 DSP
Die DSP-Firmware ist in C/C++ geschrieben und nutzt das **Raspberry Pi Pico SDK** via CMake.
* Master Volume ist logarithmisch implementiert (0-100 entspricht -50dB bis 0dB).
* Kanal-Trims (Sub, Mid, High) haben eine 0-20 Skala, bei der 10 = 0dB entspricht (1 Step = 1dB).
* DSP Downsampling für den Subwoofer-Kanal: Die 44.1 kHz der Quelle werden für den Subwoofer auf 11025 Hz (16-bit) heruntergesampelt, indem performant ein Modulo-Counter (`& 3`) zur Nutzung jedes vierten Cycles ohne FPU-Last angewendet wird.

## PlatformIO (Bluetooth, SUB-TX, SUB-RX)
Module auf Basis der WROOM-32 Chipsätze nutzen PlatformIO.
* **Kompilieren:** Per `pio run` im jeweiligen Unterverzeichnis.
* **Bluetooth (BT-RX):** Erfordert zwingend das manuelle Klonen der Libraries `ESP32-A2DP` und `arduino-audio-tools` in den `/lib` Ordner. Das Modul benötigt aufgrund von OTA und A2DP-Größe eine spezielle Partition Table (`min_spiffs.csv`).
* **SUB-TX:** Nutzt das ESP-IDF Framework. `esp_timer` muss in der `CMakeLists.txt` der Komponente unter `REQUIRES` gelistet sein.

## CI/CD und GitHub Actions
Automatisierte Builds erfolgen über GitHub Actions.
