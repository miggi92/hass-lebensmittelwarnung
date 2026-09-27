"""Sensor für die betroffenen Bundesländer der jüngsten Meldung."""

from __future__ import annotations

from typing import Any

from .base import LmwSensorBase, shorten


class LmwAffectedStatesSensor(LmwSensorBase):
    """Betroffene Bundesländer der jüngsten Meldung, zusätzlich als Liste."""

    key = "affected_states"
    _attr_translation_key = "affected_states"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("states")) if entry else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self.coordinator.latest
        if entry is None:
            return None
        # Als Liste, damit Automationen z.B. mit "'Bayern' in ..." filtern können.
        return {"bundeslaender": entry.get("affected_states")}
