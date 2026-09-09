"""Gemeinsame Basis für alle Entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LebensmittelwarnungCoordinator


class LmwEntity(CoordinatorEntity[LebensmittelwarnungCoordinator]):
    """Hängt alle Entities an ein gemeinsames Gerät."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: LebensmittelwarnungCoordinator, key: str
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        state_key = coordinator.state_key or "alle"
        self._attr_unique_id = f"{DOMAIN}_{state_key}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, state_key)},
            name=f"Lebensmittelwarnung {coordinator.state_name}",
            manufacturer="BVL / Bundesländer",
            model="lebensmittelwarnung.de",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.lebensmittelwarnung.de/",
        )