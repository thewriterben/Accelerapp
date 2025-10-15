"""
ESP32-CAM core module.
Provides camera interface, configuration, and control.
"""

from .core import ESP32Camera, CameraConfig, CameraResolution
from .streaming import StreamingServer, StreamProtocol
from .motion_detection import MotionDetector, MotionEvent
from .digital_twin import CameraDigitalTwin
from .web_interface import CameraWebInterface
from .storage import StorageManager
from .security import CameraSecurityManager

__all__ = [
    "ESP32Camera",
    "CameraConfig",
    "CameraResolution",
    "StreamingServer",
    "StreamProtocol",
    "MotionDetector",
    "MotionEvent",
    "CameraDigitalTwin",
    "CameraWebInterface",
    "StorageManager",
    "CameraSecurityManager",
]
