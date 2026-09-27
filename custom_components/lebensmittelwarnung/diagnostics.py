"""Diagnosedaten zum Download in der HA-Oberfläche."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import LmwConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LmwConfigEntry
) -> dict[str, Any]:
    """Coordinator-Zustand und geparste Meldungen. Enthält nichts Geheimes."""
    coordinator = entry.runtime_data
    return {
        "entry": {"data": dict(entry.data), "title": entry.title},
        "coordinator": {
            "feed_url": coordinator.feed_url,
            "last_update_success": coordinator.last_update_success,
            "last_success": coordinator.last_success,
            "consecutive_failures": coordinator._consecutive_failures,  # noqa: SLF001
            "last_exception": repr(coordinator.last_exception)
            if coordinator.last_exception
            else None,
        },
        "data": coordinator.data,
    }
