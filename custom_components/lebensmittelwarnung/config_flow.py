"""Config Flow: Meldungsart und Bundesland auswählen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import CONF_KEYWORDS, CONF_STATE, CONF_TYPE, DOMAIN, STATES, TYPES
from .entity import device_id
from .watchlist import normalize_keywords


def _select(options: dict[str, str]) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=key, label=name)
                for key, name in options.items()
            ],
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_TYPE, default=defaults.get(CONF_TYPE, "")
            ): _select(TYPES),
            vol.Required(
                CONF_STATE, default=defaults.get(CONF_STATE, "")
            ): _select(STATES),
        }
    )


def _title(type_key: str, state_key: str) -> str:
    return f"Lebensmittelwarnung {TYPES[type_key]} – {STATES[state_key]}"


class LebensmittelwarnungConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ein Eintrag pro Kombination aus Meldungsart und Bundesland."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LmwOptionsFlow:
        return LmwOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            type_key = user_input[CONF_TYPE]
            state_key = user_input[CONF_STATE]
            await self.async_set_unique_id(
                f"{DOMAIN}_{device_id(type_key, state_key)}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=_title(type_key, state_key),
                data={CONF_TYPE: type_key, CONF_STATE: state_key},
            )

        return self.async_show_form(step_id="user", data_schema=_schema({}))

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            type_key = user_input[CONF_TYPE]
            state_key = user_input[CONF_STATE]
            await self.async_set_unique_id(
                f"{DOMAIN}_{device_id(type_key, state_key)}"
            )
            self._abort_if_unique_id_configured()

            return self.async_update_reload_and_abort(
                entry,
                title=_title(type_key, state_key),
                data={CONF_TYPE: type_key, CONF_STATE: state_key},
            )

        return self.async_show_form(
            step_id="reconfigure", data_schema=_schema(entry.data)
        )


class LmwOptionsFlow(OptionsFlowWithReload):
    """Watchlist-Stichwörter pflegen; Speichern lädt den Eintrag neu."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_KEYWORDS: normalize_keywords(user_input.get(CONF_KEYWORDS))
                }
            )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_KEYWORDS,
                    default=self.config_entry.options.get(CONF_KEYWORDS, []),
                ): TextSelector(TextSelectorConfig(multiple=True)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
