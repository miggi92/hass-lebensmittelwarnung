"""Sensor für die Anzahl der Meldungen der letzten 7 Tage."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.util import dt as dt_util

from .base import LmwSensorBase

RECENT_COUNT_WINDOW = timedelta(days=7)


class LmwRecentCountSensor(LmwSensorBase):
    """Meldungen, die in den letzten 7 Tagen veröffentlicht wurden.

    Gezählt wird nur, was der Coordinator hält (MAX_ENTRIES). Bei sehr vielen
    Meldungen pro Woche ist das also eine Untergrenze.
    """

    key = "recent_count"
    _attr_translation_key = "recent_count"

    @property
    def native_value(self) -> int:
        since = dt_util.utcnow() - RECENT_COUNT_WINDOW
        return sum(
            1
            for entry in self.coordinator.data or []
            if entry.get("published") is not None and entry["published"] >= since
        )
