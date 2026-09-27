"""Kalender mit den gehaltenen Meldungen als ganztägige Termine."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import LmwConfigEntry
from .coordinator import LebensmittelwarnungCoordinator
from .entity import LmwEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([LmwCalendar(entry.runtime_data)])


def _to_event(entry: dict[str, Any]) -> CalendarEvent | None:
    published: datetime | None = entry.get("published")
    if published is None:
        return None
    day = dt_util.as_local(published).date()
    lines = [
        entry.get("product"),
        f"Grund: {entry['reason']}" if entry.get("reason") else None,
        f"Hersteller: {entry['manufacturer']}" if entry.get("manufacturer") else None,
        entry.get("link"),
    ]
    return CalendarEvent(
        start=day,
        end=day + timedelta(days=1),
        summary=entry["title"],
        description="\n".join(line for line in lines if line),
        uid=entry.get("guid"),
    )


class LmwCalendar(LmwEntity, CalendarEntity):
    """Die letzten MAX_ENTRIES Meldungen, je am Tag der Veröffentlichung."""

    _attr_translation_key = "warnings"

    def __init__(self, coordinator: LebensmittelwarnungCoordinator) -> None:
        super().__init__(coordinator, "calendar")

    def _events(self) -> list[CalendarEvent]:
        events = (_to_event(entry) for entry in self.coordinator.data or [])
        return [event for event in events if event is not None]

    @property
    def event(self) -> CalendarEvent | None:
        """Die neueste Meldung, solange ihr Tag noch läuft."""
        today = dt_util.now().date()
        for event in self._events():  # neueste zuerst
            if event.end > today:
                return event
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        start = start_date.date()
        end = end_date.date()
        return [
            event
            for event in self._events()
            if event.start < end and event.end > start
        ]
