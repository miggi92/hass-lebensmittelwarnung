# Commit-Konventionen

Commit-Messages folgen [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<scope>): <description>`, Scope optional.

Der Changelog (`CHANGELOG.md`) wird per [changelogen](https://github.com/unjs/changelogen)
aus genau diesen Commit-Messages generiert (siehe `release.md`). Nur folgende
Typen landen im Changelog, mit diesen Überschriften (siehe `changelog`-Feld in
`package.json`):

| Typ        | Abschnitt im Changelog |
| ---------- | ---------------------- |
| `feat`     | ✨ Features              |
| `fix`      | 🐛 Bugfixes              |
| `docs`     | 📚 Dokumentation         |
| `refactor` | 🚜 Refactoring           |
| `perf`     | ⚡ Performance            |
| `test`     | 🧪 Tests                 |
| `ci`       | ⚙️ CI                    |
| `chore`    | 🔧 Sonstiges             |
| `revert`   | ◀️ Revert                |

Alles andere (z.B. `style`, `build`, unkonventionelle Messages, Merge-Commits)
wird stillschweigend übersprungen.

- `chore(deps): ...` (Renovate-Commits) werden von changelogen automatisch
  ausgeblendet – dafür ist keine zusätzliche Konfiguration nötig.
- Autoren-Namen/E-Mails tauchen im Changelog nicht auf (`noAuthors: true`).
  Das ist bewusst so, nicht nachträglich "reparieren".
