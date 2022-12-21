"""Sample API Client."""
import logging
from typing import List
import aiohttp
from homeassistant.core import HomeAssistant
import jellyfishlightspy as jf

TIMEOUT = 10
_LOGGER: logging.Logger = logging.getLogger(__package__)


class JellyfishLightingApiClient:
    """API Client for Jellyfish Lighting"""

    def __init__(
        self, host: str, session: aiohttp.ClientSession, hass: HomeAssistant
    ) -> None:
        """Initialize API client."""
        self._host = host
        self._session = session
        self._hass = hass
        self._controller = jf.JellyFishController(self._host, True)

    async def async_get_data(self):
        """Get data from the API."""
        try:
            # TODO: extend JF library to retrieve zone states
            self._controller.connectAndGetData()
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Failed to connect to Jellyfish Lighting controller at %s", self._host
            )
            raise ex

    async def async_turn_on(self, zones: List[str] = None):
        """Turn one or more zones on. Affects all zones if zone list is None"""
        self._controller.turnOn(zones)

    async def async_turn_off(self, zones: List[str] = None):
        """Turn one or more zones off. Affects all zones if zone list is None"""
        self._controller.turnOff(zones)
