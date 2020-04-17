"""Sensor platform for blueprint."""
from custom_components.blueprint.const import DEFAULT_NAME, DOMAIN, ICON
from custom_components.blueprint.entity import BlueprintEntity


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_devices([BlueprintSensor(coordinator, config_entry)])


class BlueprintSensor(BlueprintEntity):
    """blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return DEFAULT_NAME

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("static")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
