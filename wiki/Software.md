# Software und Steuerung

## Insane Control Center
Das "Insane Control Center" ist eine Python-Anwendung zur Steuerung und Diagnose der Soundbar.
* **Bibliotheken:** Nutzt `customtkinter` für die GUI sowie `zeroconf`, `esptool`, `requests` und `Pillow`.
* **API-Verbindung:** Verbindet sich mit der ESPHome REST API des Masters (Port 80).
* **Hinweis für Entwickler:** Beim Ansprechen von ESPHome-Entitäten per API müssen die Namen genau der YAML-Definition entsprechen und URL-codiert werden (`urllib.parse.quote()`). Bei Headless-Testing unter Linux (CI/CD) muss `customtkinter` via `xvfb-run -a` ausgeführt werden.
* **Android APK:** Die mobile Version wird mit `flet` erstellt. Der Build erfolgt mit `flet build apk` aus dem `Insane Control Center/Android` Verzeichnis.

## OTA Flashing (UART-to-TCP)
Das Master-Modul implementiert einen UART-to-TCP "Flash Hub" via `stream_server` Komponente. Die Ports sind:
* Port `8081`: DSP Modul
* Port `8082`: SUB-TX Modul
* Port `8083`: BT-RX Modul

### Spezielles DSP Flashing
Der RP2354/RP2350 DSP unterstützt natives Bootloader-UART (1 Megabaud). Der Flasher muss:
1. Eine Knock-Sequenz senden (`0x56, 0xff, 0x8b, 0xe4`).
2. Das Raw `.bin` File in strikten 32-Byte-Blöcken (mit `w`-Kommando) übertragen.
3. Den Vorgang mit einem Execute-Befehl (`x`) abschließen.

## Home Assistant & ESPHome
Für eine reibungslose Bedienung in der Home Assistant GUI müssen Template Number Komponenten (z.B. für EQ oder Volume) mit `optimistic: true` konfiguriert sein, um das optische Zurückschnappen (Visual Snap-Back) von Slidern zu vermeiden.
