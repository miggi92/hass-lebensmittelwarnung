"""Config Flow: Bundesland auswählen."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_STATE, DOMAIN, STATES


class LebensmittelwarnungConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ein Eintrag pro Bundesland."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            state_key = user_input[CONF_STATE]
            await self.async_set_unique_id(f"{DOMAIN}_{state_key or 'alle'}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Lebensmittelwarnung {STATES[state_key]}",
                data={CONF_STATE: state_key},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATE, default=""): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=key, label=name)
                            for key, name in STATES.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)