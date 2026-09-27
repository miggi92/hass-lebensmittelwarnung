"""Sensor für die Anzahl der Meldungen im Feed."""

from __future__ import annotations

from typing import Any

from homeassistant.const import EntityCategory

from .base import LmwSensorBase, entry_attributes


class LmwCountSensor(LmwSensorBase):
    """Anzahl der aktuell im Feed enthaltenen Meldungen."""

    key = "count"
    _attr_translation_key = "count"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {
            "meldungen": [
                {"titel": entry["title"], **entry_attributes(entry)}
                for entry in self.coordinator.data or []
            ]
        }
