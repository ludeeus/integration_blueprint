"""Sensor platform for powerpal."""
from homeassistant.components.sensor import (
    SensorEntity,
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY

from .const import NAME, DOMAIN, ICON, CONF_DEVICE_ID, ATTRIBUTION


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        PowerpalTotalConsumptionSensor(coordinator, entry),
        PowerpalLiveConsumptionSensor(coordinator, entry),
    ]
    async_add_devices(entities)


class PowerpalSensor(CoordinatorEntity):
    """Powerpal Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the native unit of measurement."""
        return ENERGY_KILO_WATT_HOUR

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_ENERGY

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": NAME,
            "model": self.config_entry.data[CONF_DEVICE_ID],
            "manufacturer": NAME,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.config_entry.data[CONF_DEVICE_ID],
            "integration": DOMAIN,
        }

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON


class PowerpalTotalConsumptionSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Total Consumption"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-total-{self.config_entry.entry_id}"

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get("total_watt_hours") / 1000


class PowerpalLiveConsumptionSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Live Consumption"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-live-{self.config_entry.entry_id}"

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return STATE_CLASS_MEASUREMENT

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (self.coordinator.data.get("last_reading_watt_hours") * 60) / 1000
