"""Test program for the SecuritySpy Wrapper.
   Remember to create settings.json before running.
"""
import argparse
import shlex
from enum import Enum
from typing import List

import asyncio
import aiohttp
import logging
import time
import json
from aiohttp import ClientSession
from base64 import b64encode

from pysecurityspy.events import SecuritySpyEvents
from pysecurityspy.errors import ResultError
from pysecurityspy.const import (
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
)

_LOGGER = logging.getLogger(__name__)

async def run_tests() -> None:

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
    ssevents = SecuritySpyEvents(host, port, username, password, use_ssl, session)
    await ssevents.registerCallback(update_callback)

    await ssevents.event_loop()
   
    await session.close()

def update_callback(data):
    _LOGGER.info("CALLBACK")
    cameras = [camera for camera in data]
    for camera in cameras:
        if camera == 1:
            _LOGGER.info("\n" +
                f"UID: {camera}" + "\n" + 
                f"NAME: {data[camera]['name']}" + "\n" + 
                f"TIMESTAMP: {data[camera]['timestamp']}" + "\n" +
                f"EVENT TYPE: {data[camera]['event_type']}" + "\n" +
                f"TRIGGER: {data[camera]['trigger_type']}" + "\n" +
                f"SCORE: {data[camera]['classify_score']}" + "\n" +
                f"SCORE_TYPE: {data[camera]['classify_type']}" + "\n" 
            )

    # for row in data:
    #     _LOGGER.info(f"TIME: {row.timestamp} - ID: {row.camera_id} - TYPE: {row.event_type} - X: {row.box_pos_x} - Y: {row.box_pos_y} - H: {row.box_pos_h} - W: {row.box_pos_w} '\n' TRIGGER: {row.trigger_type} - SCORE: {row.classify_score} - SCORE_TYPE: {row.classify_type} - IS_MOTION: {row.is_motion}")


# Start the program
loop = asyncio.get_event_loop()
loop.run_until_complete(run_tests())
loop.close()