"""Config flow for the ENGIE Belgium integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import slugify

from .api import (
    AuthFlowState,
    EngieBeApiClient,
    EngieBeApiClientAuthenticationError,
    EngieBeApiClientCommunicationError,
    EngieBeApiClientError,
    EngieBeApiClientMfaError,
)
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CUSTOMER_NUMBER,
    CONF_MFA_METHOD,
    CONF_REFRESH_TOKEN,
    CONF_UPDATE_INTERVAL,
    DEFAULT_CLIENT_ID,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    LOGGER,
    MAX_UPDATE_INTERVAL_HOURS,
    MFA_METHOD_EMAIL,
    MFA_METHOD_SMS,
    MIN_UPDATE_INTERVAL_HOURS,
)


class EngieBeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for ENGIE Belgium."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow handler."""
        super().__init__()
        self._user_input: dict[str, Any] = {}
        self._auth_flow_state: AuthFlowState | None = None
        self._client: EngieBeApiClient | None = None

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,  # noqa: ARG004
    ) -> EngieBeOptionsFlowHandler:
        """Return the options flow handler."""
        return EngieBeOptionsFlowHandler()

    # ------------------------------------------------------------------
    # Step 1: credentials + customer number + MFA method
    # ------------------------------------------------------------------

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial credentials step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._user_input = user_input
            try:
                self._client = EngieBeApiClient(
                    session=async_get_clientsession(self.hass),
                    client_id=user_input.get(CONF_CLIENT_ID, DEFAULT_CLIENT_ID),
                )
                self._auth_flow_state = await self._client.async_start_authentication(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    mfa_method=user_input.get(CONF_MFA_METHOD, MFA_METHOD_SMS),
                )
            except EngieBeApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                errors["base"] = "auth"
            except EngieBeApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except EngieBeApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                mfa_method = user_input.get(CONF_MFA_METHOD, MFA_METHOD_SMS)
                if mfa_method == MFA_METHOD_EMAIL:
                    return await self.async_step_mfa_email()
                return await self.async_step_mfa_sms()

        customer_default = (user_input or {}).get(CONF_CUSTOMER_NUMBER, vol.UNDEFINED)
        if isinstance(customer_default, str):
            customer_default = customer_default.removeprefix("00")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Required(
                        CONF_CUSTOMER_NUMBER,
                        default=customer_default,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            prefix="00",
                        ),
                    ),
                    vol.Required(
                        CONF_CLIENT_ID,
                        default=(user_input or {}).get(
                            CONF_CLIENT_ID, DEFAULT_CLIENT_ID
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_MFA_METHOD,
                        default=(user_input or {}).get(CONF_MFA_METHOD, MFA_METHOD_SMS),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=MFA_METHOD_SMS,
                                    label="SMS",
                                ),
                                selector.SelectOptionDict(
                                    value=MFA_METHOD_EMAIL,
                                    label="Email",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        ),
                    ),
                },
            ),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2a: SMS MFA code entry
    # ------------------------------------------------------------------

    async def async_step_mfa_sms(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the SMS MFA code entry step."""
        return await self._handle_mfa_step(
            step_id="mfa_sms",
            mfa_method=MFA_METHOD_SMS,
            user_input=user_input,
        )

    # ------------------------------------------------------------------
    # Step 2b: email MFA code entry
    # ------------------------------------------------------------------

    async def async_step_mfa_email(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the email MFA code entry step."""
        return await self._handle_mfa_step(
            step_id="mfa_email",
            mfa_method=MFA_METHOD_EMAIL,
            user_input=user_input,
        )

    # ------------------------------------------------------------------
    # Shared MFA handler
    # ------------------------------------------------------------------

    async def _handle_mfa_step(
        self,
        *,
        step_id: str,
        mfa_method: str,
        user_input: dict[str, Any] | None,
    ) -> config_entries.ConfigFlowResult:
        """Handle MFA code entry for both SMS and email methods."""
        errors: dict[str, str] = {}

        if user_input is not None and self._auth_flow_state is not None:
            try:
                (
                    access_token,
                    refresh_token,
                ) = await self._client.async_complete_authentication(
                    flow_state=self._auth_flow_state,
                    mfa_code=user_input["code"],
                    mfa_method=mfa_method,
                )
            except EngieBeApiClientMfaError as exception:
                LOGGER.warning(exception)
                errors["base"] = "invalid_mfa_code"
            except EngieBeApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                errors["base"] = "auth"
            except EngieBeApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except EngieBeApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                self._auth_flow_state = None

                await self.async_set_unique_id(slugify(self._user_input[CONF_USERNAME]))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._user_input[CONF_USERNAME],
                    data={
                        CONF_USERNAME: self._user_input[CONF_USERNAME],
                        CONF_PASSWORD: self._user_input[CONF_PASSWORD],
                        CONF_CUSTOMER_NUMBER: (
                            f"00{self._user_input[CONF_CUSTOMER_NUMBER]}"
                        ),
                        CONF_CLIENT_ID: self._user_input.get(
                            CONF_CLIENT_ID, DEFAULT_CLIENT_ID
                        ),
                        CONF_ACCESS_TOKEN: access_token,
                        CONF_REFRESH_TOKEN: refresh_token,
                    },
                )

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required("code"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=errors,
        )


class EngieBeOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for ENGIE Belgium."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL,
                            DEFAULT_UPDATE_INTERVAL_HOURS,
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_UPDATE_INTERVAL_HOURS,
                            max=MAX_UPDATE_INTERVAL_HOURS,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="hours",
                        ),
                    ),
                },
            ),
        )
