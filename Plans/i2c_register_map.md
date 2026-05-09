# Insane Sound Bar - I2C Register Map (Master Reference)

Diese Dokumentation dient als verbindliche Referenz für die I2C-Kommunikation der Soundbar. 

## 1. Hardware-Konfiguration & Adressen

| Gerät | Chip | Rolle | I2C-Adresse | SDA | SCL | INT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Main Control** | ESP32-S3 | **Master** | - | GPIO 8 | GPIO 9 | - |
| **Audio DSP** | RP2354 | Slave | `0x20` | GPIO 4 | GPIO 5 | GPIO 2 |
| **Bluetooth** | ESP32-WROOM-32UE | Slave | `0x21` | GPIO 21 | GPIO 22 | GPIO 23 |
| **Sub-Link** | ESP32-WROOM-32U | Slave | `0x22` | GPIO 21 | GPIO 22 | GPIO 23 |
| **Display** | 1.3" OLED | Slave | `0x3C` | GPIO 8 | GPIO 9 | - |

---

## 2. Register-Details: RP2354 (Audio DSP) @ `0x20`
*Verantwortlich für Audio-Routing, EQ und Frequenzweichen.*

| Reg | Name | R/W | Einheit / Skala | Funktion |
| :--- | :--- | :--- | :--- | :--- |
| `0x01` | `VOL_MASTER` | W | 0 - 100 | Hauptlautstärke in % |
| `0x02` | `MUTE_CTRL` | W | 0 / 1 | 1 = Systemweit stummschalten (TPA & DAC) |
| `0x03` | `INPUT_SEL` | W | 0 - 3 | 0:Toslink, 1:Aux, 2:BT, 3:WLAN |
| `0x10` | `EQ_B1` | W | 0 - 20 | Bass (10 = 0dB) |
| `0x11` | `EQ_B2` | W | 0 - 20 | Tief-Mitten (10 = 0dB) |
| `0x12` | `EQ_B3` | W | 0 - 20 | Mitten (10 = 0dB) |
| `0x13` | `EQ_B4` | W | 0 - 20 | Hoch-Mitten (10 = 0dB) |
| `0x14` | `EQ_B5` | W | 0 - 20 | Höhen (10 = 0dB) |
| `0x20` | `TRIM_SUB` | W | 0 - 20 | Subwoofer-Pegel (unabhängig von Master) |
| `0x21` | `TRIM_MID` | W | 0 - 20 | Mitteltöner-Pegel (unabhängig von Master) |
| `0x22` | `TRIM_HIGH` | W | 0 - 20 | Hochtöner-Pegel (unabhängig von Master) |
| `0x30` | `XOVER_SUB_LP`| W | Hz (direkt) | Subwoofer Tiefpass (50-255 Hz) |
| `0x31` | `XOVER_SAT_HP`| W | Hz (direkt) | Satelliten Hochpass (50-255 Hz) |
| `0x32` | `XOVER_MID_LP`| W | Wert * 100Hz | Mitten Tiefpass (z.B. 35 = 3500 Hz) |
| `0x33` | `XOVER_HIGH_HP`| W | Wert * 100Hz | Hochton Hochpass (z.B. 35 = 3500 Hz) |
| `0xFF` | `SYS_STATUS` | R | Code | 0=OK; >0 Fehlercode (z.B. TPA Temp) |

---

## 3. Register-Details: ESP32-WROOM-32UE (Bluetooth) @ `0x21`
*Schnittstelle für Smartphone-Steuerung.*

| Reg | Name | R/W | Werte | Funktion |
| :--- | :--- | :--- | :--- | :--- |
| `0x01` | `BT_STATE` | R | 0 - 3 | 0:Aus, 1:Suche, 2:Verbunden, 3:Play |
| `0x02` | `BT_RSSI` | R | 0 - 255 | Empfangsstärke |
| `0x03` | `SYNC_VOL` | R | 0 - 100 | Aktuelle Lautstärke am Smartphone |
| `0x0A` | `MEDIA_CMD` | W | 1 / 2 / 3 | 1:Play/Pause, 2:Next, 3:Prev |
| `0x10` | `DEV_NAME` | R | String | Name des Handys (max 32 Bytes) |

---

## 4. Register-Details: ESP32-WROOM-32U (Sub-Link) @ `0x22`
*Transmitter für den kabellosen Subwoofer.*

| Reg | Name | R/W | Werte | Funktion |
| :--- | :--- | :--- | :--- | :--- |
| `0x01` | `SUB_STATE` | R | 0 / 1 | 0: Getrennt, 1: Verbunden |
| `0x02` | `SUB_RSSI` | R | 0 - 255 | Signalstärke zum Subwoofer |
| `0x03` | `BUF_DELAY` | W/R | 0 - 255 | Audio-Delay in ms zum Latenzausgleich |
| `0x04` | `PAIR_CMD` | W/R | 0 / 1 | 1 = Starte Pairing-Modus (Subwoofer-Suche) für max. 60s. Fällt automatisch auf 0 zurück. |