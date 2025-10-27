"""HDFury API Client."""

from __future__ import annotations

import socket
from typing import Any
from urllib.parse import quote

import aiohttp
import async_timeout

from .const import MAX_INPUT_PORT


class HDFuryApiClientError(Exception):
    """Exception to indicate a general API error."""


class HDFuryApiClientCommunicationError(HDFuryApiClientError):
    """Exception to indicate a communication error."""


class HDFuryApiClientConnectionError(HDFuryApiClientError):
    """Exception to indicate a connection error."""


class HDFuryApiClient:
    """HDFury API Client."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        port: int = 80,
    ) -> None:
        """
        Initialize the HDFury API Client.

        Args:
            host: The hostname or IP address of the HDFury device
            session: The aiohttp client session
            port: The port number (default: 80)

        """
        self._host = host
        self._port = port
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def async_get_status(self) -> dict[str, Any]:
        """
        Get current status from the HDFury device.

        Returns:
            Dictionary containing device status information

        """
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(
                    f"{self._base_url}/ssi/infopage.ssi",
                )
                response.raise_for_status()
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information from {self._host}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information from {self._host} - {exception}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error occurred - {exception}"
            raise HDFuryApiClientError(msg) from exception

    async def async_set_input(self, input_port: int, output_port: int = 4) -> None:
        """
        Set the input port for the specified output.

        Args:
            input_port: Input port number (0-3)
            output_port: Output port (default: 4 which means "follow")

        """
        if not 0 <= input_port <= MAX_INPUT_PORT:
            msg = f"Invalid input port: {input_port}. Must be 0-{MAX_INPUT_PORT}."
            raise ValueError(msg)

        # Format: /cmd?insel=<input>%20<output>
        # %20 is URL encoded space
        url = f"{self._base_url}/cmd?insel={input_port}%20{output_port}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()

        except TimeoutError as exception:
            msg = f"Timeout error setting input on {self._host}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error setting input on {self._host} - {exception}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error occurred - {exception}"
            raise HDFuryApiClientError(msg) from exception

    async def async_send_command(self, command: str) -> str:
        """
        Send a raw command to the HDFury device via HTTP.

        Args:
            command: The command string (e.g., "get insel" or "set oled on")

        Returns:
            Response from the device

        """
        # URL encode the command
        encoded_cmd = quote(command)
        url = f"{self._base_url}/cmd?{encoded_cmd}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()
                return await response.text()

        except TimeoutError as exception:
            msg = f"Timeout error sending command to {self._host}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error sending command to {self._host} - {exception}"
            raise HDFuryApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error occurred - {exception}"
            raise HDFuryApiClientError(msg) from exception

    async def async_test_connection(self) -> bool:
        """
        Test if we can connect to the HDFury device.

        Returns:
            True if connection is successful

        """
        try:
            await self.async_get_status()
            return True
        except HDFuryApiClientError:
            return False
