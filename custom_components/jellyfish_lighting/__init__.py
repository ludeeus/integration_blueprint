"""
Custom integration to integrate Jellyfish Lighting with Home Assistant.
"""
from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import device_registry as dr

from .api import JellyfishLightingApiClient

from .const import (
    CONF_HOST,
    DOMAIN,
    NAME,
    LIGHT,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=15)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(
    hass: HomeAssistant, config: Config
):  # pylint: disable=unused-argument
    """Setting up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    _LOGGER.info("Setting up Jellyfish Lighting integration")
    _LOGGER.debug(
        "async_setup_entry config entry is: %s",
        {
            "entry_id": entry.entry_id,
            "unique_id": entry.unique_id,
            "domain": entry.domain,
            "title": entry.title,
            "data": entry.data,
        },
    )
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data.get(CONF_HOST)
    client = JellyfishLightingApiClient(host, entry, hass)
    coordinator = JellyfishLightingDataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        manufacturer=NAME,
        name=NAME,
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, LIGHT))

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


class JellyfishLightingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: JellyfishLightingApiClient) -> None:
        """Initialize."""
        _LOGGER.debug("in data coordinator __init__")
        self.api = client
        self.platforms = []
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        _LOGGER.debug("in data coordinator async_update_data")
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.info("Unloading Jellyfish Lighting integration")
    # coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = await hass.config_entries.async_forward_entry_unload(entry, LIGHT)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.info("Reloading Jellyfish Lighting integration")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
