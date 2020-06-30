"""Test program for the SecuritySpy Wrapper.
   Remember to create settings.json before running.
"""

import asyncio
import logging
import time
import json
from aiohttp import ClientSession

from pysecurityspy.server import SecuritySpyServer

_LOGGER = logging.getLogger(__name__)

async def camera_list():
    """Returns a list of configured Cameras."""

    start = time.time()
    logging.basicConfig(level=logging.DEBUG)
    _LOGGER.info("GETTING CAMERA LIST:")

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

    data = await secspy.async_get_cameras()
    print(data)

    #Close the session
    await session.close()

    end = time.time()
    _LOGGER.info("Execution time: %s seconds", end - start)

# Start the program
loop = asyncio.get_event_loop()
loop.run_until_complete(camera_list())
loop.close()