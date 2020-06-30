"""Test program for the SecuritySpy Wrapper.
   Remember to create settings.json before running.
"""

import asyncio
import logging
import time
import json

_LOGGER = logging.getLogger(__name__)

async def camera_list():
    """Returns a list of configured Cameras."""

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

    print(host)

# Start the program
loop = asyncio.get_event_loop()
loop.run_until_complete(camera_list())
loop.close()