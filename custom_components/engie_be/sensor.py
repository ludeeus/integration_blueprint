"""Sensor platform for the ENGIE Belgium integration."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import (
    ELECTRICITY_EAN_PREFIX,
    GAS_EAN_PREFIX,
    LOGGER,
)
from .entity import EngieBeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EngieBeDataUpdateCoordinator
    from .data import EngieBeConfigEntry


def _detect_energy_type(ean: str) -> str:
    """Detect the energy type from the EAN prefix."""
    if ean.startswith(GAS_EAN_PREFIX):
        return "Gas"
    if ean.startswith(ELECTRICITY_EAN_PREFIX):
        return "Electricity"
    return ean


def _find_current_price(prices: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the price entry whose date range covers today, or the last entry."""
    today = datetime.now(tz=UTC).date()
    for price in prices:
        from_date = date.fromisoformat(price["from"])
        to_date = date.fromisoformat(price["to"])
        if from_date <= today < to_date:
            return price
    # Fall back to the last entry if no exact match
    return prices[-1] if prices else None


# Mapping from API timeOfUseSlotCode to (key_suffix, translation_suffix).
# TOTAL_HOURS uses empty strings to preserve backward compatibility.
_SLOT_CODE_MAP: dict[str, tuple[str, str]] = {
    "TOTAL_HOURS": ("", ""),
    "PEAK": ("_peak", "_peak"),
    "OFFPEAK": ("_offpeak", "_offpeak"),
}


def _slot_suffixes(slot_code: str) -> tuple[str, str]:
    """Return (key_suffix, translation_suffix) for a time-of-use slot code."""
    if slot_code in _SLOT_CODE_MAP:
        return _SLOT_CODE_MAP[slot_code]
    # Unknown codes: use lowercased slot code as suffix
    lower = slot_code.lower()
    return (f"_{lower}", f"_{lower}")


def _build_sensor_descriptions(
    data: dict[str, Any],
) -> list[tuple[SensorEntityDescription, str, str, str]]:
    """
    Build sensor descriptions from the API response.

    Returns a list of ``(description, ean, value_key, slot_code)`` tuples where
    *value_key* is a dotted path like ``offtake.priceValue`` and *slot_code* is
    the ``timeOfUseSlotCode`` (e.g. ``TOTAL_HOURS``, ``PEAK``, ``OFFPEAK``).
    """
    sensors: list[tuple[SensorEntityDescription, str, str, str]] = []

    for item in data.get("items", []):
        ean: str = item.get("ean", "unknown")
        energy_type = _detect_energy_type(ean)
        # Strip trailing _ID* suffix for display
        # e.g. "541448...267_ID1" -> cleaner key
        ean_short = ean.split("_", maxsplit=1)[0] if "_" in ean else ean

        current_price = _find_current_price(item.get("prices", []))
        if current_price is None:
            continue

        configs = current_price.get("proportionalPriceConfigurations", {})

        for direction, icon in (
            ("offtake", "mdi:cash-minus"),
            ("injection", "mdi:cash-plus"),
        ):
            direction_list: list[dict[str, Any]] = configs.get(direction, [])
            if not direction_list:
                continue

            for slot_entry in direction_list:
                slot_code: str = slot_entry.get("timeOfUseSlotCode", "TOTAL_HOURS")
                key_suffix, trans_suffix = _slot_suffixes(slot_code)

                base_key = f"{ean_short}_{direction}{key_suffix}"
                base_trans = f"{energy_type.lower()}_{direction}{trans_suffix}"

                # Price including VAT
                sensors.append(
                    (
                        SensorEntityDescription(
                            key=base_key,
                            translation_key=base_trans,
                            icon=icon,
                            native_unit_of_measurement="EUR/kWh",
                            state_class=SensorStateClass.MEASUREMENT,
                            suggested_display_precision=6,
                        ),
                        ean,
                        f"{direction}.priceValue",
                        slot_code,
                    )
                )
                # Price excluding VAT
                sensors.append(
                    (
                        SensorEntityDescription(
                            key=f"{base_key}_excl_vat",
                            translation_key=f"{base_trans}_excl_vat",
                            icon=icon,
                            native_unit_of_measurement="EUR/kWh",
                            state_class=SensorStateClass.MEASUREMENT,
                            suggested_display_precision=6,
                        ),
                        ean,
                        f"{direction}.priceValueExclVAT",
                        slot_code,
                    )
                )

    return sensors


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: EngieBeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    # Wait for first data before building sensors
    if coordinator.data is None:
        LOGGER.warning("No data available yet, skipping sensor setup")
        return

    sensor_defs = _build_sensor_descriptions(coordinator.data)
    async_add_entities(
        EngieBeEnergySensor(
            coordinator=coordinator,
            entity_description=desc,
            ean=ean,
            value_key=value_key,
            slot_code=slot_code,
        )
        for desc, ean, value_key, slot_code in sensor_defs
    )


class EngieBeEnergySensor(EngieBeEntity, SensorEntity):
    """Sensor for an ENGIE Belgium energy price."""

    def __init__(
        self,
        coordinator: EngieBeDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        ean: str,
        value_key: str,
        slot_code: str,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._ean = ean
        self._value_key = value_key
        self._slot_code = slot_code
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the current price value."""
        return self._get_price_value()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs: dict[str, Any] = {"ean": self._ean}
        price_entry = self._get_current_price_entry()
        if price_entry:
            attrs["from"] = price_entry.get("from")
            attrs["to"] = price_entry.get("to")
            attrs["vat_tariff"] = price_entry.get("vatTariff")
            attrs["time_of_use_slot_code"] = self._slot_code
        return attrs

    def _get_current_price_entry(self) -> dict[str, Any] | None:
        """Find the current price entry for this sensor's EAN."""
        if not self.coordinator.data:
            return None
        for item in self.coordinator.data.get("items", []):
            if item.get("ean") == self._ean:
                return _find_current_price(item.get("prices", []))
        return None

    def _get_price_value(self) -> float | None:
        """Extract the specific price value from the current entry."""
        price_entry = self._get_current_price_entry()
        if not price_entry:
            return None

        direction, field_name = self._value_key.split(".")
        configs = price_entry.get("proportionalPriceConfigurations", {})
        direction_list: list[dict[str, Any]] = configs.get(direction, [])
        if not direction_list:
            return None

        # Find the entry matching this sensor's time-of-use slot code
        for slot_entry in direction_list:
            if slot_entry.get("timeOfUseSlotCode") == self._slot_code:
                value = slot_entry.get(field_name)
                if value is None:
                    return None
                return float(value)

        return None
