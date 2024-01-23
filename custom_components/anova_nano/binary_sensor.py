"""Binary sensor platform for anova_nano."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .coordinator import AnovaNanoDataUpdateCoordinator
from .entity import AnovaNanoDescriptionEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="water_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    BinarySensorEntityDescription(
        key="water_leak",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        AnovaNanoBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AnovaNanoBinarySensor(AnovaNanoDescriptionEntity, BinarySensorEntity):
    """anova_nano binary_sensor class."""

    def __init__(
        self,
        coordinator: AnovaNanoDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get("title", "") == "foo"
