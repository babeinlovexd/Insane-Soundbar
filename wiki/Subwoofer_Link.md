# Wireless Subwoofer Link

Der Subwoofer der Insane Soundbar ist komplett kabellos und nutzt das verzögerungsarme **ESP-NOW** Protokoll zur Audioübertragung im Unicast-Modus.

## Hardware und Architektur
Der DSP wandelt das Audiosignal durch einen effizienten Modulo-Counter (`& 3`) von 44.1 kHz in einen 11025 Hz (16-bit) Stream für den Subwoofer um, um die Bandbreite für ESP-NOW zu optimieren. Der SUB-TX empfängt diesen I2S-Stream im Slave-RX-Modus.

## Das Pairing-Protokoll
Damit der Sender (SUB-TX) den Empfänger (SUB-RX) findet:
1. Der Nutzer aktiviert das Pairing (I2C Kommando `0x04` auf dem TX).
2. Der TX sendet Broadcast-Pakete des Typs `pairing_packet_t` (Typ = `1`).
3. Befindet sich der RX im Pairing-Modus, antwortet dieser mit einem Unicast-ACK (Typ = `2`).
4. Der TX speichert die MAC-Adresse des RX fest im NVS (Non-Volatile Storage), um bei künftigen Starts die Unicast-Verbindung direkt herzustellen.

## ESP-NOW Audio Callback
Beim Empfänger (SUB-RX) akzeptiert der ESP-NOW Callback dynamische Paketgrößen bis maximal `sizeof(audio_packet_t)`. Dies dient dem Ausgleich von I2S DMA-Buffer-Drift und verhindert Micro-Stottern während der Wiedergabe.
