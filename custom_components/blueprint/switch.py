"""Switch platform for blueprint."""
from homeassistant.components.switch import SwitchDevice
from . import update_data
from .const import ICON, DOMAIN_DATA


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
        self._name = config["name"]

    async def async_update(self):
        """Update the switch."""
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
        self.attr["user_id"] = updated.get("userId")
        self.attr["title"] = updated.get("title")

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self._status = True

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self._status = False

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
