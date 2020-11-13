"""Sensor platform for Blueprint."""
from custom_components.blueprint.const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from custom_components.blueprint.entity import BlueprintEntity

from homeassistant.util import slugify


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([BlueprintSensor(coordinator, entry)])


class BlueprintSensor(BlueprintEntity):
    """blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        # slugify the state to allow translation
        return slugify(self.coordinator.data.get("static"))

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "blueprint__custom_device_class"
