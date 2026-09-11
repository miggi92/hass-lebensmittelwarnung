# Architektur

Ein Config-Entry entspricht einer Kombination aus Meldungsart (`type_key`) und
Bundesland (`state_key`). Jede Kombination bekommt einen eigenen
`LebensmittelwarnungCoordinator` (`coordinator.py`), der den RSS-Feed pollt und
die letzten `MAX_ENTRIES` geparsten Meldungen als Liste hält
(`coordinator.data`, neueste zuerst; `coordinator.latest` ist `data[0]`).

**Sensoren:** ein Sensor pro Feld, eine Datei pro Sensor, unter `sensors/`.

- Neuer Sensor → Datei in `sensors/`, Klasse erbt von `LmwSensorBase`
  (`sensors/base.py`), UND in `SENSOR_CLASSES` in `sensors/__init__.py`
  eintragen. Ohne den Eintrag dort wird der Sensor nie erzeugt.
- `shorten()` aus `sensors/base.py` für alles benutzen, was als `native_value`
  in den State geschrieben wird (255-Zeichen-Limit von HA) – nicht für
  `extra_state_attributes`, da gilt das Limit nicht.
- Der `binary_sensor.py` (`recent_warning`) ist eine eigene Plattform, kein
  Teil von `sensors/`, weil er kein Feld einer Meldung zeigt, sondern einen
  reinen Zeitfenster-Zustand (24h seit `published`). Er verwaltet dafür einen
  eigenen `async_track_point_in_utc_time`-Timer statt sich nur auf den
  stündlichen Coordinator-Poll zu verlassen (siehe Git-History für den Bug,
  den das behoben hat).

**Neue Übersetzungsschlüssel:** siehe `translations.md`.
