"""Tests for anova_nano api."""

from custom_components.anova_nano.api import (
    AnovaNanoApiClient,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def test_api(hass, aioclient_mock, caplog):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = AnovaNanoApiClient("test", "test", async_get_clientsession(hass))

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return {"test": "test"} when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    aioclient_mock.get(
        "https://jsonplaceholder.typicode.com/posts/1", text='{"test": "test"}'
    )
    assert await api.async_get_data() == {"test": "test"}

    # We do the same for `async_set_title`. Note the difference in the mock call
    # between the previous step and this one. We use `patch` here instead of `get`
    # because we know that `async_set_title` calls `api_wrapper` with `patch` as the
    # first parameter
    aioclient_mock.patch("https://jsonplaceholder.typicode.com/posts/1", text='null')
    assert await api.async_set_title("test") is None
