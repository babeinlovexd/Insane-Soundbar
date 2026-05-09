# 🔊 Projekt-Spezifikation: Insane 2.1 DSP Soundbar (V2.0)

## 1. System-Konzept
* **Modellname**: Insane Wireless 2.1 Soundbar V2.0
* **Prinzip**: 3-Wege-Aktivsystem (Subwoofer + 2x geschlossene Satelliten)
* **Gehäuse-Volumen**: 
    * Subwoofer: 12 Liter (Netto-Luftvolumen) – Downfiring mit PR
    * Satelliten (L/R): Jeweils 1,14 Liter (Netto) – Geschlossen
* **Ziel-Abstimmung Subwoofer**: 32,22 Hz (fb)

---

## 2. Hardware-Komponenten
| Komponente | Modell | Spezifikationen |
| :--- | :--- | :--- |
| **Aktiv-Treiber (Sub)** | **Dayton Audio MX6-22 Max-X** | Xmax: 12 mm, Re: 4,7 Ohm (Reihenschaltung), Prms: 70 W |
| **Passivmembran** | **Dayton Audio DS215-PR** | Xmax: 11 mm, Sd: 211,2 cm² |
| **Mitteltöner (Sat)** | **2x Dayton Audio ND91-8** | Xmax: 5,1 mm, Fs: 73,1 Hz, Korbmaß: 87,5 mm |
| **Hochtöner (Sat)** | **2x Dayton Audio ND16FA-6** | Durchmesser: 32,5 mm, geschlossene Rückseite |
| **Verstärker** | **TPA3116D2 (z. B. 2.1 Board)** | Versorgung: 24 V DC, Leistung Sub an 4,7 Ohm ≈ 51 W |
| **Controller** | **ESP32-32U** | I2S Audio-Processing, DSP-Weiche & Wireless Sync |

---

## 3. Akustische Parameter & Tuning
* **Tuning-Frequenz Sub (fb)**: 32,22 Hz
* **Zusatzgewicht (PR)**: **80 g** (Added Mass an der DS215-PR)
* **Akustische Trennung (Sub zu Sat)**: **115 Hz** (-6 dB Kreuzungspunkt, nahezu perfekte Phasenlage)
* **Mechanische Auslastung bei Vollast (51 W / 20 W)**:
    * **MX6-Treiber-Hub**: ≈ 5,3 mm (von 12 mm maximal)
    * **PR-Hub**: ≈ 9,0 mm (von 11 mm maximal)
    * **ND91-8 Hub**: ≈ 3,2 mm (von 5,1 mm maximal)

---

## 4. DSP-Konfiguration (ESP32)
Die folgenden Filter-Settings sind für den sicheren Betrieb und die optimale klangliche Harmonie (Übergang bei 115 Hz) zwingend erforderlich:

### A. Subwoofer-Kanal (MX6-22)
* **Subsonic-Filter**: Butterworth High-Pass, 4. Ordnung (24 dB/Oktave) @ **26 Hz**
* **Crossover (Tiefpass)**: Linkwitz-Riley Low-Pass, 4. Ordnung (24 dB/Oktave) @ **120 Hz**
* **EQ-Punch (Optional)**: Peak-Filter @ 40 Hz, Gain: +2,5 dB, Q: 1,4

### B. Satelliten-Kanal (ND91-8)
* **Crossover (Hochpass)**: Linkwitz-Riley High-Pass, 4. Ordnung (24 dB/Oktave) @ **95 Hz**

* **Crossover (Tiefpass)**: Linkwitz-Riley Low-Pass, 4. Ordnung (24 dB/Oktave) @ **ca. 3.500 Hz**

### C. Hochtöner-Kanal (ND16FA-6)
* **Crossover (Hochpass)**: Linkwitz-Riley High-Pass, 4. Ordnung (24 dB/Oktave) @ **ca. 3.500 Hz**

---

## 5. Gehäuse-Bauvorgaben
* **Brutto-Innenvolumen Sub-Kammer**: ≈ 13,5 bis 14,0 Liter (12 L Netto + 0,9 L Treiber + 0,6 L PR & Verstrebung).
* **Volumen Satelliten-Kammern**: Jeweils exakt **1,14 Liter Netto** (locker mit Sonofil gefüllt).
* **Bauform**: Subwoofer Downfiring (Bodenabstand mind. 35 mm durch Standfüße). Satelliten Front-Firing (Mittel- und Hochtöner so nah wie möglich beieinander).

---

## 6. Berechnungsformel der Leistung
Basierend auf der realen Impedanz des MX6-22 und der verfügbaren Spannung (24 V Netzteil):
P = U² / R = 15,5 V² / 4,7 Ohm ≈ 51,1 Watt