"""Sensor platform for ims_envista."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfPrecipitationDepth,
    UnitOfSpeed,
    UnitOfTemperature,
)

from .const import (
    LAST_UPDATED_CHANNEL,
    LATEST_KEY,
    LOGGER,
    RAIN_CHANNEL,
    RH_CHANNEL,
    STATIC_DATA_CHANNELS,
    STATION_NAME_CHANNEL,
    STDWD_CHANNEL,
    TD_CHANNEL,
    TDMAX_CHANNEL,
    TDMIN_CHANNEL,
    WD_CHANNEL,
    WDMAX_CHANNEL,
    WS_1MM_CHANNEL,
    WS_10MM_CHANNEL,
    WS_CHANNEL,
    WSMAX_CHANNEL,
)
from .entity import ImsEnvistaEntity

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ims_envista.station_data import StationInfo

    from .coordinator import ImsEnvistaUpdateCoordinator
    from .data import ImsEnvistaConfigEntry


@dataclass(frozen=True, kw_only=True)
class ImsEnvistaEntityDescriptionMixin:
    """Mixin values for required keys."""

    value_fn: Callable[[dict | tuple | StationInfo], str | float | datetime] | None = (
        None
    )


@dataclass(frozen=True, kw_only=True)
class ImsEnvistaSensorEntityDescription(
    SensorEntityDescription, ImsEnvistaEntityDescriptionMixin
):
    """Class describing IMS sensors entities."""


ENTITY_DESCRIPTIONS = {
    STATION_NAME_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="station_name",
        name="Station Name",
        icon="mdi:home-city",
        value_fn=lambda station_info: station_info.name.title(),
    ),
    LAST_UPDATED_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="last_updated",
        device_class=SensorDeviceClass.TIMESTAMP,
        name="Last Update Time",
        icon="mdi:sun-clock",
        value_fn=lambda data: data[LATEST_KEY].datetime,
    ),
    RAIN_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="rain",
        device_class=SensorDeviceClass.PRECIPITATION,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        suggested_display_precision=1,
        name="Rain",
        icon="mdi:weather-pouring",
        value_fn=lambda data: data[LATEST_KEY].rain,
    ),
    WSMAX_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="wsmax",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        suggested_display_precision=1,
        name="WS Max",
        icon="mdi:weather-windy",
        value_fn=lambda data: data[LATEST_KEY].ws_max,
    ),
    WDMAX_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="wdmax",
        native_unit_of_measurement=DEGREE,
        suggested_display_precision=0,
        name="WD Max",
        icon="mdi:compass",
        value_fn=lambda data: data[LATEST_KEY].wd_max,
    ),
    WS_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="ws",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        suggested_display_precision=1,
        name="WS",
        icon="mdi:weather-windy",
        value_fn=lambda data: data[LATEST_KEY].ws,
    ),
    WD_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="wd",
        native_unit_of_measurement=DEGREE,
        suggested_display_precision=0,
        name="WD",
        icon="mdi:compass",
        value_fn=lambda data: data[LATEST_KEY].wd,
    ),
    STDWD_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="std_wd",
        native_unit_of_measurement=DEGREE,
        suggested_display_precision=1,
        name="Std WD",
        icon="mdi:compass",
        value_fn=lambda data: data[LATEST_KEY].std_wd,
    ),
    TD_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="td",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        name="TD",
        icon="mdi:thermometer",
        value_fn=lambda data: data[LATEST_KEY].td,
    ),
    TDMAX_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="td_max",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        name="TD max",
        icon="mdi:thermometer-chevron-up",
        value_fn=lambda data: data[LATEST_KEY].td_max,
    ),
    TDMIN_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="td_min",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        name="TD Min",
        icon="mdi:thermometer-chevron-min",
        value_fn=lambda data: data[LATEST_KEY].td_min,
    ),
    RH_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="rh",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        name="RH",
        icon="mdi:cloud-percent",
        value_fn=lambda data: data[LATEST_KEY].rh,
    ),
    # TG_CHANNEL: ImsEnvistaSensorEntityDescription(
    #     key="tg",
    #     name="TG",
    #     icon="mdi:weather-pouring",
    #     value_fn=lambda data: data[LATEST_KEY].tg
    # ),
    # RAD_AGRO_CHANNEL: ImsEnvistaSensorEntityDescription(
    #     key="rad_rgro",
    #     name="Rad Agro",
    #     icon="mdi:weather-pouring",
    #     value_fn=lambda data: data[LATEST_KEY].rad_agro
    # ),
    WS_1MM_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="ws_1mm",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        suggested_display_precision=1,
        name="WS 1mm",
        icon="mdi:weather-windy",
        value_fn=lambda data: data[LATEST_KEY].ws_1mm,
    ),
    WS_10MM_CHANNEL: ImsEnvistaSensorEntityDescription(
        key="ws_10mm",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        suggested_display_precision=1,
        name="WS 10mm",
        icon="mdi:weather-windy",
        value_fn=lambda data: data[LATEST_KEY].ws_10mm,
    ),
    # TIME_CHANNEL: ImsEnvistaSensorEntityDescription(
    #     key="time",
    #     name="Time",
    #     icon="mdi:weather-pouring",
    #     value_fn=lambda data: data[LATEST_KEY].TIME_CHANNEL
    # ),
    # TW_CHANNEL: ImsEnvistaSensorEntityDescription(
    #     key="tw",
    #     name="TW",
    #     icon="mdi:weather-pouring",
    #     value_fn=lambda data: data[LATEST_KEY].tw
    # ),
}


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ImsEnvistaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    station_id = entry.runtime_data.station_id
    conditions = entry.runtime_data.conditions

    async_add_entities(
        ImsEnvistaSensor(
            coordinator=coordinator,
            station_id=station_id,
            condition_name=condition,
            entity_description=ENTITY_DESCRIPTIONS.get(condition),
        )
        for condition in conditions
        if ENTITY_DESCRIPTIONS.get(condition)
    )

    for condition in conditions:
        if not ENTITY_DESCRIPTIONS.get(condition):
            LOGGER.warning(
                "Condition %s has no matching EntityDescription, skipping!", condition
            )


class ImsEnvistaSensor(ImsEnvistaEntity, SensorEntity):
    """ims_envista Sensor class."""

    def __init__(
        self,
        coordinator: ImsEnvistaUpdateCoordinator,
        station_id: int,
        condition_name: str,
        entity_description: ImsEnvistaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, station_id, condition_name)
        self._attr_translation_key = f"{entity_description.key}"
        self.entity_description = entity_description
        self._attr_translation_key = f"{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self._condition_name in STATIC_DATA_CHANNELS:
            return self.entity_description.value_fn(
                self.coordinator.get_station_info(self._station_id)
            )
        if self.coordinator.data is not None:
            return self.entity_description.value_fn(
                self.coordinator.data.get(self._station_id)
            )
        return None
