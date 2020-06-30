"""Constant definitions for pysecurityspy."""

DEFAULT_TIMEOUT = 10

TRIGGER_TYPE = {
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