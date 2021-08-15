"""Switch platform for integration_blueprint."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_NAME, DOMAIN, ICON, SWITCH
from .entity import IntegrationBlueprintEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([IntegrationBlueprintBinarySwitch(coordinator)])


class IntegrationBlueprintBinarySwitch(IntegrationBlueprintEntity, SwitchEntity):
    """integration_blueprint switch class."""

    _attr_icon = ICON
    _attr_name = f"{DEFAULT_NAME}_{SWITCH}"

    async def async_turn_on(self, **kwargs: dict[str, Any]) -> None:
        """Turn on the switch."""
        await self.coordinator.api.async_set_title("foo")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: dict[str, Any]) -> None:
        """Turn off the switch."""
        await self.coordinator.api.async_set_title("bar")
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get("title", "") == "foo"
