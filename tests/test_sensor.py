"""Test sensor for simple integration."""
import pytest

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.anova_nano.const import DOMAIN
from custom_components.anova_nano.const import (
    DOMAIN,
)

from .const import MOCK_CONFIG

async def test_sensor(hass):
    """Test sensor."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.integration_sensor")

    assert state
    assert state.state == "23"
