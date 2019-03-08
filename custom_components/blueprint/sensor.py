"""Sensor platform for blueprint"""
from homeassistant.helpers.entity import Entity
from . import update_data
from .const import *  # pylint: disable=wildcard-import, unused-wildcard-import

ICON = "mdi:format-quote-close"


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([blueprintSensor(hass)], True)


class blueprintSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass):
        self.hass = hass
        self._state = None

    async def async_update(self):
        """Update the sensor."""
        await update_data(self.hass)
        updated = self.hass.data[DOMAIN_DATA].get("compliment")
        if updated is None:
            updated = self._state
        self._state = updated.capitalize()

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
