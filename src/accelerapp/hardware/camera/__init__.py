"""
ESP32-CAM hardware integration module for Accelerapp.
Provides comprehensive camera control, streaming, and AI processing capabilities.
"""

from .esp32_cam.core import ESP32Camera, CameraConfig, CameraResolution
from .esp32_cam.streaming import StreamingServer, StreamProtocol
from .esp32_cam.motion_detection import MotionDetector, MotionEvent
from .esp32_cam.digital_twin import CameraDigitalTwin
from .esp32_cam.web_interface import CameraWebInterface
from .esp32_cam.storage import StorageManager
from .esp32_cam.security import CameraSecurityManager

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
