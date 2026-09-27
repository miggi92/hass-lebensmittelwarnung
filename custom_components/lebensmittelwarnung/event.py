"""Feuert ein Event für jede neu im Feed auftauchende Meldung."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LmwConfigEntry
from .coordinator import LebensmittelwarnungCoordinator
from .entity import LmwEntity
from .sensors.base import entry_attributes
from .watchlist import find_matches, find_product_matches

EVENT_NEW_WARNING = "new_warning"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([LmwNewWarningEvent(entry.runtime_data)])


class LmwNewWarningEvent(LmwEntity, EventEntity):
    """Ein Event pro neuer Meldung (erkannt an der guid).

    Anders als Zustandsänderungen der Sensoren löst das weder beim Neustart
    noch bei einem Wechsel nach/von "unavailable" aus - der robuste Trigger
    für Benachrichtigungen.
    """

    _attr_translation_key = "new_warning"
    _attr_event_types = [EVENT_NEW_WARNING]

    def __init__(self, coordinator: LebensmittelwarnungCoordinator) -> None:
        super().__init__(coordinator, "new_warning")
        # Beim Start ist alles im Feed "schon bekannt", sonst gäbe es nach
        # jedem HA-Neustart eine Flut von Events für alte Meldungen.
        self._seen: set[str] = self._guids()

    def _guids(self) -> set[str]:
        return {
            entry["guid"] for entry in self.coordinator.data or [] if entry.get("guid")
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        new = [
            entry
            for entry in self.coordinator.data or []
            if entry.get("guid") and entry["guid"] not in self._seen
        ]
        # Älteste zuerst, damit das letzte Event (= Entity-Zustand) die
        # neueste Meldung ist. Bereits gesehene guids werden bewusst nicht
        # vergessen: fällt eine Meldung kurz aus dem Feed und taucht wieder
        # auf, soll sie nicht erneut melden. Bei ~10 Meldungen pro Tag ist
        # das Set auch über Jahre vernachlässigbar klein.
        products = self.coordinator.product_names() if new else []
        for entry in reversed(new):
            self._seen.add(entry["guid"])
            found_keywords = find_matches(entry, self.coordinator.keywords)
            found_products = find_product_matches(entry, products)
            self._trigger_event(
                EVENT_NEW_WARNING,
                {
                    "titel": entry["title"],
                    **entry_attributes(entry),
                    # Alle Treffer zusammen, zum einfachen Filtern in Automationen.
                    "watchlist_treffer": found_keywords + found_products,
                    "watchlist_produkte": found_products,
                },
            )
        super()._handle_coordinator_update()
