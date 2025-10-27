"""HDFuryEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import HDFuryDataUpdateCoordinator


class HDFuryEntity(CoordinatorEntity[HDFuryDataUpdateCoordinator]):
    """HDFury Entity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: HDFuryDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    coordinator.config_entry.entry_id,
                ),
            },
            name="HDFury Vertex²",
            manufacturer="HDFury",
            model="Vertex²",
        )
