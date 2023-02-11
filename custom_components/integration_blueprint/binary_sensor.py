"""Binary sensor platform for integration_blueprint."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)

from .coordinator import BlueprintDataUpdateCoordinator

from .const import DOMAIN
from .entity import IntegrationBlueprintEntity


ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="integration_blueprint",
        name="Integration Blueprint Sensor",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        IntegrationBlueprintBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class IntegrationBlueprintBinarySensor(IntegrationBlueprintEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get("title", "") == "foo"
