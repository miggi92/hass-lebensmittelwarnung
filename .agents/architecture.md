# Architektur

Ein Config-Entry entspricht einer Kombination aus Meldungsart (`type_key`) und
Bundesland (`state_key`). Jede Kombination bekommt einen eigenen
`LebensmittelwarnungCoordinator` (`coordinator.py`), der den RSS-Feed pollt und
die letzten `MAX_ENTRIES` geparsten Meldungen als Liste hält
(`coordinator.data`, neueste zuerst; `coordinator.latest` ist `data[0]`).

**Fehlertoleranz:** Schlägt ein Feed-Abruf fehl, liefert der Coordinator die
letzten bekannten Daten weiter, bis `MAX_CONSECUTIVE_FAILURES` Polls in Folge
fehlgeschlagen sind – erst dann gehen die Entities auf `unavailable`. Nicht
"vereinfachen" zu einem direkten `raise UpdateFailed`, siehe `decisions.md`.

**Sensoren:** ein Sensor pro Feld, eine Datei pro Sensor, unter `sensors/`.

- Neuer Sensor → Datei in `sensors/`, Klasse erbt von `LmwSensorBase`
  (`sensors/base.py`), UND in `SENSOR_CLASSES` in `sensors/__init__.py`
  eintragen. Ohne den Eintrag dort wird der Sensor nie erzeugt.
- Attribute mit allen Details einer Meldung (Latest/Previous/Count, Event)
  kommen aus `entry_attributes()` in `sensors/base.py` – neue Felder dort
  ergänzen, nicht in jeder Entity einzeln.
- `shorten()` aus `sensors/base.py` für alles benutzen, was als `native_value`
  in den State geschrieben wird (255-Zeichen-Limit von HA) – nicht für
  `extra_state_attributes`, da gilt das Limit nicht.
- Der `binary_sensor.py` (`recent_warning`) ist eine eigene Plattform, kein
  Teil von `sensors/`, weil er kein Feld einer Meldung zeigt, sondern einen
  reinen Zeitfenster-Zustand (24h seit `published`). Er verwaltet dafür einen
  eigenen `async_track_point_in_utc_time`-Timer statt sich nur auf den
  stündlichen Coordinator-Poll zu verlassen (siehe Git-History für den Bug,
  den das behoben hat).

**Weitere Plattformen neben `sensors/`:**

- `event.py` (`new_warning`) feuert ein Event pro neuer `guid`. Beim Start
  gilt alles im Feed als bekannt (keine Event-Flut nach Neustart), gesehene
  guids werden nie vergessen. Das ist der empfohlene Trigger für
  Benachrichtigungen, siehe `decisions.md`.
- `calendar.py` zeigt die gehaltenen Meldungen als ganztägige Termine am
  (lokalen) Tag der Veröffentlichung.
- `diagnostics.py` liefert Coordinator-Status und geparste Meldungen für den
  Diagnose-Download in HA.
- `coordinator.last_success` ist der Zeitpunkt des letzten *echten*
  erfolgreichen Abrufs (wegen der Fehlertoleranz sagt `last_update_success`
  das nicht aus). Der Sensor `last_success` bleibt deshalb auch verfügbar,
  wenn der Coordinator aufgegeben hat.

**Hinweis für lokale Tests:** Die Datei `calendar.py` überdeckt die
Stdlib-`calendar`, wenn Python direkt aus dem Integrationsordner gestartet
wird. In HA ist das egal (Paket-Import), Tests also vom Repo-Root aus starten.

**Neue Übersetzungsschlüssel:** siehe `translations.md`.
