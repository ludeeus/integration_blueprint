"""Custom types for the ENGIE Belgium integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import EngieBeApiClient
    from .coordinator import EngieBeDataUpdateCoordinator


type EngieBeConfigEntry = ConfigEntry[EngieBeData]


@dataclass
class EngieBeData:
    """Runtime data for the ENGIE Belgium integration."""

    client: EngieBeApiClient
    coordinator: EngieBeDataUpdateCoordinator
    authenticated: bool = field(default=False)
    last_options: dict[str, Any] = field(default_factory=dict)
