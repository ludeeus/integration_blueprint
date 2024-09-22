"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_API_TOKEN, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from ims_envista import IMSEnvista

from .const import CONF_STATION_CONDITIONS, CONF_STATION_ID
from .coordinator import ImsEnvistaUpdateCoordinator
from .data import ImsEnvistaData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ImsEnvistaConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ImsEnvistaConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = ImsEnvistaUpdateCoordinator(hass=hass)

    entry.runtime_data = ImsEnvistaData(
        client=IMSEnvista(
            token=entry.data[CONF_API_TOKEN],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
        station_id=entry.data[CONF_STATION_ID],
        conditions=entry.data[CONF_STATION_CONDITIONS],
    )

    await coordinator.add_station(entry.data[CONF_STATION_ID])

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ImsEnvistaConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ImsEnvistaConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
