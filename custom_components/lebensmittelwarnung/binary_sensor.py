"""Binary-Sensoren mit Zeitfenster: aktuelle Warnung und Watchlist-Treffer."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from . import LmwConfigEntry
from .entity import LmwEntity
from .watchlist import WATCHLIST_WINDOW, find_matches

RECENT_WINDOW = timedelta(hours=24)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [LmwRecentWarning(coordinator), LmwWatchlistMatch(coordinator)]
    )


class LmwTimedBinarySensor(LmwEntity, BinarySensorEntity):
    """Basis für Sensoren, deren Zustand an einem Zeitpunkt kippt.

    Ohne eigenen Timer bliebe der Sensor bis zum nächsten erfolgreichen
    Feed-Poll (stündlich, oder später bei Poll-Fehlern) fälschlicherweise
    "an".
    """

    def __init__(self, coordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._expiry_unsub = None

    def _next_expiry(self) -> datetime | None:
        """Nächster Zeitpunkt, an dem sich der Zustand ändern kann."""
        raise NotImplementedError

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._schedule_expiry()

    async def async_will_remove_from_hass(self) -> None:
        self._cancel_expiry()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._schedule_expiry()
        super()._handle_coordinator_update()

    @callback
    def _cancel_expiry(self) -> None:
        if self._expiry_unsub is not None:
            self._expiry_unsub()
            self._expiry_unsub = None

    @callback
    def _schedule_expiry(self) -> None:
        self._cancel_expiry()
        expires_at = self._next_expiry()
        if expires_at is None or expires_at <= dt_util.utcnow():
            return

        @callback
        def _expire(_now: datetime) -> None:
            self._expiry_unsub = None
            # Es können mehrere Zeitpunkte anstehen (Watchlist), also neu planen.
            self._schedule_expiry()
            self.async_write_ha_state()

        self._expiry_unsub = async_track_point_in_utc_time(
            self.hass, _expire, expires_at
        )


class LmwRecentWarning(LmwTimedBinarySensor):
    """An, solange die jüngste Meldung keine 24 Stunden alt ist."""

    _attr_translation_key = "recent_warning"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "recent")

    @property
    def is_on(self) -> bool:
        entry = self.coordinator.latest
        published = entry.get("published") if entry else None
        if published is None:
            return False
        return dt_util.utcnow() - published < RECENT_WINDOW

    def _next_expiry(self) -> datetime | None:
        entry = self.coordinator.latest
        published = entry.get("published") if entry else None
        return published + RECENT_WINDOW if published else None


class LmwWatchlistMatch(LmwTimedBinarySensor):
    """An, wenn eine Meldung der letzten 7 Tage ein Stichwort enthält."""

    _attr_translation_key = "watchlist"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "watchlist")

    def _matches(self) -> list[tuple[dict[str, Any], list[str]]]:
        keywords = self.coordinator.keywords
        if not keywords:
            return []
        since = dt_util.utcnow() - WATCHLIST_WINDOW
        result = []
        for entry in self.coordinator.data or []:
            published = entry.get("published")
            if published is None or published <= since:
                continue
            if found := find_matches(entry, keywords):
                result.append((entry, found))
        return result

    @property
    def is_on(self) -> bool:
        return bool(self._matches())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "stichwoerter": self.coordinator.keywords,
            "treffer": [
                {
                    "titel": entry["title"],
                    "link": entry["link"],
                    "stichwoerter": found,
                    "veroeffentlicht": entry.get("published"),
                }
                for entry, found in self._matches()
            ],
        }

    def _next_expiry(self) -> datetime | None:
        # Die älteste noch passende Meldung fällt als erste aus dem Fenster.
        expiries = [
            entry["published"] + WATCHLIST_WINDOW for entry, _ in self._matches()
        ]
        return min(expiries) if expiries else None
