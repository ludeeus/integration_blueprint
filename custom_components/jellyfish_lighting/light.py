"""Switch platform for jellyfish-lighting."""
import re
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import LightEntity, LightEntityFeature, ColorMode
from .const import DOMAIN
from . import JellyfishLightingDataUpdateCoordinator
from .entity import JellyfishLightingEntity

_ALL_ZONES = "All Zones"


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup light platform"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    lights = [
        JellyfishLightingLight(coordinator, entry, zone)
        for zone in coordinator.api.zones
    ]
    if len(lights) > 1:
        lights.insert(0, JellyfishLightingLight(coordinator, entry, _ALL_ZONES))
    async_add_devices(lights)


class JellyfishLightingLight(JellyfishLightingEntity, LightEntity):
    """jellyfish-lighting light class."""

    def __init__(
        self,
        coordinator: JellyfishLightingDataUpdateCoordinator,
        entry: ConfigEntry,
        zone: str,
    ) -> None:
        """Initialize."""
        self._attr_supported_features = LightEntityFeature.EFFECT
        self._attr_supported_color_modes = ColorMode.ONOFF
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_icon = "mdi:led-strip-variant"
        self._attr_assumed_state = True  # TODO: Remove once polling is added
        self.zone = zone
        self.api_zone = None if self.zone == _ALL_ZONES else [self.zone]
        self.uid = re.sub("[^a-z0-9]", "_", zone.lower().strip("_"))
        self._attr_has_entity_name = True
        self._attr_name = zone
        self._attr_is_on = False
        self._attr_effect = None
        self._attr_effect_list = coordinator.api.patterns
        super().__init__(coordinator, entry)

    @property
    def unique_id(self):
        return self.uid

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the light."""
        await self.coordinator.api.async_turn_on(self.api_zone)
        self._attr_is_on = True
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the light."""
        await self.coordinator.api.async_turn_off(self.api_zone)
        self._attr_is_on = False
        # await self.coordinator.async_request_refresh()
