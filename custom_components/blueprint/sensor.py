"""Sensor platform for blueprint."""
from homeassistant.helpers.entity import Entity
from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN_DATA, ICON


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([BlueprintSensor(hass, discovery_info)], True)


class BlueprintSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = config.get("name", DEFAULT_NAME)

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        updated = self.hass.data[DOMAIN_DATA]["data"].get("data", {})

        # Check the data and update the value.
        if updated.get("static") is None:
            self._state = self._status
        else:
            self._state = updated.get("static")

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["time"] = str(updated.get("time"))
        self.attr["none"] = updated.get("none")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
