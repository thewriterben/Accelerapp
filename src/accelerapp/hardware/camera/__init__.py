"""
Camera hardware support for Accelerapp.
Provides comprehensive ESP32-CAM integration with advanced features.
"""

from .esp32_cam import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
    StreamingProtocol,
)

__all__ = [
    "ESP32Camera",
    "CameraVariant",
    "CameraConfig",
    "StreamingProtocol",
]
