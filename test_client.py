"""Test program for the SecuritySpy Wrapper.
   Remember to create settings.json before running.
"""

import asyncio
import logging
import time
import json
from aiohttp import ClientSession

from pysecurityspy.server import SecuritySpyServer
from pysecurityspy.errors import ResultError

_LOGGER = logging.getLogger(__name__)

async def run_tests():
    """Run all the tests."""
    start = time.time()
    logging.basicConfig(level=logging.DEBUG)

   # Read the settings.json file
    path_index = __file__.rfind("/")
    top_path = __file__[0:path_index]
    filepath = f"{top_path}/settings.json"
    with open(filepath) as json_file:
        data = json.load(json_file)
        host = data["connection"]["host"]
        port = data["connection"]["port"]
        username = data["connection"]["username"]
        password = data["connection"]["password"]
        use_ssl = data["connection"]["use_ssl"]

    session = ClientSession()
    secspy = SecuritySpyServer(host, port, username, password, use_ssl, session)

    await camera_list(secspy)

    #Close the session
    await session.close()

    end = time.time()
    _LOGGER.info("Execution time: %s seconds", end - start)

async def camera_list(secspy):
    """Returns a list of configured Cameras."""

    _LOGGER.info("GETTING CAMERA LIST:")

    try:
        data = await secspy.async_get_cameras()
        for row in data:
            _LOGGER.info("\n" +
                f"UID: {row.uid}" + "\n" + 
                f"ONLINE: {row.online}" + "\n" + 
                f"NAME: {row.name}" + "\n" + 
                f"IMAGE WIDTH: {row.image_width}" + "\n" + 
                f"IMAGE HEIGHT: {row.image_height}" + "\n" +
                f"SENSITIVITY: {row.mdsensitivity}" + "\n" +
                f"MODEL: {row.camera_model}" + "\n" + 
                f"MODE_C: {row.mode_c}" + "\n" + 
                f"MODE_M: {row.mode_m}" + "\n" + 
                f"MODE_A: {row.mode_a}" + "\n" +
                f"RECORDING MODE: {row.recording_mode}" + "\n" +
                f"VIDEO: {row.rtsp_video}" + "\n" +
                f"IMAGE: {row.still_image}" + "\n"
            )

    except ResultError:
        _LOGGER.info("Something went wrong in retrieving data")


# Start the program
loop = asyncio.get_event_loop()
loop.run_until_complete(run_tests())
loop.close()