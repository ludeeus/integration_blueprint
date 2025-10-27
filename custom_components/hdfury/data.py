"""Custom types for HDFury integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import HDFuryApiClient
    from .coordinator import HDFuryDataUpdateCoordinator


type HDFuryConfigEntry = ConfigEntry[HDFuryData]


@dataclass
class HDFuryData:
    """Data for the HDFury integration."""

    client: HDFuryApiClient
    coordinator: HDFuryDataUpdateCoordinator
    integration: Integration
