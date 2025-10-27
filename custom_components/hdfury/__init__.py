"""
Custom integration to integrate HDFury devices with Home Assistant.

For more details about this integration, please refer to
https://github.com/pkern90/hdfury-homeassistant
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import HDFuryApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER
from .coordinator import HDFuryDataUpdateCoordinator
from .data import HDFuryData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HDFuryConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HDFuryConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = HDFuryDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )
    entry.runtime_data = HDFuryData(
        client=HDFuryApiClient(
            host=entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HDFuryConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: HDFuryConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
