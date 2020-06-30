"""Defines the Data Classes used."""
import logging

_LOGGER = logging.getLogger(__name__)

class CameraData:
    """A representation of Cameras in SecuritySpy."""

    def __init__(self, data):
        self._uid = data["uid"]
        self._online = data["online"]
        self._name = data["name"]
        self._image_width = data["image_width"]
        self._image_height = data["image_height"]
        self._mdsensitivity = data["mdsensitivity"]
        self._camera_model = data["camera_model"]
        self._mode_c = data["mode_c"]
        self._mode_m = data["mode_m"]
        self._mode_a = data["mode_a"]
        self._recording_mode = data["recording_mode"]
        self._rtsp_video = data["rtsp_video"]
        self._still_image = data["still_image"]

    @property
    def uid(self) -> int:
        """UID of Camera."""
        return self._uid

    @property
    def online(self) -> bool:
        """Return True if Camera Online."""
        return self._online

    @property
    def name(self) -> str:
        """Name of Camera."""
        return self._name

    @property
    def image_width(self) -> int:
        """Image Width."""
        return self._image_width

    @property
    def image_height(self) -> int:
        """Image Height."""
        return self._image_height

    @property
    def mdsensitivity(self) -> int:
        """Camera Motion Sensitivity."""
        return self._mdsensitivity

    @property
    def camera_model(self) -> str:
        """Model of Camera."""
        return self._camera_model

    @property
    def mode_c(self) -> str:
        """Continues recording Enabled."""
        return self._mode_c

    @property
    def mode_m(self) -> str:
        """Motion recording Enabled."""
        return self._mode_m

    @property
    def mode_a(self) -> str:
        """Action mode Enabled."""
        return self._mode_a

    @property
    def recording_mode(self) -> str:
        """Recording mode of Camera."""
        return self._recording_mode

    @property
    def rtsp_video(self) -> str:
        """Live Video Stream Address."""
        return self._rtsp_video

    @property
    def still_image(self) -> str:
        """Still Image Address."""
        return self._still_image
