"""Module to communicate with the SecuritySpy API."""
import logging
import asyncio
import xml.etree.ElementTree as ET

from typing import Optional
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
from base64 import b64encode

from pysecurityspy.const import (
    DEFAULT_TIMEOUT,
)
from pysecurityspy.errors import (
    InvalidCredentials,
    RequestError,
    ResultError,
)
from pysecurityspy.dataclasses import (
    CameraData,
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
        self._use_sll = use_ssl
        self._session: ClientSession = session

    async def async_get_cameras(self) -> None:
        return await self._get_camera_list()

    async def _get_camera_list(self) -> None:
        """Returns a list of the attached Cameras."""
        auth = b64encode(bytes(self._username + ":" + self._password, "utf-8")).decode()
        endpoint = 'http://%s:%s/++systemInfo&auth=%s' % (self._host, self._port, auth)
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
                recording_mode = "never"
                if mode_c == "armed":
                    recording_mode = "always"
                elif mode_m == "armed":
                    recording_mode = "motion"
                rtsp_video = "rtsp://%s:%s@%s:%s/++stream?cameraNum=%s" % (self._username, self._password, self._host, self._port, uid)
                still_image = "http://%s:%s/++image?cameraNum=%s&auth=%s" % (self._host, self._port, uid, auth)
                item = {
                    "uid": int(uid),
                    "online": online,
                    "name": item.findtext("name"),
                    "image_width": int(item.findtext("width")),
                    "image_height": int(item.findtext("height")),
                    "mdsensitivity": int(item.findtext("mdsensitivity")),
                    "camera_model": item.findtext("devicename"),
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
        
    async def async_request(self, method: str, endpoint: str) -> dict:
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
                decoded_content = data.decode("utf-8")
                return decoded_content
        except asyncio.TimeoutError:
            raise RequestError("Request to endpoint timed out: {endpoint}")
        except ClientError as err:
            if err.message == "Unauthorized":
                raise InvalidCredentials("Your Username/Password combination is not correct")
            elif err.message == "Not Found":
                raise ResultError("The Meteobridge cannot not be found on this IP Address")
            else:
                raise RequestError(
                    f"Error requesting data from {endpoint}: {err}"
                ) from None
        finally:
            if not use_running_session:
                await session.close()