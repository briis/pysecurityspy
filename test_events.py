"""Test program for the SecuritySpy Wrapper.
   Remember to create settings.json before running.
"""

import asyncio
import aiohttp
import logging
import time
import json
from aiohttp import ClientSession
from base64 import b64encode

from pysecurityspy.server import SecuritySpyServer
from pysecurityspy.errors import ResultError
from pysecurityspy.const import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
)

_LOGGER = logging.getLogger(__name__)
run_event_loop = False

async def run_tests():
    """Run all the tests."""
    start = time.time()
    logging.basicConfig(level=logging.DEBUG)

   # Read the settings.json file
    path_index = __file__.rfind("/")
    if path_index == -1:
        filepath = "settings.json"
    else:
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
    auth = b64encode(bytes(username + ":" + password, "utf-8")).decode()
    global run_event_loop
    run_event_loop = True
    await read_events(session, host, port, auth)

    time.sleep(39)
    run_event_loop = False
    #Close the session
    await session.close()

    end = time.time()
    _LOGGER.info("Execution time: %s seconds", end - start)

async def read_events(session, host, port, auth):
    """Hopefully reads the events coming from SecuritySpy."""
    url = f"http://{host}:{port}/++eventStream?version=3&format=multipart&auth={auth}"
    _LOGGER.debug(run_event_loop)
    async with session.request("get", url) as resp:
        async for line in resp.content:
            if run_event_loop == False:
                _LOGGER.debug("BREAK LOOP")
                break
            data = line.decode()
            if data[:14].isnumeric():
                event_arr = data.split(" ")
                camera_id = event_arr[2]
                if event_arr[3] == "MOTION" and camera_id != "X":
                    _LOGGER.info(f"MOTION DETECTED - CAMERA {camera_id}")
                elif event_arr[3] == "TRIGGER_M" and camera_id != "X":
                    _LOGGER.info(f"MOTION CAPTURED: REASON: {event_arr[4]} - CAMERA {camera_id}")


# Start the program
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run_tests())
finally:
    loop.close()