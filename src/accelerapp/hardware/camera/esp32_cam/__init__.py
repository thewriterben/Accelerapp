"""
ESP32-CAM hardware support module.
Provides camera control, streaming, AI processing, and remote access.
"""

from .ai_processing import (
    AIProcessor,
    DetectionModel,
    DetectionResult,
    InferenceBackend,
    ModelConfig,
)
from .core import (
    CameraConfig,
    CameraModel,
    CameraSensor,
    CameraVariant,
    ESP32Camera,
    FrameFormat,
    FrameSize,
    PixelFormat,
)
from .digital_twin import (
    CameraDigitalTwin,
)
from .motion_detection import (
    MotionConfig,
    MotionDetector,
    QRScanner,
)
from .remote_access import (
    AuthConfig,
    AuthMethod,
    RemoteAccess,
    TunnelConfig,
    TunnelType,
)
from .security import (
    AccessLevel,
    CameraSecurityManager,
    SecurityConfig,
)
from .storage import (
    StorageConfig,
    StorageManager,
    StorageType,
)
from .streaming import (
    StreamConfig,
    StreamingManager,
    StreamingProtocol,
)
from .web_interface import (
    APIConfig,
    WebInterface,
)

__all__ = [
    # Core
    "ESP32Camera",
    "CameraConfig",
    "CameraVariant",
    "CameraSensor",
    "FrameSize",
    "PixelFormat",
    "CameraModel",
    "FrameFormat",
    # Streaming
    "StreamingManager",
    "StreamingProtocol",
    "StreamConfig",
    # AI Processing
    "AIProcessor",
    "DetectionModel",
    "ModelConfig",
    "DetectionResult",
    "InferenceBackend",
    # Motion Detection
    "MotionDetector",
    "MotionConfig",
    "QRScanner",
    # Remote Access
    "RemoteAccess",
    "AuthConfig",
    "TunnelConfig",
    "TunnelType",
    "AuthMethod",
    # Web Interface
    "WebInterface",
    "APIConfig",
    # Security
    "CameraSecurityManager",
    "SecurityConfig",
    "AccessLevel",
    # Storage
    "StorageManager",
    "StorageConfig",
    "StorageType",
    # Digital Twin
    "CameraDigitalTwin",
]
