"""AnovaNanoEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import AnovaNanoDataUpdateCoordinator


class AnovaNanoEntity(CoordinatorEntity):
    """AnovaNanoEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: AnovaNanoDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )


class AnovaNanoDescriptionEntity(AnovaNanoEntity):
    """Defines an Anova Nano entity that uses a description."""

    def __init__(
        self,
        coordinator: AnovaNanoDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity and declare unique id based on description key."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
