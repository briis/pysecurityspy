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
from pysecurityspy.const import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
)

_LOGGER = logging.getLogger(__name__)

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
    secspy = SecuritySpyServer(host, port, username, password, use_ssl, session)

    cameras = await camera_list(secspy, True)
    await get_server_info(secspy)

    # await snapshots(secspy, cameras)
    # await recording_mode(secspy, 2, RECORDING_MODE_MOTION)
    # await get_recording_mode(secspy, 2)

    #Close the session
    await session.close()

    end = time.time()
    _LOGGER.info("Execution time: %s seconds", end - start)

async def camera_list(secspy, output: bool = True):
    """Returns a list of configured Cameras."""
    cnt = 0
    while cnt < 10:
        _LOGGER.info(f"GETTING CAMERA LIST: ROUND {cnt}")

        try:
            cameras = []
            data = await secspy.update()
            cameras = [camera for camera in data]
            _LOGGER.info(cameras)
            for camera in cameras:
                if output and camera == 2:
                    _LOGGER.info("\n" +
                        f"UID: {camera}" + "\n" + 
                        f"ONLINE: {data[camera]['online']}" + "\n" + 
                        f"NAME: {data[camera]['name']}" + "\n" + 
                        f"IMAGE WIDTH: {data[camera]['image_width']}" + "\n" +
                        f"IMAGE HEIGHT: {data[camera]['image_height']}" + "\n" +
                        f"SENSITIVITY: {data[camera]['mdsensitivity']}" + "\n" +
                        f"MODEL: {data[camera]['camera_model']}" + "\n" +
                        f"TYPE: {data[camera]['camera_type']}" + "\n" +
                        f"ADDRESS: {data[camera]['address']}" + "\n" +
                        f"PORT: {data[camera]['port']}" + "\n" +
                        f"MODE_C: {data[camera]['mode_c']}" + "\n" + 
                        f"MODE_M: {data[camera]['mode_m']}" + "\n" + 
                        f"MODE_A: {data[camera]['mode_a']}" + "\n" +
                        f"RECORDING MODE: {data[camera]['recording_mode']}" + "\n" +
                        f"VIDEO: {data[camera]['rtsp_video']}" + "\n" +
                        f"IMAGE: {data[camera]['still_image']}" + "\n"
                    )
            cnt = cnt + 1
            await asyncio.sleep(2)

        except ResultError:
            _LOGGER.info("Something went wrong in retrieving data")

    return cameras

async def snapshots(secspy, cameras):
    """Save a snapshot of each available camera."""
    _LOGGER.info("SAVE SNAPSHOTS:")

    for camera in cameras:
        filename = f"snapshot_{camera}.jpg"
        image = await secspy.get_snapshot_image(camera)
        with open(filename, "wb") as img_file:
            _LOGGER.info(f"Writing snapshot {filename}")
            img_file.write(image)
            time.sleep(1)

async def get_server_info(secspy):
    """Display Server Information."""
    result = await secspy.get_server_information()
    _LOGGER.info(f"SERVER {result['name']} - VERSION {result['version']} - HOST {result['host']}")

async def recording_mode(secspy, camera_id, recording_mode):
    """Set recording mode for cameras."""
    _LOGGER.info("SET RECORDING MODE:")

    result = await secspy.set_recording_mode(camera_id, recording_mode)
    _LOGGER.info(result)

async def get_recording_mode(secspy, camera_id):
    """Set recording mode for cameras."""
    _LOGGER.info("GET RECORDING MODE:")

    result = await secspy.get_recording_mode(camera_id)
    for row in result:
        _LOGGER.info(f"C: {row.mode_always} - M: {row.mode_motion} - A: {row.mode_action} - R: {row.is_recording} ")


# Start the program
loop = asyncio.get_event_loop()
loop.run_until_complete(run_tests())
loop.close()