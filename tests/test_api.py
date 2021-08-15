"""Tests for integration_blueprint api."""
import pytest
import asyncio

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.integration_blueprint.api import (
    ApiClientException,
    IntegrationBlueprintApiClient,
)


async def test_api(hass, aioclient_mock):
    """Test API calls."""

    # To test the api submodule, we first create an instance of our API client
    api = IntegrationBlueprintApiClient("test", "test", async_get_clientsession(hass))

    # Use aioclient_mock which is provided by `pytest_homeassistant_custom_components`
    # to mock responses to aiohttp requests. In this case we are telling the mock to
    # return {"test": "test"} when a `GET` call is made to the specified URL. We then
    # call `async_get_data` which will make that `GET` request.
    aioclient_mock.get(
        "https://jsonplaceholder.typicode.com/posts/1", json={"test": "test"}
    )
    assert await api.async_get_data() == {"test": "test"}

    # We do the same for `async_set_title`. Note the difference in the mock call
    # between the previous step and this one. We use `patch` here instead of `get`
    # because we know that `async_set_title` calls `api_wrapper` with `patch` as the
    # first parameter
    aioclient_mock.patch("https://jsonplaceholder.typicode.com/posts/1")
    assert await api.async_set_title("test") is None

    # In order to get 100% coverage, we need to test `api_wrapper` to test the code
    # that isn't already called by `async_get_data` and `async_set_title`. Because the
    # only logic that lives inside `api_wrapper` that is not being handled by a third
    # party library (aiohttp) is the exception handling, we also want to simulate
    # raising the exceptions to ensure that the function handles them as expected.
    aioclient_mock.put(
        "https://jsonplaceholder.typicode.com/posts/1", exc=asyncio.TimeoutError
    )
    with pytest.raises(
        ApiClientException,
        match="Timeout error fetching information from https://jsonplaceholder.typicode.com/posts/1",
    ):
        assert (
            await api.api_wrapper("put", "https://jsonplaceholder.typicode.com/posts/1")
            is None
        )

    aioclient_mock.post(
        "https://jsonplaceholder.typicode.com/posts/1", exc=aiohttp.ClientError
    )
    with pytest.raises(
        ApiClientException,
        match="Error fetching information from https://jsonplaceholder.typicode.com/posts/1 - ",
    ):
        assert (
            await api.api_wrapper(
                "post", "https://jsonplaceholder.typicode.com/posts/1"
            )
            is None
        )

    aioclient_mock.post(
        "https://jsonplaceholder.typicode.com/posts/2", exc=Exception("Unkonw exeption")
    )
    with pytest.raises(ApiClientException, match="Unkonw exeption"):
        assert (
            await api.api_wrapper(
                "post", "https://jsonplaceholder.typicode.com/posts/2"
            )
            is None
        )

    aioclient_mock.post("https://jsonplaceholder.typicode.com/posts/3", exc=TypeError)
    with pytest.raises(
        ApiClientException,
        match="Error parsing information from https://jsonplaceholder.typicode.com/posts/3 - ",
    ):
        assert (
            await api.api_wrapper(
                "post", "https://jsonplaceholder.typicode.com/posts/3"
            )
            is None
        )
