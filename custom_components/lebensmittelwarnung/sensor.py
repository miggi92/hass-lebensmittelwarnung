"""Sensoren für die jüngste Meldung."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LmwConfigEntry
from .entity import LmwEntity

# Zustände sind auf 255 Zeichen begrenzt. Felder wie "Haltbarkeit" oder
# "Produktbezeichnung" listen bei Sammelrückrufen schnell mehr auf.
MAX_STATE_LENGTH = 255


def _shorten(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\n", " | ")
    return text[:MAX_STATE_LENGTH]


# Die Gründe sind ein fester Satz von sieben Werten (siehe Filter auf
# lebensmittelwarnung.de). Bei Mehrfachnennungen gewinnt der erste Treffer.
REASON_ICONS: dict[str, str] = {
    "Krankheitserreger": "mdi:bacteria-outline",
    "Allergene": "mdi:peanut-off-outline",
    "Fremdkörper": "mdi:magnet-on",
    "Gesundheitsschädliche Substanz": "mdi:skull-crossbones-outline",
    "Rückstände und Kontaminanten": "mdi:flask-outline",
    "Irreführung und Täuschung": "mdi:eye-off-outline",
    "Sonstige Gründe": "mdi:dots-horizontal-circle-outline",
}
DEFAULT_REASON_ICON = "mdi:alert-octagon-outline"


@dataclass(frozen=True, kw_only=True)
class LmwSensorDescription(SensorEntityDescription):
    """Sensor mit eigener Wertfunktion."""

    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


SENSORS: tuple[LmwSensorDescription, ...] = (
    LmwSensorDescription(
        key="latest",
        translation_key="latest",
        value_fn=lambda entry: entry["title"],
        attr_fn=lambda entry: {
            "link": entry["link"],
            "grund": entry.get("reason"),
            "gruende": entry.get("reasons"),
            "charge": entry.get("batch"),
            "haltbarkeit": entry.get("expiry"),
            "produkt": entry.get("product"),
            "verpackungseinheit": entry.get("package"),
            "hersteller": entry.get("manufacturer"),
            "bild": entry.get("image"),
            "bilder": entry.get("images"),
            "veroeffentlicht": entry.get("published"),
        },
    ),
    LmwSensorDescription(
        key="reason",
        translation_key="reason",
        value_fn=lambda entry: entry.get("reason"),
        attr_fn=lambda entry: {"gruende": entry.get("reasons")},
    ),
    LmwSensorDescription(
        key="batch",
        translation_key="batch",
        value_fn=lambda entry: entry.get("batch"),
    ),
    LmwSensorDescription(
        key="expiry",
        translation_key="expiry",
        value_fn=lambda entry: entry.get("expiry"),
    ),
    LmwSensorDescription(
        key="product",
        translation_key="product",
        value_fn=lambda entry: entry.get("product"),
    ),
    LmwSensorDescription(
        key="manufacturer",
        translation_key="manufacturer",
        value_fn=lambda entry: entry.get("manufacturer"),
    ),
    LmwSensorDescription(
        key="published",
        translation_key="published",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda entry: entry.get("published"),
    ),
    LmwSensorDescription(
        key="count",
        translation_key="count",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda entry: None,  # wird im Sensor überschrieben
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        LmwSensor(coordinator, description) for description in SENSORS
    )


class LmwSensor(LmwEntity, SensorEntity):
    """Ein Feld der jüngsten Meldung."""

    entity_description: LmwSensorDescription

    def __init__(self, coordinator, description: LmwSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        if self.entity_description.key == "count":
            return len(self.coordinator.data or [])

        entry = self.coordinator.latest
        if entry is None:
            return None

        value = self.entity_description.value_fn(entry)
        if self.entity_description.device_class is SensorDeviceClass.TIMESTAMP:
            return value
        return _shorten(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self.coordinator.latest
        if entry is None or self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(entry)

    @property
    def icon(self) -> str | None:
        """Beim Grund-Sensor richtet sich das Icon nach der Art der Meldung.

        Alle übrigen Icons kommen aus icons.json; None bedeutet dort:
        Standard verwenden.
        """
        if self.entity_description.key != "reason":
            return None

        entry = self.coordinator.latest
        if entry is None:
            return DEFAULT_REASON_ICON

        for reason in entry.get("reasons") or []:
            if icon := REASON_ICONS.get(reason):
                return icon
        return DEFAULT_REASON_ICON