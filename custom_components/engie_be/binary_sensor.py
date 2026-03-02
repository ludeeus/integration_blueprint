"""Binary sensor platform for the ENGIE Belgium integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import EngieBeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EngieBeDataUpdateCoordinator
    from .data import EngieBeConfigEntry

AUTHENTICATION_SENSOR_DESCRIPTION = BinarySensorEntityDescription(
    key="authentication",
    translation_key="authentication",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
    icon="mdi:shield-check",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: EngieBeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [EngieBeAuthSensor(coordinator=coordinator, entry=entry)],
    )


class EngieBeAuthSensor(EngieBeEntity, BinarySensorEntity):
    """Binary sensor indicating whether the integration is authenticated."""

    entity_description = AUTHENTICATION_SENSOR_DESCRIPTION

    def __init__(
        self,
        coordinator: EngieBeDataUpdateCoordinator,
        entry: EngieBeConfigEntry,
    ) -> None:
        """Initialise the authentication binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_authentication"

    @property
    def available(self) -> bool:
        """Auth sensor is always available; its state reflects token validity."""
        return True

    @property
    def is_on(self) -> bool:
        """Return True if the integration is currently authenticated."""
        return self._entry.runtime_data.authenticated
