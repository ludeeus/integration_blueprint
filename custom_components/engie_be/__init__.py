"""Custom integration to integrate ENGIE Belgium with Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .api import EngieBeApiClient, EngieBeApiClientError
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_REFRESH_TOKEN,
    DEFAULT_CLIENT_ID,
    LOGGER,
    TOKEN_REFRESH_INTERVAL_SECONDS,
)
from .coordinator import EngieBeDataUpdateCoordinator
from .data import EngieBeData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import EngieBeConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EngieBeConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    client = EngieBeApiClient(
        session=async_get_clientsession(hass),
        client_id=entry.data.get(CONF_CLIENT_ID, DEFAULT_CLIENT_ID),
        access_token=entry.data.get(CONF_ACCESS_TOKEN),
        refresh_token=entry.data.get(CONF_REFRESH_TOKEN),
    )

    coordinator = EngieBeDataUpdateCoordinator(hass=hass, config_entry=entry)

    entry.runtime_data = EngieBeData(
        client=client,
        coordinator=coordinator,
        last_options=dict(entry.options),
    )

    # Do an initial token refresh so we have a valid access token
    try:
        new_access, new_refresh = await client.async_refresh_token()
        _persist_tokens(hass, entry, new_access, new_refresh)
        entry.runtime_data.authenticated = True
    except EngieBeApiClientError:
        LOGGER.warning("Initial token refresh failed; will retry on next interval")
        entry.runtime_data.authenticated = False

    # Set up recurring token refresh (every 60 seconds)
    async def _refresh_token_callback(_now: object) -> None:
        """Refresh the access token periodically."""
        try:
            new_access, new_refresh = await client.async_refresh_token()
            _persist_tokens(hass, entry, new_access, new_refresh)
            entry.runtime_data.authenticated = True
            LOGGER.debug("Token refreshed successfully")
        except EngieBeApiClientError:
            entry.runtime_data.authenticated = False
            LOGGER.warning("Scheduled token refresh failed; will retry")
        # Poke the coordinator so binary_sensor picks up the new auth state
        coordinator.async_set_updated_data(coordinator.data)

    cancel_refresh = async_track_time_interval(
        hass,
        _refresh_token_callback,
        timedelta(seconds=TOKEN_REFRESH_INTERVAL_SECONDS),
    )
    entry.async_on_unload(cancel_refresh)

    # Fetch initial data and forward platforms
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: EngieBeConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: EngieBeConfigEntry,
) -> None:
    """Reload config entry only when options change (not on token rotation)."""
    if dict(entry.options) != entry.runtime_data.last_options:
        await hass.config_entries.async_reload(entry.entry_id)


def _persist_tokens(
    hass: HomeAssistant,
    entry: EngieBeConfigEntry,
    access_token: str,
    refresh_token: str,
) -> None:
    """Persist refreshed tokens to the config entry data."""
    updated_data = {**entry.data}
    updated_data[CONF_ACCESS_TOKEN] = access_token
    updated_data[CONF_REFRESH_TOKEN] = refresh_token
    hass.config_entries.async_update_entry(entry, data=updated_data)
