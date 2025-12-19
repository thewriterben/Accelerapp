"""
ESP32-CAM hardware support module.
Provides camera control, streaming, AI processing, and remote access.
"""

from .core import (
    ESP32Camera,
    CameraConfig,
    CameraVariant,
    CameraSensor,
    FrameSize,
    PixelFormat,
    CameraModel,
    FrameFormat,
)
from .streaming import (
    StreamingManager,
    StreamingProtocol,
    StreamConfig,
)
from .ai_processing import (
    AIProcessor,
    DetectionModel,
    ModelConfig,
    DetectionResult,
    InferenceBackend,
)
from .motion_detection import (
    MotionDetector,
    MotionConfig,
    QRScanner,
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
)
from .security import (
    CameraSecurityManager,
    SecurityConfig,
    AccessLevel,
)
from .storage import (
    StorageManager,
    StorageConfig,
    StorageType,
)
from .digital_twin import (
    CameraDigitalTwin,
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
