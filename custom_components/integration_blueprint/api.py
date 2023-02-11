"""Sample API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .const import LOGGER


class IntegrationBlueprintApiClient:
    """Sample API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> any:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        return await self._api_wrapper("get", url)

    async def async_set_title(self, value: str) -> any:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        return await self._api_wrapper(
            "patch",
            url,
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception("Something really wrong happened! - %s", exception)
