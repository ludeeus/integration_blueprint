"""Binary sensor platform for HDFury integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import HDFuryEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HDFuryDataUpdateCoordinator
    from .data import HDFuryConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="signal_detected",
        name="Signal Detected",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:hdmi-port",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: HDFuryConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        HDFuryBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class HDFuryBinarySensor(HDFuryEntity, BinarySensorEntity):
    """HDFury binary_sensor class."""

    def __init__(
        self,
        coordinator: HDFuryDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on (signal detected)."""
        if self.entity_description.key == "signal_detected":
            # Check RX0 status for the currently selected input
            rx_status = self.coordinator.data.get("RX0", "")
            # Signal is detected if RX0 status doesn't contain "no signal"
            return "no signal" not in rx_status.lower() if rx_status else False
        return False
