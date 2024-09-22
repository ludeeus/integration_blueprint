"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import ImsEnvistaUpdateCoordinator


class ImsEnvistaEntity(CoordinatorEntity[ImsEnvistaUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ImsEnvistaUpdateCoordinator,
        station_id: int,
        condition_name: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        station = coordinator.get_station_info(station_id)

        self._station_id = station_id
        self._condition_name = condition_name
        self._attr_unique_id = f"ims_envista_{station_id!s}_{condition_name}"
        self._attr_device_info = DeviceInfo(
            name=station.name,
            manufacturer=station.owner,
            model=station.station_target,
            identifiers={
                (
                    coordinator.config_entry.domain,
                    f"station_{station_id!s}",
                ),
            },
        )
