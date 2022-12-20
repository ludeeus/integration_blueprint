"""Switch platform for jellyfish-lighting."""
from homeassistant.components.light import LightEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, LIGHT
from .entity import JellyfishLightingEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup light platform"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([JellyfishLightingLight(coordinator, entry)])


class JellyfishLightingLight(JellyfishLightingEntity, LightEntity):
    """jellyfish-lighting light class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the light."""
        await self.coordinator.api.async_set_title("on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the light."""
        await self.coordinator.api.async_set_title("off")
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DEFAULT_NAME}_{LIGHT}"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get("title", "") == "on"
