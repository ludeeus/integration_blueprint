"""Switch platform for jellyfish-lighting."""
from homeassistant.components.light import LightEntity

from .const import DOMAIN
from . import JellyfishLightingDataUpdateCoordinator
from .entity import JellyfishLightingEntity

_ICON = "mdi:led-strip-variant"


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup light platform"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # TODO: Add light per zone, and one to control them all
    async_add_devices([JellyfishLightingLight(coordinator, entry)])


class JellyfishLightingLight(JellyfishLightingEntity, LightEntity):
    """jellyfish-lighting light class."""

    def __init__(
        self, coordinator: JellyfishLightingDataUpdateCoordinator, entity: LightEntity
    ) -> None:
        """Initialize."""
        self._on = False
        super().__init__(coordinator, entity)

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the light."""
        await self.coordinator.api.async_turn_on()
        self._on = True
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the light."""
        await self.coordinator.api.async_turn_off()
        self._on = False
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the light."""
        return f"{DOMAIN}_all_zones"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return _ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._on
