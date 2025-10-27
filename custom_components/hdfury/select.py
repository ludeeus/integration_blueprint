"""Select platform for HDFury integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription

from .const import INPUT_NAMES
from .entity import HDFuryEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import HDFuryDataUpdateCoordinator
    from .data import HDFuryConfigEntry

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="input_select",
        name="Input Selection",
        icon="mdi:hdmi-port",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: HDFuryConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        HDFurySelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class HDFurySelect(HDFuryEntity, SelectEntity):
    """HDFury select class for input selection."""

    def __init__(
        self,
        coordinator: HDFuryDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"
        self._attr_options = INPUT_NAMES

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        port_num = self.coordinator.data.get("portseltx0")
        if port_num is not None:
            try:
                port_idx = int(port_num)
                if 0 <= port_idx < len(INPUT_NAMES):
                    return INPUT_NAMES[port_idx]
            except (ValueError, TypeError):
                pass
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            # Find the index of the selected option
            input_index = INPUT_NAMES.index(option)

            # Set the input using the API
            await self.coordinator.config_entry.runtime_data.client.async_set_input(
                input_port=input_index,
            )

            # Request a coordinator refresh to update all entities
            await self.coordinator.async_request_refresh()

        except ValueError:
            # Option not found in INPUT_NAMES
            pass
