# Hardware-Spezifikationen

## Mikrocontroller
* **Master (MAIN-CTRL):** ESP32-S3-N16R8 (16MB Flash, 8MB PSRAM)
* **Audio DSP:** RP2354A. Nutzt eine strikte Dual-Core-Architektur:
  * **Core 0:** Gewidmet der I2C-Kommunikation (Slave Adresse `0x20`) und dem Audio-Routing.
  * **Core 1:** Verarbeitet ausschließlich die DSP-Mathematik und Biquad-Filter.
* **Bluetooth (BT-RX):** ESP32-WROOM-32UE-N4.
* **Subwoofer TX/RX:** ESP32-WROOM-32U / ESP32-WROOM-32UE.

## Audio ICs und Verstärker
Das System setzt auf **PCM5102A** DACs für die D/A-Wandlung der I2S-Signale und **PCM1808** für den analogen AUX-Eingang.

Zur Verstärkung kommen Class-D Verstärkerchips zum Einsatz:
* **Soundbar (Mitten/Höhen):** TPA3118D2.
* **Subwoofer:** TPA3116D2.

### Hardware-Steuerungslogik & Anti-Pop
Um Audio-Pops ("Knacksen") beim Einschalten zu vermeiden, muss das System eine genaue Einschaltsequenz (Anti-Pop Unmute) für die Hardware-Pins beachten, da die Steuerungslogik gemischte Polaritäten aufweist:
* **MUTE (TPA311x):** Active-High (High = Mute, Low = Play)
* **SDZ (Shutdown TPA311x):** Active-Low
* **XSMT (Mute PCM5102A DAC):** Active-Low
* **FAULTZ (Fehlerstatus TPA311x):** Active-Low

**Anti-Pop Sequenz:**
1. `SDZ` und `XSMT` auf `HIGH` ziehen, um den Verstärker und DAC aus dem Standby/Shutdown zu holen.
2. ~50ms warten zur Stabilisierung.
3. `MUTE`-Pin auf `LOW` ziehen, um die Audioausgabe freizuschalten.

## Lautsprecher & Chassis
* **Mitteltöner:** Dayton CE70PR-4
* **Hochtöner:** Dayton ND25FA-4
* **Subwoofer:** Dayton DCS205-4 mit Passive Radiator (Dayton DSA215-PR)
