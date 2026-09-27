"""Stichwort- und Produktlisten-Suche für die Watchlist."""

from __future__ import annotations

from datetime import timedelta
import re
from typing import Any

from homeassistant.core import HomeAssistant

# Wie lange eine passende Meldung den Watchlist-Sensor "an" hält.
WATCHLIST_WINDOW = timedelta(days=7)

# Kontakt, Haltbarkeit und Charge bleiben bewusst außen vor: dort stehen
# Adressen, Hotlines und Datumsangaben, die nur Fehlalarme erzeugen.
SEARCH_FIELDS = ("product", "manufacturer", "reason")

# Kürzere Wörter aus Produktnamen ("TK", "400", "30l") werden ignoriert.
MIN_PRODUCT_WORD_LENGTH = 4

_WORD_RE = re.compile(r"\w+")


def _haystack(entry: dict[str, Any]) -> str:
    return " ".join(entry.get(field) or "" for field in SEARCH_FIELDS).casefold()


def find_matches(entry: dict[str, Any], keywords: list[str]) -> list[str]:
    """Alle Stichwörter, die in einem der Suchfelder vorkommen.

    Groß-/Kleinschreibung egal, Teilwort-Suche (deutsche Komposita:
    "Käse" soll auch "Weinbauernkäse" finden).
    """
    haystack = _haystack(entry)
    return [keyword for keyword in keywords if keyword.casefold() in haystack]


def product_words(name: str) -> list[str]:
    """Die für den Abgleich relevanten Wörter eines Produktnamens."""
    return [
        word
        for word in _WORD_RE.findall(name.casefold())
        if len(word) >= MIN_PRODUCT_WORD_LENGTH
    ]


def find_product_matches(entry: dict[str, Any], products: list[str]) -> list[str]:
    """Produkte, deren relevante Wörter alle in der Meldung vorkommen.

    Anders als bei Stichwörtern reicht hier kein Teilstring des ganzen
    Namens: "Bio Wildheidelbeeren TK" soll auch "EDEKA Bio Wildheidelbeeren
    tiefgefroren" finden. Produkte ohne relevantes Wort ("Ibu 400") werden
    nie gemeldet.
    """
    haystack = _haystack(entry)
    matches = []
    for name in products:
        words = product_words(name)
        if words and all(word in haystack for word in words):
            matches.append(name)
    return matches


def product_names(
    hass: HomeAssistant, entity_id: str | None, attribute: str, name_key: str
) -> list[str]:
    """Produktnamen aus dem Attribut einer Entity, z.B. sensor.grocy_stock.

    Das Attribut darf eine Liste von Dicts (Name unter name_key) oder von
    Strings sein. Fehlt die Entity oder passt das Format nicht, gibt es
    einfach keine Produkte.
    """
    if not entity_id or (state := hass.states.get(entity_id)) is None:
        return []
    items = state.attributes.get(attribute)
    if not isinstance(items, list):
        return []
    names = []
    for item in items:
        name = item.get(name_key) if isinstance(item, dict) else item
        if isinstance(name, str):
            names.append(name)
    return normalize_keywords(names)


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
