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
        self._controller = jf.JellyFishController(host, False)
        self.zones = None
        self.patterns = None

    async def async_get_data(self):
        """Get data from the API."""
        try:
            # TODO: extend JF library to retrieve zone states
            self._controller.connectAndGetData()
            self.zones = self._controller.zones
            self.patterns = [p.toFolderAndName() for p in self._controller.patternFiles]
            self.patterns.sort()
            _LOGGER.debug("Zones:\n%s", " ".join(self.zones))
            _LOGGER.debug("Patterns:\n%s", " ".join(self.patterns))
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Failed to connect to Jellyfish Lighting controller at %s", self.host
            )
            raise ex

    async def async_turn_on(self, zones: List[str] = None):
        """Turn one or more zones on. Affects all zones if zone list is None"""
        try:
            self._controller.turnOn(zones)
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Failed to connect to turn on Jellyfish Lighting zone(s) '%s'",
                zones or "[all zones]",
            )
            raise ex

    async def async_turn_off(self, zones: List[str] = None):
        """Turn one or more zones off. Affects all zones if zone list is None"""
        try:
            self._controller.turnOff(zones)
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Failed to connect to turn of Jellyfish Lighting zone(s) '%s'",
                zones or "[all zones]",
            )
            raise ex

    async def async_play_pattern(self, pattern: str, zones: List[str] = None):
        """Turn one or more zones off. Affects all zones if zone list is None"""
        try:
            self._controller.playPattern(pattern, zones)
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Failed to play pattern '%s' on Jellyfish Lighting zone(s) '%s'",
                pattern,
                zones or "[all zones]",
            )
            raise ex
