"""Coordinator: holt den RSS-Feed und hält die geparsten Meldungen."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import feedparser

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DEFAULT_SCAN_INTERVAL, FEED_URL, STATES, TYPES, USER_AGENT
from .parser import parse_entry

_LOGGER = logging.getLogger(__name__)

MAX_ENTRIES = 10

# So viele Polls hintereinander dürfen fehlschlagen, bevor die Entities auf
# "unavailable" gehen. Der Server bricht Verbindungen gelegentlich ab (oder
# DNS hakt kurz); ohne Toleranz springt dann jeder Sensor für eine Stunde auf
# "unavailable" und wieder zurück, was Automationen doppelt auslöst.
MAX_CONSECUTIVE_FAILURES = 3


class LebensmittelwarnungCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Ruft den Feed ab und liefert eine Liste geparster Meldungen."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        type_key: str,
        state_key: str,
    ) -> None:
        self.type_key = type_key
        self.type_name = TYPES.get(type_key, type_key)
        self.state_key = state_key
        self.state_name = STATES.get(state_key, state_key)
        self._session = async_get_clientsession(hass)
        self._consecutive_failures = 0
        # Zeitpunkt des letzten tatsächlich erfolgreichen Abrufs. Wegen der
        # Fehlertoleranz unten ist last_update_success dafür nicht aussagekräftig.
        self.last_success: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"Lebensmittelwarnung {self.type_name} – {self.state_name}",
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    @property
    def feed_url(self) -> str:
        url = FEED_URL
        if self.type_key:
            url += f"&type={self.type_key}"
        if self.state_key:
            url += f"&state={self.state_key}"
        return url

    @property
    def latest(self) -> dict[str, Any] | None:
        """Die jüngste Meldung, falls vorhanden."""
        return self.data[0] if self.data else None

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            entries = await self._async_fetch_entries()
        except UpdateFailed as err:
            self._consecutive_failures += 1
            if (
                self.data is not None
                and self._consecutive_failures < MAX_CONSECUTIVE_FAILURES
            ):
                _LOGGER.warning(
                    "%s (Versuch %s/%s), behalte letzte bekannte Meldungen",
                    err,
                    self._consecutive_failures,
                    MAX_CONSECUTIVE_FAILURES,
                )
                return self.data
            raise

        self._consecutive_failures = 0
        self.last_success = dt_util.utcnow()
        return entries

    async def _async_fetch_entries(self) -> list[dict[str, Any]]:
        try:
            response = await self._session.get(
                self.feed_url, headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            raw = await response.text()
        except Exception as err:  # noqa: BLE001 - alles wird zu UpdateFailed
            raise UpdateFailed(f"Feed konnte nicht geladen werden: {err}") from err

        # feedparser ist synchron und rechenintensiv genug für den Executor.
        parsed = await self.hass.async_add_executor_job(feedparser.parse, raw)

        if parsed.bozo and not parsed.entries:
            raise UpdateFailed(f"Feed nicht lesbar: {parsed.bozo_exception}")

        return [parse_entry(entry) for entry in parsed.entries[:MAX_ENTRIES]]