# Übersetzungen

Jeder neue `_attr_translation_key` (Sensor, Binary-Sensor, Image, Config-Flow)
braucht einen passenden Eintrag in **allen drei** Dateien, sonst zeigt HA nur
den rohen Key oder Entity-ID-Fallback an:

- `strings.json`
- `translations/de.json`
- `translations/en.json`

**Bekannte Eigenheit:** `strings.json` enthält aktuell deutschen Text,
identisch zu `translations/de.json` – nicht den HA-üblichen englischen
Default. Bei neuen Einträgen also `strings.json` und `de.json` synchron mit
demselben (deutschen) Text halten, `en.json` mit der englischen Übersetzung.
Das ist eine bestehende Inkonsistenz im Repo, keine Vorlage zum Nachmachen bei
einem Cleanup – falls das mal bereinigt wird, ist das eine bewusste,
eigenständige Änderung.
