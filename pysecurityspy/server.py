"""Module to communicate with the SecuritySpy API."""
import logging
import asyncio
import sys
import xml.etree.ElementTree as ET

from typing import Optional
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from base64 import b64encode

from pysecurityspy.const import (
    DEFAULT_TIMEOUT,
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
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

    async def async_get_cameras(self) -> None:
        return await self._get_camera_list()

    async def _get_camera_list(self) -> None:
        """Returns a list of the attached Cameras."""
        endpoint = f"{self._base}://{self._host}:{self._port}/++systemInfo&auth={self._auth}"
        _LOGGER.debug(endpoint)
        response = await self.async_request("get", endpoint)

        cameras = ET.fromstring(response)
        items = []
        for item in cameras.iterfind('cameralist/camera'):
            try:
                uid = item.findtext("number")
                if item.findtext("connected") == "yes":
                    online = True
                else:
                    online = False
                mode_c = item.findtext("mode-c")
                mode_m = item.findtext("mode-m")
                recording_mode = RECORDING_MODE_NEVER
                if mode_c == "armed":
                    recording_mode = RECORDING_MODE_ALWAYS
                elif mode_m == "armed":
                    recording_mode = RECORDING_MODE_MOTION
                rtsp_video = f"rtsp://{self._username}:{self._password}@{self._host}:{self._port}/++stream?cameraNum={uid}&width=1920&height=1080&req_fps=15"
                still_image = f"{self._base}://{self._host}:{self._port}/++image?cameraNum={uid}&width=1920&height=1080&quality=1&auth={self._auth}"
                item = {
                    "uid": int(uid),
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
                }
                items.append(CameraData(item))

            except BaseException as e:
                _LOGGER.debug("Error when retrieving Camera Data: " + str(e))
                raise ResultError

        return items

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
            capturemode = "CMA"

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