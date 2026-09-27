"""Sensor für die Verpackungseinheit der jüngsten Meldung."""

from __future__ import annotations

from .base import LmwSensorBase, shorten


class LmwPackageSensor(LmwSensorBase):
    """Verpackungseinheit der jüngsten Meldung."""

    key = "package"
    _attr_translation_key = "package"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("package")) if entry else None
