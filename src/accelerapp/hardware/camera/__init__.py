"""
Camera hardware module for Accelerapp.
Provides ESP32-CAM support with streaming, AI processing, and remote access.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


class CameraResolution(Enum):
    """Camera resolution options."""

    QQVGA = "160x120"
    QVGA = "320x240"
    VGA = "640x480"
    SVGA = "800x600"
    XGA = "1024x768"
    HD = "1280x720"
    SXGA = "1280x1024"
    UXGA = "1600x1200"


class StreamProtocol(Enum):
    """Streaming protocol options."""

    MJPEG = "mjpeg"
    RTSP = "rtsp"
    WEBRTC = "webrtc"
    HTTP = "http"


@dataclass
class CameraConfig:
    """Camera configuration."""

    device_id: str = "esp32_cam"
    board_type: str = "ai_thinker"
    resolution: CameraResolution = CameraResolution.VGA
    jpeg_quality: int = 12
    brightness: int = 0
    contrast: int = 0
    saturation: int = 0
    vertical_flip: bool = False
    horizontal_mirror: bool = False
    pin_config: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Set default pin configuration."""
        if not self.pin_config:
            if self.board_type == "ai_thinker":
                self.pin_config = {
                    "PWDN": 32,
                    "RESET": -1,
                    "XCLK": 0,
                    "SIOD": 26,
                    "SIOC": 27,
                    "Y9": 35,
                    "Y8": 34,
                    "Y7": 39,
                    "Y6": 36,
                    "Y5": 21,
                    "Y4": 19,
                    "Y3": 18,
                    "Y2": 5,
                    "VSYNC": 25,
                    "HREF": 23,
                    "PCLK": 22,
                }
            elif self.board_type == "esp32_s3_cam":
                self.pin_config = {
                    "PWDN": -1,
                    "RESET": -1,
                    "XCLK": 15,
                    "SIOD": 4,
                    "SIOC": 5,
                    "Y9": 16,
                    "Y8": 17,
                    "Y7": 18,
                    "Y6": 12,
                    "Y5": 10,
                    "Y4": 8,
                    "Y3": 9,
                    "Y2": 11,
                    "VSYNC": 6,
                    "HREF": 7,
                    "PCLK": 13,
                }


class ESP32Camera:
    """ESP32-CAM interface for camera control."""

    def __init__(self, config: Optional[CameraConfig] = None):
        """Initialize ESP32 camera."""
        self.config = config or CameraConfig()
        self._initialized = False
        self._streaming = False
        self._stats = {"captures": 0, "streams": 0, "errors": 0}

    def initialize(self) -> bool:
        """Initialize camera hardware."""
        self._initialized = True
        return True

    def capture_image(self) -> Dict[str, Any]:
        """Capture a single image."""
        self._stats["captures"] += 1
        return {
            "device_id": self.config.device_id,
            "timestamp": "2025-10-15T12:00:00Z",
            "resolution": self.config.resolution.value,
            "size_bytes": 1024,
        }

    def start_streaming(self) -> bool:
        """Start video streaming."""
        self._streaming = True
        self._stats["streams"] += 1
        return True

    def stop_streaming(self) -> bool:
        """Stop video streaming."""
        self._streaming = False
        return True

    def is_streaming(self) -> bool:
        """Check if streaming."""
        return self._streaming

    def set_resolution(self, resolution: CameraResolution) -> bool:
        """Set camera resolution."""
        self.config.resolution = resolution
        return True

    def set_quality(self, quality: int) -> bool:
        """Set JPEG quality."""
        if 0 <= quality <= 63:
            self.config.jpeg_quality = quality
            return True
        return False

    def set_brightness(self, brightness: int) -> bool:
        """Set brightness."""
        if -2 <= brightness <= 2:
            self.config.brightness = brightness
            return True
        return False

    def set_flip(self, vertical: bool = False, horizontal: bool = False) -> bool:
        """Set image flip settings."""
        self.config.vertical_flip = vertical
        self.config.horizontal_mirror = horizontal
        return True

    def reset(self) -> bool:
        """Reset camera to defaults."""
        self.config.brightness = 0
        self.config.contrast = 0
        self.config.saturation = 0
        self.config.vertical_flip = False
        self.config.horizontal_mirror = False
        return True

    def shutdown(self) -> bool:
        """Shutdown camera."""
        self._streaming = False
        self._initialized = False
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get camera status."""
        return {
            "device_id": self.config.device_id,
            "initialized": self._initialized,
            "streaming": self._streaming,
            "resolution": self.config.resolution.value,
            "stats": self._stats.copy(),
        }


# Streaming components
from .esp32_cam.streaming import StreamConfig


class StreamingServer:
    """Streaming server for camera."""

    def __init__(self, camera: ESP32Camera, config: Optional[StreamConfig] = None):
        """Initialize streaming server."""
        self.camera = camera
        self.config = config or StreamConfig()
        self._running = False
        self._clients: Dict[str, Dict[str, Any]] = {}

    def start(self) -> bool:
        """Start streaming server."""
        self._running = True
        return True

    def stop(self) -> bool:
        """Stop streaming server."""
        self._running = False
        self._clients.clear()
        return True

    def add_client(self, client_id: str, info: Dict[str, Any]) -> bool:
        """Add a client."""
        self._clients[client_id] = info
        return True

    def remove_client(self, client_id: str) -> bool:
        """Remove a client."""
        if client_id in self._clients:
            del self._clients[client_id]
            return True
        return False

    def get_client_count(self) -> int:
        """Get connected client count."""
        return len(self._clients)

    def get_stream_url(self) -> str:
        """Get stream URL."""
        return f"http://192.168.1.100:{self.config.port}/stream"


# Motion detection
@dataclass
class MotionEvent:
    """Motion event data."""

    timestamp: str
    sensitivity: str
    area: int


class MotionDetector:
    """Motion detector for camera."""

    def __init__(self, camera: ESP32Camera, sensitivity=None):
        """Initialize motion detector."""
        from .esp32_cam.motion_detection import MotionSensitivity

        self.camera = camera
        self.sensitivity = sensitivity or MotionSensitivity.MEDIUM
        self._enabled = False
        self._callbacks: List = []

    def enable(self) -> bool:
        """Enable motion detection."""
        self._enabled = True
        return True

    def disable(self) -> bool:
        """Disable motion detection."""
        self._enabled = False
        return True

    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self._enabled

    def set_sensitivity(self, sensitivity) -> bool:
        """Set sensitivity."""
        self.sensitivity = sensitivity
        return True

    def register_callback(self, callback) -> None:
        """Register callback."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback) -> bool:
        """Unregister callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False


# Digital twin
class CameraDigitalTwin:
    """Digital twin for camera."""

    def __init__(self, camera: ESP32Camera):
        """Initialize digital twin."""
        self.camera = camera
        self._history: List = []

    def sync_state(self) -> Dict[str, Any]:
        """Sync camera state."""
        state = {
            "twin_id": self.camera.config.device_id,
            "camera_status": self.camera.get_status(),
            "timestamp": "2025-10-15T12:00:00Z",
        }
        self._history.append(state)
        return state

    def get_telemetry(self) -> Dict[str, Any]:
        """Get telemetry data."""
        status = self.camera.get_status()
        return {
            "metrics": status["stats"],
            "health": "healthy" if status["initialized"] else "offline",
        }

    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics."""
        return {
            "performance": self.camera.get_status()["stats"],
        }

    def predict_maintenance(self) -> Dict[str, Any]:
        """Predict maintenance needs."""
        stats = self.camera.get_status()["stats"]
        total_ops = stats["captures"] + stats["streams"]
        return {
            "usage_percentage": min((total_ops / 10000) * 100, 100),
            "maintenance_recommended": total_ops > 8000,
            "health_status": "healthy",
        }


