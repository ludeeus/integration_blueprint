"""Adds config flow for Blueprint."""
import logging
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol
from .api import JellyfishLightingApiClient
from .const import (
    CONF_HOST,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class JellyfishLightingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Jellyfish Lighting"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Only a single instance of the integration is allowed
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_connection(user_input[CONF_HOST])
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )
            else:
                # TODO: use translations
                self._errors[
                    "base"
                ] = "Could not connect to controller at specified host/IP."

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_HOST] = ""

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str}
            ),
            errors=self._errors,
        )

    async def _test_connection(self, host):
        """Return true if host is valid."""
        try:
            _LOGGER.info(
                "Testing connection to Jellyfish Lighting controller at %s...", host
            )
            session = async_create_clientsession(self.hass)
            client = JellyfishLightingApiClient(host, session, self.hass)
            await client.async_get_data()
            _LOGGER.info(
                "Successfully connected to Jellyfish Lighting controller at %s!", host
            )
            return True
        except Exception:  # pylint: disable=broad-except
            return False
