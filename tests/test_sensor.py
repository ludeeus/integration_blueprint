"""Test sensor for simple integration."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.anova_nano.const import DOMAIN

from .const import MOCK_CONFIG


async def test_sensor(hass, aioclient_mock):
    """Test sensor."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    aioclient_mock.get(
        "https://jsonplaceholder.typicode.com/posts/1", text='{"body": "value"}'
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.integration_sensor")

    assert state
    assert state.state == "value"
