# Entscheidungsprotokoll

Kurzes Log architektonischer/prozessualer Entscheidungen, damit ein neuer
Chat oder ein anderer KI-Assistent nicht bei Null anfängt und nicht versucht,
bereits bewusst getroffene Entscheidungen "aufzuräumen". Neueste zuerst.

**Pflicht:** Wird eine vergleichbare Entscheidung getroffen (Design, Ablehnung
einer Alternative, bewusste Abweichung von einer Konvention), hier einen neuen
Eintrag ergänzen – im selben PR, nicht als Nachtrag.

---

## 2026-10-02 – `feedparser` mit Untergrenze statt festem Pin

**Entscheidung:** `manifest.json` verlangt `feedparser>=6.0.12` statt
`feedparser==6.0.14`.

**Warum:** Home Assistant gibt `feedparser` selbst fest vor (aktuell 6.0.12 in
der Entwicklerversion). Ein abweichender fester Pin macht hassfest rot
(`hassfest@master` prüft gegen die HA-Entwicklerversion) und kann bei der
Installation mit den HA-Constraints kollidieren. Mit Untergrenze nimmt pip die
Version, die die jeweilige HA-Installation vorgibt.

**Nicht „aufräumen“:** Nicht wieder auf `==` umstellen, und Renovate-Updates,
die den Pin hochziehen wollen, nicht blind mergen.

## 2026-09-27 – Watchlist: optionale Produktliste aus einer Entity (Grocy)

**Entscheidungen:**

1. Die Produktliste ist generisch konfigurierbar (Entity + Attribut +
   Namensfeld, Defaults `products`/`name` passend zu Grocy) statt einer
   festen Grocy-Anbindung – nicht jeder hat Grocy, und Entity-Namen
   unterscheiden sich. Das Attribut darf auch eine Liste von Strings sein.
2. Produktnamen werden per **Wortregel** abgeglichen: alle Wörter mit ≥ 4
   Zeichen müssen in Produkt/Hersteller/Grund vorkommen (je als Teilwort).
   So findet „Bio Wildheidelbeeren TK“ auch „EDEKA Bio Wildheidelbeeren
   tiefgefroren“. Namen ohne solches Wort („Ibu 400“) werden nie gemeldet.
3. Treffer zeigen die Quelle: im Sensor-Attribut `treffer` getrennt als
   `stichwoerter`/`produkte`; im Event enthält `watchlist_treffer` beide
   zusammen (einfaches Filtern), `watchlist_produkte` nur die aus der Liste.

**Warum:** Nutzerwunsch. Vorher geprüft: Der Grocy-Bestand des Nutzers hat
keine Barcodes, der Feed keine EANs und Grocy keine Chargennummern – ein
exakter Abgleich ist nicht möglich, es bleibt nur der Name. Reine
Teilstring-Suche des ganzen Namens hätte abweichende Schreibweisen verpasst.

**Verworfen:** Direkte Abfrage der Grocy-API (eigene Zugangsdaten, doppelte
Konfiguration neben der bestehenden Grocy-Integration); Barcode-/Chargen-Abgleich
(Daten fehlen auf beiden Seiten).

## 2026-09-27 – Watchlist-Binary-Sensor per Options-Flow

**Entscheidungen (Nutzerentscheidungen aus einer expliziten Rückfrage):**

1. Eine Stichwortliste pro Feed-Eintrag im Options-Flow, keine mehreren
   benannten Listen (Subentries).
2. Gesucht wird nur in Produkt, Hersteller und Grund – nicht in Kontakt,
   Haltbarkeit oder Charge (Adressen/Hotlines erzeugen Fehlalarme, z.B.
   „Berlin“). Groß-/Kleinschreibung egal, Teilwort-Suche wegen deutscher
   Komposita („Käse“ findet „Weinbauernkäse“); dass kurze Stichwörter wie
   „Ei“ dadurch zu viel finden, ist bewusst in Kauf genommen.
3. `binary_sensor.watchlist` ist an, solange eine Meldung der letzten 7 Tage
   passt (fest, nicht konfigurierbar); eigener Ablauf-Timer wie beim
   24h-Sensor. Er wird auch ohne Stichwörter angelegt (dann `off`), damit die
   Entity-ID stabil ist.
4. Das „Neue Meldung“-Event bekommt `watchlist_treffer` (Liste der passenden
   Stichwörter), damit Automationen ohne zweiten Trigger filtern können.

**Verworfen:** Konfigurierbares Zeitfenster; Suche in allen Textfeldern.

## 2026-09-27 – Kaputter Feed-Titel: Fallback auf Produktbezeichnung

