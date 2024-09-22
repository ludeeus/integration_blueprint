"""Adds config flow for Blueprint."""

from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_API_TOKEN
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from ims_envista import (
    IMSEnvista,
    ImsEnvistaApiClientAuthenticationError,
    ImsEnvistaApiClientCommunicationError,
    ImsEnvistaApiClientError,
)

from .const import (
    CONF_STATION,
    CONF_STATION_CONDITIONS,
    CONF_STATION_ID,
    DOMAIN,
    LAST_UPDATED_CHANNEL,
    LOGGER,
    STATION_NAME_CHANNEL,
)

if TYPE_CHECKING:
    from uuid import UUID

    from ims_envista.station_data import StationInfo

MIN_DISTANCE_TO_STATION_FOR_AUTOSELECT = 10


def _find_closest_station(
    stations: list[StationInfo], ha_latitude: float, ha_longitude: float
) -> StationInfo | None:
    """Find the closest station based on the Home Assistant coordinates."""

    def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Calculate the distance between two lat/lon points (Haversine formula)
        R = 6371  # Radius of Earth in kilometers  # noqa: N806
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c  # Distance in kilometers

    closest_station = None
    closest_distance = float("inf")

    for station in stations:
        station_lat = station.location.latitude
        station_lon = station.location.longitude
        dist = distance(ha_latitude, ha_longitude, station_lat, station_lon)

        if dist < closest_distance:
            closest_distance = dist
            closest_station = station

    if closest_distance > MIN_DISTANCE_TO_STATION_FOR_AUTOSELECT:
        LOGGER.debug(
            "Closest station is too far away: %s > %s",
            closest_distance,
            MIN_DISTANCE_TO_STATION_FOR_AUTOSELECT,
        )
        return stations[0] if len(stations) > 0 else None
    LOGGER.debug(
        "Closest station is: %s - %s km",
        closest_station.name,
        round(closest_distance, 2),
    )
    return closest_station


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    def __init__(self) -> None:
        """Instantiate a config flow."""
        super().__init__()
        self._selected_station: StationInfo | None = None
        self._stations: list[StationInfo] | None = None
        self._token: UUID | str | None = None

    async def _test_token(self, token: UUID | str) -> list[StationInfo]:
        """Validate credentials."""
        client = IMSEnvista(
            token=str(token),
            session=async_create_clientsession(self.hass),
        )
        return await client.get_all_stations_info()

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            try:
                stations = await self._test_token(
                    token=token,
                )
                LOGGER.debug("IMS Token is valid")
                LOGGER.debug("Number of stations: %d", len(stations))

            except ImsEnvistaApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except ImsEnvistaApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except ImsEnvistaApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                self._token = token
                self._stations = stations
                return await self.async_step_select_station()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def async_step_select_station(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle the seconds step of the configure flow - selecting a station."""
        _errors = {}
        if user_input is not None and user_input[CONF_STATION]:
            selected_station = next(
                filter(
                    lambda st: st.station_id == user_input[CONF_STATION], self._stations
                ),
                None,
            )
            LOGGER.debug("Selected Station is: %s", selected_station.name)
            if selected_station:
                self._selected_station = selected_station
                return await self.async_step_select_station_conditions()
            _errors["base"] = "unknown"
        active_stations = [station for station in self._stations if station.active]

        # Step 2: Calculate the closest station based on Home Assistant's coordinates
        ha_latitude = self.hass.config.latitude
        ha_longitude = self.hass.config.longitude
        closest_station = _find_closest_station(
            active_stations, ha_latitude, ha_longitude
        )

        # Step 3: Create a selection field for cities
        station_options = {
            station.station_id: station.name for station in active_stations
        }

        return self.async_show_form(
            step_id="select_station",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION, default=closest_station.station_id
                    ): vol.In(station_options),
                },
            ),
            errors=_errors,
        )

    async def async_step_select_station_conditions(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle the configure flow - selecting station's properties."""
        _errors = {}
        if user_input is not None and user_input[CONF_STATION_CONDITIONS]:
            selected_conditions = user_input[CONF_STATION_CONDITIONS]
            LOGGER.debug("Selected Monitored Conditions: %s", selected_conditions)
            data = {
                CONF_API_TOKEN: self._token,
                CONF_STATION_ID: self._selected_station.station_id,
                CONF_STATION_CONDITIONS: selected_conditions,
            }

            return self.async_create_entry(
                title="IMS Envista - " + self._selected_station.name,
                data=data,
            )

        LOGGER.debug("All Monitored Conditions: %s", self._selected_station.monitors)
        # Step 3: Create a selection field for monitored conditions
        monitor_options = [
            monitor.name
            for monitor in self._selected_station.monitors
            if monitor.active
        ]

        monitor_options.insert(0, LAST_UPDATED_CHANNEL)
        monitor_options.insert(0, STATION_NAME_CHANNEL)
        LOGGER.debug("Active Monitored Conditions: %s", monitor_options)

        return self.async_show_form(
            step_id="select_station_conditions",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_STATION_CONDITIONS, default=monitor_options
                    ): cv.multi_select(monitor_options),
                },
            ),
            errors=_errors,
        )
