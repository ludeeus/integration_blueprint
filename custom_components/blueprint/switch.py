"""Switch platform for blueprint."""
from homeassistant.components.switch import SwitchDevice
from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN_DATA, ICON


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup switch platform."""
    async_add_entities([BlueprintBinarySwitch(hass, discovery_info)], True)


class BlueprintBinarySwitch(SwitchDevice):
    """blueprint switch class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._status = False
        self._name = config.get("name", DEFAULT_NAME)

    async def async_update(self):
        """Update the switch."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        updated = self.hass.data[DOMAIN_DATA]["data"].get("data", {})

        # Check the data and update the value.
        self._status = self.hass.data[DOMAIN_DATA]["client"].client.something

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["time"] = str(updated.get("time"))
        self.attr["static"] = updated.get("static")

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        await self.hass.data[DOMAIN_DATA]["client"].client.change_something(True)

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        await self.hass.data[DOMAIN_DATA]["client"].client.change_something(False)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
