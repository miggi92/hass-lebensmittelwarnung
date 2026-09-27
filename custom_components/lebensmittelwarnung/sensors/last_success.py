"""Sensor für den Zeitpunkt des letzten erfolgreichen Feed-Abrufs."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import EntityCategory

from .base import LmwSensorBase


class LmwLastSuccessSensor(LmwSensorBase):
    """Wann der Feed zuletzt tatsächlich abgerufen werden konnte.

    Der Coordinator liefert bei einzelnen Fehlschlägen die alten Meldungen
    weiter; hier sieht man, wie alt dieser Stand wirklich ist.
    """

    key = "last_success"
    _attr_translation_key = "last_success"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        # Bleibt auch verfügbar, wenn der Coordinator aufgegeben hat - gerade
        # dann ist interessant, seit wann nichts mehr ankommt.
        return self.coordinator.last_success is not None

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_success
