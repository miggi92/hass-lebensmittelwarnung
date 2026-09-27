"""Stichwort-Suche für die Watchlist."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

# Wie lange eine passende Meldung den Watchlist-Sensor "an" hält.
WATCHLIST_WINDOW = timedelta(days=7)

# Kontakt, Haltbarkeit und Charge bleiben bewusst außen vor: dort stehen
# Adressen, Hotlines und Datumsangaben, die nur Fehlalarme erzeugen.
SEARCH_FIELDS = ("product", "manufacturer", "reason")


def find_matches(entry: dict[str, Any], keywords: list[str]) -> list[str]:
    """Alle Stichwörter, die in einem der Suchfelder vorkommen.

    Groß-/Kleinschreibung egal, Teilwort-Suche (deutsche Komposita:
    "Käse" soll auch "Weinbauernkäse" finden).
    """
    haystack = " ".join(
        entry.get(field) or "" for field in SEARCH_FIELDS
    ).casefold()
    return [keyword for keyword in keywords if keyword.casefold() in haystack]


def normalize_keywords(raw: list[str] | None) -> list[str]:
    """Leere Einträge und Duplikate (ohne Groß-/Kleinschreibung) entfernen."""
    result: list[str] = []
    seen: set[str] = set()
    for keyword in raw or []:
        keyword = keyword.strip()
        if keyword and keyword.casefold() not in seen:
            seen.add(keyword.casefold())
            result.append(keyword)
    return result
