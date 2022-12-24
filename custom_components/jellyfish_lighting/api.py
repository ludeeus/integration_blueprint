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
        self.host = host
        self._session = session
        self._hass = hass
        self._controller = jf.JellyFishController(host, True)
        self.zones = None
        self.patterns = None

    async def async_get_data(self):
        """Get data from the API."""
        try:
            _LOGGER.debug("In apy.py async_get_data")
            # TODO: extend JF library to retrieve zone states
            self._hass.loop.set_debug(True)
            await self._hass.async_add_executor_job(self._controller.connectAndGetData)
            self.zones = self._controller.zones
            self.patterns = list(
                set([p.toFolderAndName() for p in self._controller.patternFiles])
            )
            self.patterns.sort()
            _LOGGER.debug("Zones:\n%s", " ".join(self.zones))
            _LOGGER.debug("Patterns:\n%s", " ".join(self.patterns))
            # TODO: Add/remove entities if zones have changed?
        except BaseException as ex:  # pylint: disable=broad-except
            msg = f"Failed to connect and get data from Jellyfish Lighting controller at {self.host}"
            _LOGGER.exception(msg)
            raise Exception(msg) from ex

    async def async_turn_on(self, zones: List[str] = None):
        """Turn one or more zones on. Affects all zones if zone list is None"""
        try:
            self._controller.turnOn(zones)
        except BaseException as ex:  # pylint: disable=broad-except
            msg = f"Failed to connect to turn on Jellyfish Lighting zone(s) '{zones or '[all zones]'}'"
            _LOGGER.exception(msg)
            raise Exception(msg) from ex

    async def async_turn_off(self, zones: List[str] = None):
        """Turn one or more zones off. Affects all zones if zone list is None"""
        try:
            self._controller.turnOff(zones)
        except BaseException as ex:  # pylint: disable=broad-except
            msg = f"Failed to connect to turn off Jellyfish Lighting zone(s) '{zones or '[all zones]'}'"
            _LOGGER.exception(msg)
            raise Exception(msg) from ex

    async def async_play_pattern(self, pattern: str, zones: List[str] = None):
        """Turn one or more zones off. Affects all zones if zone list is None"""
        try:
            self._controller.playPattern(pattern, zones)
        except BaseException as ex:  # pylint: disable=broad-except
            msg = f"Failed to play pattern '{pattern}' on Jellyfish Lighting zone(s) '{zones or '[all zones]'}'"
            _LOGGER.exception(msg)
            raise Exception(msg) from ex
