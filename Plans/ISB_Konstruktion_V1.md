# Konstruktionsblatt: Insane Sound Bar (V1.0)

## 1. Gehäuse-Konzept
* **Typ**: 2.1 System (Stereo-Bar + externer Wireless Sub)
* **Aufbau**: 3-Kammer-System (Links, Mitte, Rechts)
* **Gesamtbreite**: 600 mm (3 x 200 mm Segmente)
* **Außenmaße (pro Box-Sektion)**: 200 mm (B) x 90 mm (H) x 117 mm (T)
* **Material**: 3D-Druck (Wandstärke 4 mm empfohlen)
* **Akustik**: Bassreflex-Prinzip via Passivmembran (DMA70-PR)[cite: 2]

---

## 2. Bestückung pro Seite (Links / Rechts)
| Komponente | Modell | Funktion | Montage-Info |
| :--- | :--- | :--- | :--- |
| **Mitteltöner** | Dayton Audio PC68-8 | 120 Hz – 4.500 Hz[cite: 4] | Außendurchmesser 68 mm[cite: 4] |
| **Hochtöner** | Dayton Audio ND16FA-6 | 4.500 Hz – 20 kHz+[cite: 3] | Press-fit (Loch ~25 mm)[cite: 3] |
| **Passivmembran** | Dayton Audio DMA70-PR | Bass-Unterstützung[cite: 2] | 70x70 mm Frontplatte[cite: 2] |

---

## 3. Gehäuse-Berechnungen (Pro Kammer)
* **Netto-Volumen ($V_b$)**: 1,5 Liter ($1500\text{ cm}^3$)[cite: 4]
* **Innenmaße**: 192 mm (B) x 82 mm (H) x 95 mm (T)
* **Abstimmfrequenz ($f_p$)**: ca. 47 Hz (mit DMA70-PR ohne Zusatzgewicht)[cite: 2]
* **Trennfrequenz zum Sub**: 120 Hz (Aktiv-Crossover)

---

## 4. CAD & Design-Vorgaben
### Chassis-Layout (Front-Firing)
* **ND16FA-6**: Ganz außen platzieren (Stereo-Abbildung). Einbautiefe ca. 15 mm[cite: 3].
* **PC68-8**: Mittig in der 20 cm Sektion. Einbautiefe ca. 37 mm[cite: 4].
* **DMA70-PR**: Innenliegend (Richtung PCB-Sektion). Einbautiefe ca. 41 mm[cite: 2].
* **Wichtig**: Da die Diagonale der Passivmembran **84,1 mm** beträgt[cite: 2], bei einer Innenhöhe von **82 mm**, müssen oben/unten im Gehäuseinneren **1,1 mm tiefe Kerben** für die Ecken des Rahmens eingeplant werden.

### Luftdichtigkeit & Stabilität
* **Kammer-Trennung**: Die Lautsprecher-Sektionen müssen absolut luftdicht zur mittleren Elektronik-Sektion sein.
* **Kabeldurchführung**: Löcher nach der Verkabelung mit Heißkleber oder Silikon versiegeln.
* **Dämmung**: Jede Box-Sektion locker mit Polyester-Dämmwatte füllen (Rückseite der Passivmembran muss frei bleiben)[cite: 2].
* **Dichtungen**: Nutzen von 2 mm Moosgummi oder Silikon unter den Flanschen von PC68-8 und DMA70-PR[cite: 2, 4].

---

## 5. 3D-Druck Parameter (Empfehlung)
* **Wandstärke**: 4 mm (entspricht ca. 8-10 Walls bei einer 0,4 mm Düse).
* **Infill**: 20% Gyroid für hohe Steifigkeit und Resonanzdämpfung.
* **Versiegelung**: Innenseiten der Boxen mit Epoxidharz oder Spritzfüller behandeln, um die Layer-Struktur luftdicht zu machen.
* **Verbindung**: 10 mm Falz (Überlappung) zwischen den 20 cm Sektionen zum Verkleben/Verschrauben.

---

## 6. Elektronik-Integration (Mittelteil)
* **OLED**: Ausschnitt für 1,3" Display (36 mm x 34 mm Modulmaße).
* **IR**: Loch für TSOP4838 Linse (Ø 5 mm).
* **TOSLINK/USB**: Aussparungen an der Rückseite für die Anschlüsse auf dem S3-Board.