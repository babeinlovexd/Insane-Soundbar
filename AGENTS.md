# Agent Instructions: Project Insane Soundbar 

Dieses Dokument ist das oberste Gesetz für alle KI-Agenten. Wer hier Code schreibt, muss diese Regeln zwingend befolgen.

## 1. Rollenverteilung & Zuständigkeit
- **Master (ESP32-S3):** Einzige Instanz für Home Assistant, WLAN, Infrarot-Parsing und die Logik der UART-Bridges. Er "weiß", welcher Eingang aktiv ist, und steuert die Slaves.
- **DSP (RP2354):** Ausschließlich für die Audio-Mathematik zuständig (EQ, Biquads, DRC, Crossover). Er empfängt Befehle nur via I2C.
- **Slaves (BT/Sub-TX):** Reine Funktionsmodule. Sie verarbeiten Audio-Datenströme und reagieren auf Hardware-Pins (EN/BOOT) des Masters.

## 2. Quelloffenheit & Transparenz
- Das gesamte Projekt ist **Open Source**. Es wird keine "Closed Source" Logik, keine binären Blobs ohne Quellcode und keine proprietären Bibliotheken verwendet, die den Codeverlauf verschleiern.

## 3. Die "Source of Truth" (Dateipfade)
Bevor Code geändert wird, MÜSSEN diese Dokumente gelesen werden. Änderungen im Code müssen sofort in diesen Dateien dokumentiert werden:
- **Hardware-Plan:** `Plans/ISB-PinMapping_v3.md` (Keine Software-Hacks gegen diesen Plan!).
- **I2C-Protokoll:** `Plans/i2c_register_map.md` (Jedes neue Register im DSP muss hier ZUERST eingetragen werden).

## 4. Hardware-Gesetze 
- **Keine Pin-Doppelbelegung:** Bevor ein Pin in ESPHome zugewiesen wird, prüfe `Plans/ISB-PinMapping_v3.md`.

## 5. Ordnung, Sauberkeit & Dateipflege
- **Temp-Dateien:** Temporäre Dateien, Build-Artefakte oder Test-Logs dürfen nicht im Repository verbleiben. Nach der Generierung/Prüfung ist aufzuräumen.
- **Verzeichnisstruktur:** Neue Dateien müssen logisch in `Firmware/`, `Plans/`, `PCB/` oder `Datasheets/` eingeordnet werden. Keine losen Dateien im Root-Verzeichnis (außer README und AGENTS.md).
- **Code-Qualität:** Keine ungenutzten Imports, keine auskommentierten "Leichen". Der Code muss so sauber sein wie das Platinen-Layout.

