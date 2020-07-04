"""Constant definitions for pysecurityspy."""

DEFAULT_TIMEOUT = 10

MODE_ARMED = "armed"
MODE_DISARMED = "disarmed"

RECORDING_MODE_ALWAYS = "always"
RECORDING_MODE_MOTION = "motion"
RECORDING_MODE_ACTION = "action"
RECORDING_MODE_NEVER = "never"

RECORDING_MODES = [
    RECORDING_MODE_ALWAYS,
    RECORDING_MODE_MOTION,
    RECORDING_MODE_ACTION,
    RECORDING_MODE_NEVER,
]

EVENT_TYPE_MOTION = "MOTION"
EVENT_TYPE_TRIGGER_M = "TRIGGER_M"
EVENT_TYPE_CLASIFY = "CLASSIFY"

EVENT_TYPES = [
    EVENT_TYPE_CLASIFY,
    EVENT_TYPE_MOTION,
    EVENT_TYPE_TRIGGER_M,
]

TRIGGER_TYPE = {
    0: "None",
    1: "Video motion detection",
    2: "Audio detection",
    4: "AppleScript",
    8: "Camera event",
    16: "Web server event",
    32: "Triggered by another camera",
    64: "Manual trigger",
    128: "Human",
    256: "Vehicle",
}