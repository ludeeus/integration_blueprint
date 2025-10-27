"""Config flow for HDFury integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    HDFuryApiClient,
    HDFuryApiClientCommunicationError,
    HDFuryApiClientError,
)
from .const import DOMAIN, LOGGER


class HDFuryFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HDFury."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(host=user_input[CONF_HOST])
            except HDFuryApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except HDFuryApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # Set unique ID to the host address
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"HDFury ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_connection(self, host: str) -> None:
        """Validate we can connect to the HDFury device."""
        client = HDFuryApiClient(
            host=host,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_status()
