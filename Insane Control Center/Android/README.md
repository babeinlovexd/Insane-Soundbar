# Insane Control Center für Android

Flet-App zur Bedienung der [Insane Soundbar](../../README.md) über deren HTTP-Schnittstelle. Geräte werden per mDNS gesucht; Favoriten und Profile werden lokal gespeichert. Das Soundbar-Gesamtsystem befindet sich in Entwicklung.

Diese App bietet keinen Firmware-Flasher. Zum Flashen dient das Desktop-Control-Center oder das passende Herstellerwerkzeug mit der korrekten Bootloader-Verbindung.

## Start aus dem Quellcode

Python 3.12 verwenden und im Verzeichnis dieser README ausführen:

```bash
python -m pip install -r requirements.txt
flet run src/main.py
```

## Android-APK bauen

Der zentrale [Build-Workflow](../../.github/workflows/release.yml) baut die APK und stellt sie nach erfolgreichem Gesamtlauf im [Release](https://github.com/babeinlovexd/Insane-Soundbar/releases) bereit. Ein manueller Workflow-Lauf liefert Build-Artefakte.

Für einen lokalen Build werden zusätzlich die von Flet benötigten Flutter-/Android-Werkzeuge benötigt:

```bash
flet build apk --module-name main --no-rich-output --yes
```

Die App nutzt das Verzeichnis `src`, wie in [pyproject.toml](pyproject.toml) konfiguriert. Freigaben für das lokale Netzwerk müssen auf dem Android-Gerät zugelassen sein.
