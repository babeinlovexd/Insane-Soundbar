# Insane-Soundbar v0.1.9

Update-Adresse des Control Centers auf dieses Repository korrigiert; exakte Firmware-Dateinamen statt unscharfer Suche. Architektur und Entwicklungsstand dokumentiert. Das Gesamtsystem ist bisher nicht auf echter Hardware validiert.

Die Release-Version bezeichnet den Repository-Stand, nicht eine neue PCB-Revision. Quellcode-Pakete enthalten keine `secrets.yaml`. Persönliche Einstellungen müssen vor einem Firmware-Build angepasst werden.

Die Audio-YAML verwendet die aktuelle `audio.codecs`-Konfiguration für ESPHome 2026.10.2; FLAC-Transcoding bleibt eingestellt. Bluetooth-Toolchains mit älterer I2S-API werden passend festgelegt.
