"""Module to retrieve events from the SecuritySpy API."""
import logging
import asyncio
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from typing import Optional
from base64 import b64encode
import xml.etree.ElementTree as ET

from pysecurityspy.errors import (
    InvalidCredentials,
    RequestError,
    ResultError,
)
from pysecurityspy.dataclasses import EventData
from pysecurityspy.const import (
    EVENT_TYPES,
    EVENT_TYPE_MOTION,
    EVENT_TYPE_CLASIFY,
    EVENT_TYPE_TRIGGER_M,
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
        self._callbacks = []
        self.event_data = {}

    async def registerCallback(self, callback):
        """.Handle Callback Data."""
        self._callbacks.append(callback)

    async def event_loop(self) -> None:
        """Main Event Loop listening for data."""

        # Retrieve Camera details and create JSON structure
        endpoint = f"{self._base}://{self._host}:{self._port}/++systemInfo&auth={self._auth}"
        response = await self.async_request("get", endpoint)
        cameras = ET.fromstring(response)
        for item in cameras.iterfind('cameralist/camera'):
            uid = int(item.findtext("number"))
            name = item.findtext("name")
            item = {
                uid: {
                    "name": name,
                    "timestamp": None,
                    "camera_id": 0,
                    "event_type": 0,
                    "box_pos_x": 0,
                    "box_pos_y": 0,
                    "box_pos_h": 0,
                    "box_pos_w": 0,
                    "trigger_type": 0,
                    "classify_score": 0,
                    "classify_type": None,
                }
            }
            self.event_data.update(item)
        
        # Start the Event Loop Stream
        endpoint = f"{self._base}://{self._host}:{self._port}/++eventStream?version=3&format=multipart&auth={self._auth}"
        _LOGGER.debug(f"{endpoint}")
        try:
            events = []
            async with self._session.request("get", endpoint) as resp:
                async for line in resp.content:
                    data = line.decode()
                    if data[:14].isnumeric():
                        event_arr = data.split(" ")
                        camera_id = int(event_arr[2])
                        event_id = event_arr[3]
                        if event_id in EVENT_TYPES:
                            if event_id == EVENT_TYPE_MOTION:
                                box_pos_x = int(event_arr[4])
                                box_pos_y = int(event_arr[5])
                                box_pos_w = int(event_arr[6])
                                box_pos_h = int(event_arr[7])
                                trigger_type = 0
                                classify_score = 0
                                classify_type = None
                            elif event_id == EVENT_TYPE_TRIGGER_M:
                                trigger_type = int(event_arr[4])
                                box_pos_x = 0
                                box_pos_y = 0
                                box_pos_h = 0
                                box_pos_w = 0
                                classify_score = 0
                                classify_type = None
                            elif event_id == EVENT_TYPE_CLASIFY:
                                classify_score = int(event_arr[5])
                                classify_type = event_arr[4]
                                box_pos_x = 0
                                box_pos_y = 0
                                box_pos_h = 0
                                box_pos_w = 0
                            self.event_data[camera_id]["timestamp"] = event_arr[0]
                            self.event_data[camera_id]["event_type"] = event_arr[3]
                            self.event_data[camera_id]["box_pos_x"] = box_pos_x
                            self.event_data[camera_id]["box_pos_y"] = box_pos_y
                            self.event_data[camera_id]["box_pos_w"] = box_pos_w
                            self.event_data[camera_id]["box_pos_h"] = box_pos_h
                            self.event_data[camera_id]["trigger_type"] = trigger_type
                            self.event_data[camera_id]["classify_score"] = classify_score
                            self.event_data[camera_id]["classify_type"] = classify_type

                        for callback in self._callbacks:
                            callback(self.event_data)

                    await asyncio.sleep(0)

        except asyncio.TimeoutError:
            raise RequestError("Request to endpoint timed out: {endpoint}")
        except ClientError as err:
            raise RequestError(f"Error requesting data from {endpoint}: {err}")