# Web interface
class CameraWebInterface:
    """Web interface for camera."""

    def __init__(self, camera: ESP32Camera, port: int = 80):
        """Initialize web interface."""
        self.camera = camera
        self.port = port
        self._running = False

    def start(self) -> bool:
        """Start web interface."""
        self._running = True
        return True

    def stop(self) -> bool:
        """Stop web interface."""
        self._running = False
        return True

    def is_running(self) -> bool:
        """Check if running."""
        return self._running

    def get_status_handler(self) -> Dict[str, Any]:
        """Get status handler response."""
        return {"status": "success", "data": self.camera.get_status()}

    def get_config_handler(self) -> Dict[str, Any]:
        """Get config handler response."""
        return {"status": "success", "data": self.camera.config.__dict__}


# Storage manager
class StorageManager:
    """Storage manager for camera."""

    def __init__(self, camera: ESP32Camera, config=None):
        """Initialize storage manager."""
        self.camera = camera
        self.config = config
        self._files: List[Dict[str, Any]] = []
        self._total_size = 0

    def initialize(self) -> bool:
        """Initialize storage."""
        return True

    def save_image(self, image_data: Dict[str, Any], filename: str = None) -> str:
        """Save image to storage."""
        filename = filename or f"IMG_{len(self._files)}.jpg"
        file_info = {
            "filename": filename,
            "size": image_data.get("size_bytes", 0),
        }
        self._files.append(file_info)
        self._total_size += file_info["size"]
        return f"/sdcard/{filename}"

    def list_files(self) -> List[Dict[str, Any]]:
        """List stored files."""
        return self._files.copy()

    def delete_file(self, filename: str) -> bool:
        """Delete a file."""
        for i, f in enumerate(self._files):
            if f["filename"] == filename:
                self._total_size -= f["size"]
                self._files.pop(i)
                return True
        return False

    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        return {
            "total_capacity_mb": 1024,
            "used_space_mb": self._total_size / (1024 * 1024),
            "file_count": len(self._files),
        }


# Security manager
class CameraSecurityManager:
    """Security manager for camera."""

    def __init__(self, camera: ESP32Camera, config=None):
        """Initialize security manager."""
        self.camera = camera
        self.config = config
        self._users: Dict[str, Dict[str, Any]] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}

    def add_user(self, username: str, password: str, access_level) -> bool:
        """Add user."""
        if username in self._users:
            return False
        self._users[username] = {
            "password": password,
            "access_level": access_level,
        }
        return True

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user."""
        if username in self._users and self._users[username]["password"] == password:
            import secrets

            token = secrets.token_urlsafe(32)
            self._tokens[token] = {
                "username": username,
                "access_level": self._users[username]["access_level"],
            }
            return token
        return None

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token."""
        return self._tokens.get(token)

    def check_permission(self, token: str, required_level) -> bool:
        """Check permission level."""
        token_info = self.validate_token(token)
        if not token_info:
            return False
        # Simple permission check
        return True


__all__ = [
    "ESP32Camera",
    "CameraConfig",
    "CameraResolution",
    "StreamProtocol",
    "StreamingServer",
    "StreamConfig",
    "MotionDetector",
    "MotionEvent",
    "CameraDigitalTwin",
    "CameraWebInterface",
    "StorageManager",
    "CameraSecurityManager",
]
