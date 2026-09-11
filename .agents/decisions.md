# Entscheidungsprotokoll

Kurzes Log architektonischer/prozessualer Entscheidungen, damit ein neuer
Chat oder ein anderer KI-Assistent nicht bei Null anfängt und nicht versucht,
bereits bewusst getroffene Entscheidungen "aufzuräumen". Neueste zuerst.

**Pflicht:** Wird eine vergleichbare Entscheidung getroffen (Design, Ablehnung
einer Alternative, bewusste Abweichung von einer Konvention), hier einen neuen
Eintrag ergänzen – im selben PR, nicht als Nachtrag.

---

## 2026-09-11 – `.agents/`-Doku für KI-Agents eingeführt

**Entscheidung:** Konventionen in `.agents/*.md` auslagern, per `@`-Import in
`CLAUDE.md` automatisch geladen (nicht nur eine lose Doku, die niemand liest).

**Warum:** Über eine Session hinweg wurden mehrere Konventionen erarbeitet
(Release-Ablauf, Sensor-Pattern, Übersetzungs-Sync), die aus dem Code allein
nicht ersichtlich sind. Ohne zentrale Doku müsste das jedes Mal neu erklärt
werden.

## 2026-09-11 – Changelog-Tooling: git-cliff → changelogen

**Entscheidung:** `cliff.toml` entfernt, stattdessen `package.json`/`pnpm` mit
[changelogen](https://github.com/unjs/changelogen), Konfiguration im
`changelog`-Feld von `package.json`.

**Warum:** git-cliff erzeugte zuletzt fehlerhafte Abschnitte (0.0.9 bestand
nur aus dem vorherigen "Changelog aktualisiert"-Meta-Commit statt der
eigentlichen Änderungen). Es werden ohnehin Conventional Commits genutzt,
changelogen bildet dieselben Kategorien ab und blendet `chore(deps)` sowie
Autoren-Infos automatisch/konfigurierbar aus.

**Verworfen:** Bei git-cliff bleiben und nur die Config reparieren – wurde
nicht weiterverfolgt, da der Nutzer explizit den Werkzeugwechsel wollte.

## 2026-09-11 – `manifest.json`-Version wird nie manuell gepflegt

**Entscheidung/Lektion:** `version` in `manifest.json` NICHT von Hand
hochzählen. Der `Publish`-Workflow setzt sie automatisch aus dem Release-Tag.

**Warum:** Ein manueller Bump auf `0.0.9` in einem Feature-PR war im
Nachhinein überflüssig, weil das nächste echte Release sie ohnehin
überschreibt. Um Verwirrung/Doppelarbeit zu vermeiden, ist das jetzt explizit
in `release.md` festgehalten.

## 2026-09-11 – Feed-Historie auf 10 Einträge begrenzt, Übersicht am Count-Sensor

**Entscheidung:** `MAX_ENTRIES` von 20 auf 10 reduziert. `sensor.anzahl_meldungen`
bekommt ein `meldungen`-Attribut mit den vollen Details (gleiche Felder wie
"Letzte"/"Vorherige Meldung") zu allen aktuell gehaltenen Einträgen.

**Warum:** Nutzerwunsch – mehr als die letzten 10 Meldungen sind praktisch
selten relevant; die Attribute sollen als schnelle Übersicht der Historie
dienen, ohne 10 Einzelsensoren anlegen zu müssen.

## 2026-09-11 – `recent_warning`-Timer, Detail-Sensoren bleiben befüllt, neuer `previous`-Sensor

**Entscheidungen:**

1. `binary_sensor.aktuelle_warnung` plant einen eigenen
   `async_track_point_in_utc_time`-Timer für `published + 24h`, statt sich
   nur auf den stündlichen Coordinator-Poll zu verlassen.
2. Die Detail-Sensoren (Grund, Charge, Haltbarkeit, Produkt, Hersteller,
   "Letzte Meldung" usw.) bleiben bewusst dauerhaft mit der letzten bekannten
   Meldung befüllt, auch wenn sie älter als 24h ist – der binary_sensor bleibt
   der einzige "ist das noch aktuell?"-Indikator.
3. Neuer Sensor `previous` ("Vorherige Meldung") statt `latest`
   umzubenennen oder dessen Bedeutung zu ändern.

**Warum:** (1) behebt einen echten Bug – ein verzögerter/fehlgeschlagener
Poll ließ den Sensor über die 24h-Grenze hinaus "an". (2) und (3) sind
Nutzerentscheidungen aus einer expliziten Rückfrage: "Letzte Meldung" sollte
weiterhin die neueste Meldung zeigen (nicht geleert werden), aber zusätzlich
sollte ein Sensor existieren, der sich vom aktuellen Stand unterscheiden kann.

**Verworfen:** Detail-Sensoren nach Ablauf der 24h auf `None` setzen; `latest`
in "Neueste Meldung" umbenennen statt einen zweiten Sensor zu ergänzen.
