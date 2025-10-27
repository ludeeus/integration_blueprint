"""Sensor platform for HDFury integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import INPUT_NAMES
from .entity import HDFuryEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HDFuryDataUpdateCoordinator
    from .data import HDFuryConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="current_input",
        name="Current Input",
        icon="mdi:hdmi-port",
    ),
    SensorEntityDescription(
        key="rx0_status",
        name="RX0 Status",
        icon="mdi:video-input-hdmi",
    ),
    SensorEntityDescription(
        key="rx1_status",
        name="RX1 Status",
        icon="mdi:video-input-hdmi",
    ),
    SensorEntityDescription(
        key="tx0_status",
        name="TX0 Status",
        icon="mdi:video-output-hdmi",
    ),
    SensorEntityDescription(
        key="tx1_status",
        name="TX1 Status",
        icon="mdi:video-output-hdmi",
    ),
    SensorEntityDescription(
        key="audio_output",
        name="Audio Output",
        icon="mdi:speaker",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: HDFuryConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        HDFurySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class HDFurySensor(HDFuryEntity, SensorEntity):
    """HDFury Sensor class."""

    def __init__(
        self,
        coordinator: HDFuryDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.entity_description.key == "current_input":
            # Get the current input port selection for TX0
            port_num = self.coordinator.data.get("portseltx0")
            if port_num is not None:
                try:
                    port_idx = int(port_num)
                    if 0 <= port_idx < len(INPUT_NAMES):
                        return INPUT_NAMES[port_idx]
                    return f"Input {port_idx}"
                except (ValueError, TypeError):
                    return None
            return None
        if self.entity_description.key == "rx0_status":
            return self.coordinator.data.get("RX0")
        if self.entity_description.key == "rx1_status":
            return self.coordinator.data.get("RX1")
        if self.entity_description.key == "tx0_status":
            return self.coordinator.data.get("TX0")
        if self.entity_description.key == "tx1_status":
            return self.coordinator.data.get("TX1")
        if self.entity_description.key == "audio_output":
            return self.coordinator.data.get("AUDOUT")
        return None
