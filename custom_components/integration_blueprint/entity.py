"""BlueprintEntity class"""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import BlueprintDataUpdateCoordinator
from .const import ATTRIBUTION, DOMAIN, NAME, VERSION


class IntegrationBlueprintEntity(CoordinatorEntity):
    """Base IntegrationBlueprint entity."""

    coordinator: BlueprintDataUpdateCoordinator

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID to use for this entity."""
        if not self.coordinator.config_entry:
            return None
        return self.coordinator.config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
