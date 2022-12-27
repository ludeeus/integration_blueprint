"""Sample API Client."""
import logging
from typing import List
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import jellyfishlightspy as jf

TIMEOUT = 10
_LOGGER: logging.Logger = logging.getLogger(__package__)


class JellyfishLightingApiClient:
    """API Client for Jellyfish Lighting"""

    def __init__(
        self, host: str, config_entry: ConfigEntry, hass: HomeAssistant
    ) -> None:
        """Initialize API client."""
        self.host = host
        self._config_entry = config_entry
        self._hass = hass
        self._controller = jf.JellyFishController(host, False)
        self.zones = None
        self.states = None
        self.patterns = None

    async def async_get_data(self):
        """Get data from the API."""
        try:
            _LOGGER.debug("Getting refreshed data for Jellyfish Lighting")
            await self._hass.async_add_executor_job(self._controller.connectAndGetData)
            # TODO: Check if zones have changed. Reload if so.
            # if self.zones is not None and set(self.zones) != set(self._controller.zones):
            #     # do the things
            #     return
            self.zones = self._controller.zones
            _LOGGER.debug("Zones: %s", ", ".join(self.zones))
            # Get the state of each zone
            self.states = {}
            for zone in self.zones:
                state = await self._hass.async_add_executor_job(
                    self._controller.getRunPattern, zone
                )
                self.states[zone] = (state.state, state.file)
            _LOGGER.debug("States: %s", self.states)
            # Get the list of available patterns
            self.patterns = list(
                set([p.toFolderAndName() for p in self._controller.patternFiles])
            )
            self.patterns.sort()
            _LOGGER.debug("Patterns: %s", ", ".join(self.patterns))
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
