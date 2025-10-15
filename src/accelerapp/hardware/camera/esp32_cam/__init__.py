"""
ESP32-CAM module for comprehensive camera support.
Integrates advanced features including TinyML, remote access, and multi-protocol streaming.
"""

from .core import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
    CameraSensor,
    FrameSize,
    PixelFormat,
)
from .streaming import (
    StreamingProtocol,
    StreamingManager,
    StreamConfig,
    StreamQuality,
)
from .ai_processing import (
    AIProcessor,
    DetectionModel,
    ModelConfig,
    InferenceBackend,
    DetectionResult,
)
from .motion_detection import (
    MotionDetector,
    MotionConfig,
    MotionAlgorithm,
    MotionEvent,
    QRScanner,
    QRCodeType,
)
from .remote_access import (
    RemoteAccess,
    AuthConfig,
    TunnelConfig,
    TunnelType,
    AuthMethod,
)
from .web_interface import (
    WebInterface,
    APIConfig,
    HTTPMethod,
)

__all__ = [
    # Core
    "ESP32Camera",
    "CameraVariant",
    "CameraConfig",
    "CameraSensor",
    "FrameSize",
    "PixelFormat",
    # Streaming
    "StreamingProtocol",
    "StreamingManager",
    "StreamConfig",
    "StreamQuality",
    # AI Processing
    "AIProcessor",
    "DetectionModel",
    "ModelConfig",
    "InferenceBackend",
    "DetectionResult",
    # Motion Detection
    "MotionDetector",
    "MotionConfig",
    "MotionAlgorithm",
    "MotionEvent",
    "QRScanner",
    "QRCodeType",
    # Remote Access
    "RemoteAccess",
    "AuthConfig",
    "TunnelConfig",
    "TunnelType",
    "AuthMethod",
    # Web Interface
    "WebInterface",
    "APIConfig",
    "HTTPMethod",
]
