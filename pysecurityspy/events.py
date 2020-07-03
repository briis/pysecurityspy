"""Module to retrieve events from the SecuritySpy API."""
import logging
import asyncio
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from typing import Optional
from base64 import b64encode

from pysecurityspy.errors import (
    InvalidCredentials,
    RequestError,
    ResultError,
)

_LOGGER = logging.getLogger(__name__)

class SecuritySpyEvents:
    """Main class to handle events from SecuritySpy."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = False,
        session: Optional[ClientSession] = None,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._session: ClientSession = session
        self._auth = b64encode(bytes(self._username + ":" + self._password, "utf-8")).decode()
        self._base = "http" if not use_ssl else "https"


    async def event_loop(self) -> None:
        """Main Event Loop listening for data."""

        endpoint = f"{self._base}://{self._host}:{self._port}/++eventStream?version=3&format=multipart&auth={self._auth}"
        _LOGGER.debug(f"{endpoint}")
        try:
            async with self._session.request("get", endpoint) as resp:
                async for line in resp.content:
                    data = line.decode()
                    if data[:14].isnumeric():
                        event_arr = data.split(" ")
                        camera_id = event_arr[2]
                        if event_arr[3] == "MOTION" and camera_id != "X":
                            _LOGGER.info(f"MOTION DETECTED - CAMERA {camera_id}")
                        elif event_arr[3] == "TRIGGER_M" and camera_id != "X":
                            _LOGGER.info(f"MOTION CAPTURED: REASON: {event_arr[4]} - CAMERA {camera_id}")
                    await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            raise RequestError("Request to endpoint timed out: {endpoint}")
        except ClientError as err:
            raise RequestError(f"Error requesting data from {endpoint}: {err}")