**Entscheidung:** Beginnt der Titel einer Meldung mit `$` (der Feed liefert
aktuell wörtlich `$esc.escapeXml($cms.oneLineText($m.title))`), setzt
`parser.py` stattdessen die Produktbezeichnung (einzeilig, Zeilen mit „, “
verbunden) ein, ersatzweise den Grund.

**Warum:** Serverseitiger Fehler von lebensmittelwarnung.de – der echte Titel
steht nirgends im Feed. Betroffen waren „Letzte/Vorherige Meldung“,
`titel`-Attribute, Event und Kalender. Liefert der Feed wieder echte Titel,
greift der Fallback automatisch nicht mehr.

**Verworfen:** Den Titel von der verlinkten Detailseite nachladen – zusätzliche
Requests an einen ohnehin wackeligen Server, und die Seitenstruktur war nicht
prüfbar.

## 2026-09-27 – Event-Entity für neue Meldungen, neue Felder als Sensoren

**Entscheidungen:**

1. Neue `event`-Entity `new_warning`, die pro neuer `guid` genau einmal
   feuert. Beim Start sind alle aktuellen Feed-Einträge „bekannt“; gesehene
   guids werden nicht wieder vergessen (auch nicht, wenn sie aus den
   `MAX_ENTRIES` herausfallen).
2. Bisher nur geparste Felder bekommen eigene Sensoren: Verpackungseinheit
   (`package`) und Betroffene Bundesländer (`affected_states`, zusätzlich als
   Liste im Attribut `bundeslaender`). „Kontakt“ nur als Attribut
   (`kontakt`) am Hersteller-Sensor und in den Detail-Attributen – ein
   eigener Sensor lohnt sich dafür nicht.
3. Kalender-Termine sind ganztägig am Veröffentlichungstag, nicht 24h ab
   `published` – das 24h-Fenster bleibt Sache von `binary_sensor.aktuelle_warnung`.
4. `recent_count` (Meldungen der letzten 7 Tage) zählt nur die gehaltenen
   `MAX_ENTRIES` Einträge, ist also bei sehr vielen Meldungen eine
   Untergrenze. Bewusst so, statt dafür mehr Einträge zu halten.

**Warum:** (1) behebt das Problem doppelter Benachrichtigungen grundsätzlich:
Zustandsänderungen von Sensoren (Neustart, `unavailable`) sind kein
verlässlicher „neue Meldung“-Trigger. (2)–(4) Nutzerwunsch aus einer
Vorschlagsrunde.

**Offen:** Watchlist-Binary-Sensor (Stichwörter per Options-Flow) wurde
vorgeschlagen, aber auf später verschoben.

## 2026-09-27 – Einzelne Feed-Fehler lassen Entities nicht mehr `unavailable` werden

**Entscheidung:** Der Coordinator toleriert bis zu `MAX_CONSECUTIVE_FAILURES - 1`
fehlgeschlagene Polls in Folge (aktuell 2, also ~2h) und liefert solange die
letzten bekannten Meldungen weiter (mit Warning im Log). Erst beim dritten
Fehlschlag in Folge wird `UpdateFailed` durchgereicht.

**Warum:** lebensmittelwarnung.de bricht Verbindungen sporadisch ab
("Connection reset by peer", DNS-Timeouts). Jeder dieser Aussetzer setzte
alle Sensoren für eine Stunde auf `unavailable` und danach zurück – eine
Automation auf Zustandsänderungen von "Produktbezeichnung" verschickte
dadurch doppelte Benachrichtigungen mit `unavailable`-Werten.

**Verworfen:** Nur in der Automation `unavailable`/`unknown` filtern – hilft
dem Nutzer, lässt aber Verlauf und andere Konsumenten weiter flackern.

## 2026-09-11 – `.agents/AGENTS.md` ist ein Verweis, kein zweiter Index

**Entscheidung:** `.agents/AGENTS.md` importiert die Themendateien nicht
selbst noch einmal, sondern verweist nur auf `CLAUDE.md` im Repo-Root.

**Warum:** Zwei Dateien mit identischer Import-Liste würden bei der nächsten
Änderung garantiert auseinanderlaufen – genau das Problem, das dieses Log
verhindern soll. `CLAUDE.md` bleibt die einzige maßgebliche Einstiegsdatei;
`AGENTS.md` existiert nur, weil manche Tools gezielt danach suchen.

**Zu beachten:** Diese Datei liegt unter `.agents/`, nicht im Repo-Root. Tools,
die die AGENTS.md-Konvention nutzen, erwarten sie meist im Root – falls
breitere Cross-Tool-Kompatibilität gewünscht ist, wäre eine zusätzliche, sehr
kurze `AGENTS.md` im Root (mit demselben Verweis) der nächste Schritt.

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
