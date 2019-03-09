"""Binary ensor platform for blueprint."""
from homeassistant.components.binary_sensor import BinarySensorDevice
from . import update_data
from .const import (
    BINARY_SENSOR_DEVICE_CLASS, DOMAIN_DATA, SENSOR_ICON)


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([BlueprintBinarySensor(hass, discovery_info)], True)


class BlueprintBinarySensor(BinarySensorDevice):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._status = False
        self._name = config['name']

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await update_data(self.hass)

        # Get new data (if any)
        updated = self.hass.data[DOMAIN_DATA]

        # Check the data and update the value.
        if updated.get("completed") is None:
            self._status = self._status
        else:
            self._status = updated.get("completed")

        # Set/update attributes
        self.attr['user_id'] = updated.get('userId')
        self.attr['title'] = updated.get('title')

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
