"""Test Anova Nano setup process."""
import pytest
from custom_components.anova_nano import (
    async_reload_entry,
)
from custom_components.anova_nano import (
    async_setup_entry,
)
from custom_components.anova_nano import (
    async_unload_entry,
)
from custom_components.anova_nano import (
    AnovaNanoDataUpdateCoordinator,
)
from custom_components.anova_nano.const import (
    DOMAIN,
)
from homeassistant.exceptions import ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
async def test_setup_unload_and_reload_entry(hass, bypass_get_data):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the AnovaNanoDataUpdateCoordinator.async_get_data
    # call, no code from custom_components/anova_nano/api.py actually runs.
    await hass.config_entries.async_setup(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id]) == AnovaNanoDataUpdateCoordinator
    )

    ## Reload the entry and assert that the data from above is still there
    await hass.config_entries.async_reload(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id]) == AnovaNanoDataUpdateCoordinator
    )

    ## Unload the entry and verify that the data has been removed
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id) == False
