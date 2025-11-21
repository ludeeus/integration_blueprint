"""BlueprintEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import BlueprintDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class IntegrationBlueprintEntity(CoordinatorEntity[BlueprintDataUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        # Include entity description key in unique_id to support multiple entities
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name="Integration Blueprint",
            manufacturer="Integration Blueprint",
            model=coordinator.data.get("model", "Unknown"),
        )
