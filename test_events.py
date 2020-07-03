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

async def main() -> None:

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

    eventlog = asyncio.create_task(ssevents.event_loop())

    await asyncio.sleep(60)
    
    eventlog.cancel()
    await session.close()
    try:
        await eventlog
    except asyncio.CancelledError:
        pass

def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()