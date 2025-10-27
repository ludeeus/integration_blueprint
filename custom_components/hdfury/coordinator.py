"""DataUpdateCoordinator for HDFury integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HDFuryApiClientError

if TYPE_CHECKING:
    from .data import HDFuryConfigEntry


class HDFuryDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the HDFury API."""

    config_entry: HDFuryConfigEntry

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_status()
        except HDFuryApiClientError as exception:
            raise UpdateFailed(exception) from exception
