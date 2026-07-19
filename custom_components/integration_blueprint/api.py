"""Sample API Client."""

from __future__ import annotations

import asyncio
import math
import socket
from contextlib import suppress
from http import HTTPStatus
from typing import Any

import aiohttp


class IntegrationBlueprintApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationBlueprintApiClientCommunicationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate a communication error."""


class IntegrationBlueprintApiClientAuthenticationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate an authentication error."""


class IntegrationBlueprintApiClientRateLimitError(
    IntegrationBlueprintApiClientCommunicationError,
):
    """Exception to indicate the API is rate limiting us."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        """Store the backoff period requested by the API."""
        super().__init__(message)
        self.retry_after = retry_after


def _parse_retry_after(response: aiohttp.ClientResponse) -> int:
    """Return the backoff period (whole seconds) from the Retry-After header."""
    value: float | None = None
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        with suppress(ValueError):
            value = float(retry_after)
    if value is not None and math.isfinite(value) and value >= 0:
        return math.ceil(value)
    return 60


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationBlueprintApiClientAuthenticationError(
            msg,
        )
    if response.status == HTTPStatus.TOO_MANY_REQUESTS:
        msg = "Rate limited by the API"
        raise IntegrationBlueprintApiClientRateLimitError(
            msg,
            retry_after=_parse_retry_after(response),
        )
    response.raise_for_status()


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

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except IntegrationBlueprintApiClientError:
            # Our own typed errors (auth, rate-limit, communication) are already
            # meaningful; re-raise so callers can branch on them instead of masking
            # them with the broad handler below.
            raise
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise IntegrationBlueprintApiClientError(
                msg,
            ) from exception
