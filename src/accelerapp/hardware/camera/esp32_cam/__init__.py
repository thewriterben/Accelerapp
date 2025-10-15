"""
ESP32-CAM module for comprehensive camera support.
Integrates advanced features including TinyML, remote access, and multi-protocol streaming.
"""

from .core import ESP32Camera, CameraVariant, CameraConfig, CameraSensor
from .streaming import StreamingProtocol, StreamingManager, StreamConfig
from .ai_processing import AIProcessor, DetectionModel, ModelConfig
from .motion_detection import MotionDetector, MotionConfig, QRScanner
from .remote_access import RemoteAccess, AuthConfig, TunnelConfig
from .web_interface import WebInterface, APIConfig

__all__ = [
    # Core
    "ESP32Camera",
    "CameraVariant",
    "CameraConfig",
    "CameraSensor",
    # Streaming
    "StreamingProtocol",
    "StreamingManager",
    "StreamConfig",
    # AI Processing
    "AIProcessor",
    "DetectionModel",
    "ModelConfig",
    # Motion Detection
    "MotionDetector",
    "MotionConfig",
    "QRScanner",
    # Remote Access
    "RemoteAccess",
    "AuthConfig",
    "TunnelConfig",
    # Web Interface
    "WebInterface",
    "APIConfig",
]
