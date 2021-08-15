"""Sample API Client."""
from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp
import async_timeout

API_HEADERS = {aiohttp.hdrs.CONTENT_TYPE: "application/json; charset=UTF-8"}


class ApiClientException(Exception):
    """Api Client Exception."""


class IntegrationBlueprintApiClient:
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

    async def async_get_data(self) -> dict[str, Any]:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        return await self.api_wrapper("get", url)

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=API_HEADERS)

    async def api_wrapper(
        self,
        method: str,
        url: str,
        data: dict[str, Any] = {},
        headers: dict = {},
    ) -> dict[str, Any] | None:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10, loop=asyncio.get_event_loop()):
                response = await self._session.request(
                    method=method, url=url, headers=headers, json=data
                )
                if method == "get":
                    return await response.json()

        except asyncio.TimeoutError as exception:
            raise ApiClientException(
                f"Timeout error fetching information from {url}"
            ) from exception

        except (KeyError, TypeError) as exception:
            raise ApiClientException(
                f"Error parsing information from {url} - {exception}"
            ) from exception

        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ApiClientException(
                f"Error fetching information from {url} - {exception}"
            ) from exception

        except Exception as exception:  # pylint: disable=broad-except
            raise ApiClientException(exception) from exception
