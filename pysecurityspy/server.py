"""Module to communicate with the SecuritySpy API."""
import logging
import asyncio
import sys
import xml.etree.ElementTree as ET

from typing import Optional
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from base64 import b64encode
import threading
import requests

from pysecurityspy.const import (
    DEFAULT_TIMEOUT,
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
    MODE_ARMED,
    MODE_DISARMED,
    EVENT_TYPES,
    EVENT_TYPE_MOTION,
    EVENT_TYPE_CLASIFY,
    EVENT_TYPE_TRIGGER_M,
    EVENT_TYPE_FILE,
)
from pysecurityspy.errors import (
    InvalidCredentials,
    RequestError,
    ResultError,
)
from pysecurityspy.dataclasses import (
    CameraData,
    RecordingSettings,
)

_LOGGER = logging.getLogger(__name__)

class SecuritySpyServer:
    """Main class to communicate with SecuritySpy."""

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
        self.device_data = {}
        self.event_data = {}

    @property
    def devices(self):
        """ Returns a JSON formatted list of Devices. """
        return self.device_data

    async def update(self) -> dict:
        """Returns the updated data."""
        await self._get_camera_list()
        return self.devices

    
    async def get_server_information(self) -> None:
        """Return information about the SecuritySpy Server."""
        endpoint = f"{self._base}://{self._host}:{self._port}/++systemInfo&auth={self._auth}"
        _LOGGER.debug(endpoint)
        response = await self.async_request("get", endpoint)

        data = ET.fromstring(response)
        for item in data.iterfind('server'):
            try:
                row = {
                    "name": item.findtext("name"),
                    "version": item.findtext("version"),
                    "host": self._host
                }
                return row
                
            except BaseException as e:
                _LOGGER.debug("Error when retrieving Server Data: " + str(e))
                raise ResultError

    async def _get_camera_list(self) -> None:
        """Returns a list of the attached Cameras."""
        endpoint = f"{self._base}://{self._host}:{self._port}/++systemInfo&auth={self._auth}"
        response = await self.async_request("get", endpoint)

        cameras = ET.fromstring(response)
        for item in cameras.iterfind('cameralist/camera'):
            try:
                uid = int(item.findtext("number"))
                if item.findtext("connected") == "yes":
                    online = True
                else:
                    online = False
                mode_c = item.findtext("mode-c")
                mode_m = item.findtext("mode-m")
                recording_mode = RECORDING_MODE_NEVER
                if mode_c == MODE_ARMED:
                    recording_mode = RECORDING_MODE_ALWAYS
                elif mode_m == MODE_ARMED:
                    recording_mode = RECORDING_MODE_MOTION
                rtsp_video = f"rtsp://{self._username}:{self._password}@{self._host}:{self._port}/++stream?cameraNum={uid}&width=1920&height=1080&req_fps=15"
                still_image = f"{self._base}://{self._host}:{self._port}/++image?cameraNum={uid}&width=1920&height=1080&quality=1&auth={self._auth}"

                cams = [camera for camera in self.device_data]
                if uid not in cams:
                    item = {
                        uid: {
                            "online": online,
                            "name": item.findtext("name"),
                            "image_width": int(item.findtext("width")),
                            "image_height": int(item.findtext("height")),
                            "mdsensitivity": int(item.findtext("mdsensitivity")),
                            "camera_model": item.findtext("devicename"),
                            "camera_type": item.findtext("devicetype"),
                            "address": item.findtext("address"),
                            "port": item.findtext("port"),
                            "mode_c": mode_c,
                            "mode_m": mode_m,
                            "mode_a": item.findtext("mode-a"),
                            "recording_mode": recording_mode,
                            "rtsp_video": rtsp_video,
                            "still_image": still_image,
                            "is_motion": False,
                        }
                    }
                    self.device_data.update(item)
                else:
                    self.device_data[uid]["recording_mode"] = recording_mode
                    self.device_data[uid]["online"] = online
                    self.device_data[uid]["mode_c"] = mode_c
                    self.device_data[uid]["mode_m"] = mode_m
                    self.device_data[uid]["mode_a"] = item.findtext("mode-a")

            except BaseException as e:
                _LOGGER.debug("Error when retrieving Camera Data: " + str(e))
                raise ResultError

    async def get_snapshot_image(self, camera_id):
        """ Returns a Snapshot image from a Camera. """
        endpoint = f"{self._base}://{self._host}:{self._port}/++image?cameraNum={camera_id}&width=1920&height=1080&quality=1&auth={self._auth}"
        response = await self.async_request("get", endpoint, True)
        return response

    async def set_recording_mode(self, camera_id, new_mode):
        """Sets the recording mode for a specific camera."""
        if new_mode == RECORDING_MODE_MOTION:
            schedule = 1
            capturemode = "M"
        elif new_mode == RECORDING_MODE_ALWAYS:
            schedule = 1
            capturemode = "C"
        elif new_mode == RECORDING_MODE_ACTION:
            schedule = 1
            capturemode = "A"
        else:
            schedule = 0
            capturemode = "CM"

        endpoint = f"{self._base}://{self._host}:{self._port}/++setSchedule?cameraNum={camera_id}&schedule={schedule}&mode={capturemode}&override=0&auth={self._auth}"
        response = await self.async_request("get", endpoint, False)
        if response == "OK":
            return new_mode
        else:
            raise ResultError(f"Recording mode could not be set for Camera {camera_id}")

    async def get_recording_mode(self, camera_id):
        """Returns recording mode for a specific camera."""
        endpoint = f"{self._base}://{self._host}:{self._port}/++cameramodes?cameraNum={camera_id}"
        response = await self.async_request("get", endpoint, False)
        
        items = []
        for line in response.split("\n"):
            if len(line) > 0:
                data = line.split(":")
                if data[0] == "C":
                    mode_c = data[1]
                elif data[0] == "M":
                    mode_m = data[1]
                else:
                    mode_a = data[1]

        items.append(RecordingSettings(
                {
                    "C": mode_c,
                    "M": mode_m,
                    "A": mode_a,
                }
            )
        )
        return items

    async def async_request(self, method: str, endpoint: str, rawdata: bool = False) -> dict:
        """Make a request against the SmartWeather API."""

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(
                method, endpoint
            ) as resp:
                resp.raise_for_status()
                data = await resp.read()
                if not rawdata:
                    decoded_content = data.decode("utf-8")
                    return decoded_content
                else:
                    return data
        except asyncio.TimeoutError:
            raise RequestError("Request to endpoint timed out: {endpoint}")
        except ClientError as err:
            raise RequestError(f"Error requesting data from {endpoint}: {err}")
        except:
            raise RequestError(f"Error occurred: {sys.exc_info()[1]}")
        finally:
            if not use_running_session:
                await session.close()

