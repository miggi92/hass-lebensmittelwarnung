# Release-Prozess

Der komplette Release-Ablauf ist automatisiert, nichts davon von Hand anfassen:

1. Ein GitHub-Milestone mit einem Versionsnamen (`0.0.10` oder `v0.0.10`) wird
   geschlossen → `.github/workflows/milestone_release.yaml` erstellt daraus
   automatisch einen Git-Tag + GitHub-Release (`v<version>`).
2. Das veröffentlichte Release triggert `.github/workflows/publish.yaml`:
   - `custom_components/lebensmittelwarnung/manifest.json`s `version`-Feld
     wird per `sed` auf die Tag-Version gesetzt.
   - Die Integration wird gezippt und ans Release angehängt.
   - `changelogen` generiert den neuen Abschnitt in `CHANGELOG.md` für den
     Bereich seit dem letzten Tag und committet ihn direkt auf `main`.
   - Die Release-Beschreibung wird aus genau diesem Changelog-Abschnitt
     befüllt.

**Wichtig für Änderungen/PRs:**

- `version` in `manifest.json` NICHT manuell hochzählen – das passiert erst
  beim tatsächlichen Release aus dem Tag. Ein manueller Bump in einem
  Feature-PR ist überflüssig und kann beim nächsten Release wieder
  überschrieben werden.
- `CHANGELOG.md` NICHT manuell editieren – wird ausschließlich vom
  Publish-Workflow geschrieben.
- Ob eine Änderung als `feat`/`fix`/... committet wird, entscheidet, in
  welchem Abschnitt sie im nächsten Changelog landet (siehe `commits.md`).
