# Insane Sound Bar - SUB-RX (Subwoofer Empfänger)

Dieses Modul (ESP32-WROOM-32U) befindet sich im aktiven Subwoofer der *Insane Sound Bar*. Es empfängt Audiodaten drahtlos via ESP-NOW von der Soundbar und leitet diese über I2S an den PCM5102A-DAC und den TPA3116-Verstärker weiter.

## Hauptfunktionen

- **ESP-NOW Audio Empfang:** Empfängt einen Mono-Audiostream (11025 Hz, 16-Bit) in Paketen von der Master-Soundbar im reinen ESP-NOW Modus.
- **Access Point & NVS-Pairing:** Besitzt der Subwoofer noch keine Master-MAC-Adresse, startet er einen temporären WLAN Access Point ("Insane_Subwoofer") und ein Web-Interface (`192.168.4.1`). Über einen Button im Browser wird das Pairing initiiert. Die MAC wird dauerhaft im NVS gespeichert.
- **Dynamischer Jitter-Buffer:** Um Störgeräusche durch Paketverluste oder -verzögerungen zu verhindern, puffert ein FreeRTOS-Ring-Buffer eingehende Audiodaten. Die Threshold wird dynamisch über Header-Daten vom Sender bestimmt.
- **I2S Stereo Mirroring:** Das empfangene Mono-Signal wird im Buffer für den I2S-DMA verdoppelt (auf den linken und rechten Kanal gespiegelt), um beide Eingänge des TPA3116-Verstärkers anzusteuern.
- **Hardware-Mute & Anti-Pop:**
  - Der Mute-Pin des TPA3116 wird beim Booten sofort auf LOW gezogen.
  - Das Signal wird erst auf HIGH (Unmute) gesetzt, wenn der Jitter-Buffer mindestens zur Hälfte gefüllt ist und der Datenstrom kontinuierlich empfangen wird.
  - Bei einem Abbruch des Streams (Latenz > 100 ms) wird der Pin umgehend wieder auf LOW gezogen, um unerwünschtes Knacken oder Rauschen ("Pop"-Geräusche) zu blockieren.
- **Status-LED (Pin 4):**
  - **Pulsierend (1 Sekunde Intervall):** Im AP-Setup Modus, wartet auf User über Webinterface.
  - **Schnell blinkend (100 ms Intervall):** Im Pairing-Modus, sucht die Soundbar.
  - **Blinkend (500 ms Intervall):** Warte auf Audio Stream oder Jitter-Buffer füllt sich.
  - **Dauerlicht:** ESP-NOW Stream ist aktiv und gesund (Audio wird wiedergegeben).

## Kompilieren

Dieses Projekt basiert auf PlatformIO (`esp32dev` Umgebung mit Arduino Framework).

```bash
# Im Verzeichnis Firmware/SUB_RX/ ausführen
pio run
```