class Events:
    """The Event Loop Class."""
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = False,
        session: Optional[ClientSession] = None,
        event_callback=None,
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._session: ClientSession = session
        self._auth = b64encode(bytes(self._username + ":" + self._password, "utf-8")).decode()
        self._base = "http" if not use_ssl else "https"
        self.event_data = {}

        self._run_event = threading.Event()
        self._run_event.set()
        self.event_callback = event_callback
        self._thread = threading.Thread(target=self._connect)
        self._thread.setDaemon(True)
        self._thread.start()

    def _connect(self):
        """Connect to Stream and send data."""

        endpoint = f"{self._base}://{self._host}:{self._port}/++eventStream?version=3&format=multipart&auth={self._auth}"
        while self._run_event.is_set():
            response = self.session.get(endpoint)
            if response.status_code == 200:
                for line in response.content:
                    data = line.decode()
                    if data[:14].isnumeric():
                        event_arr = data.split(" ")
                        camera_id = event_arr[2]
                        event_id = event_arr[3]
                        if event_id in EVENT_TYPES:
                            uid = int(camera_id)
                            if event_id == EVENT_TYPE_TRIGGER_M:
                                self.device_data[uid]["is_motion"] = True
                            elif event_id == EVENT_TYPE_FILE:
                                self.device_data[uid]["is_motion"] = False
                            
                            if self.event_callback:
                                self.event_callback("")

    def close_connection(self):
        """ Close connection to event loop """
        self._run_event.clear()
        self._thread.join()
