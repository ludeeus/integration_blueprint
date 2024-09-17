"""Custom types for ims_envista."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from ims_envista import IMSEnvista

    from .coordinator import ImsEnvistaUpdateCoordinator


type ImsEnvistaConfigEntry = ConfigEntry[ImsEnvistaData]


@dataclass
class ImsEnvistaData:
    """Data for the Blueprint integration."""

    client: IMSEnvista
    coordinator: ImsEnvistaUpdateCoordinator
    integration: Integration
    station_id: int
    conditions: list[str]
