"""Binary sensor platform for blueprint."""
from homeassistant.components.binary_sensor import BinarySensorDevice
from .const import ATTRIBUTION, BINARY_SENSOR_DEVICE_CLASS, DEFAULT_NAME, DOMAIN_DATA


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup binary_sensor platform."""
    async_add_entities([BlueprintBinarySensor(hass, discovery_info)], True)


class BlueprintBinarySensor(BinarySensorDevice):
    """blueprint binary_sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._status = False
        self._name = config.get("name", DEFAULT_NAME)

    async def async_update(self):
        """Update the binary_sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        updated = self.hass.data[DOMAIN_DATA]["data"].get("data", {})

        # Check the data and update the value.
        if updated.get("bool_on") is None:
            self._status = self._status
        else:
            self._status = updated.get("bool_on")

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["time"] = str(updated.get("time"))
        self.attr["static"] = updated.get("static")

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
