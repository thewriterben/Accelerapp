"""
Core ESP32-CAM interface implementation.
Provides hardware abstraction for ESP32-CAM devices with support for multiple board variants.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json


class CameraResolution(Enum):
    """Supported camera resolutions."""
    QVGA = "320x240"      # 320x240
    VGA = "640x480"       # 640x480
    SVGA = "800x600"      # 800x600
    XGA = "1024x768"      # 1024x768
    HD = "1280x720"       # 720p
    SXGA = "1280x1024"    # 1280x1024
    UXGA = "1600x1200"    # 1600x1200


class CameraModel(Enum):
    """Supported camera sensor models."""
    OV2640 = "ov2640"
    OV3660 = "ov3660"
    OV5640 = "ov5640"


class FrameFormat(Enum):
    """Image frame formats."""
    JPEG = "jpeg"
    RGB565 = "rgb565"
    YUV422 = "yuv422"
    GRAYSCALE = "grayscale"


@dataclass
class CameraConfig:
    """Configuration for ESP32-CAM device."""
    device_id: str
    board_type: str = "ai_thinker"  # ai_thinker, esp32_cam, esp32_s3_cam, ttgo
    camera_model: CameraModel = CameraModel.OV2640
    resolution: CameraResolution = CameraResolution.VGA
    frame_format: FrameFormat = FrameFormat.JPEG
    jpeg_quality: int = 10  # 0-63, lower is higher quality
    brightness: int = 0     # -2 to 2
    contrast: int = 0       # -2 to 2
    saturation: int = 0     # -2 to 2
    vertical_flip: bool = False
    horizontal_mirror: bool = False
    frame_rate: int = 10    # Frames per second
    pin_config: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default pin configuration based on board type."""
        if not self.pin_config:
            self.pin_config = self._get_default_pins()
    
    def _get_default_pins(self) -> Dict[str, int]:
        """Get default pin configuration for board type."""
        if self.board_type in ["ai_thinker", "esp32_cam"]:
            return {
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
            return {
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
        return {}


class ESP32Camera:
    """
    Main interface for ESP32-CAM hardware.
    Provides camera control, configuration, and image capture capabilities.
    """
    
    def __init__(self, config: CameraConfig):
        """
        Initialize ESP32-CAM interface.
        
        Args:
            config: Camera configuration
        """
        self.config = config
        self._initialized = False
        self._streaming = False
        self._capture_count = 0
        self._stats = {
            "captures": 0,
            "streams": 0,
            "errors": 0,
            "uptime": 0,
        }
    
    def initialize(self) -> bool:
        """
        Initialize camera hardware.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        # In a real implementation, this would initialize the camera hardware
        # For now, we simulate successful initialization
        self._initialized = True
        return True
    
    def capture_image(self) -> Optional[Dict[str, Any]]:
        """
        Capture a single image frame.
        
        Returns:
            Image data dictionary with metadata
        """
        if not self._initialized:
            if not self.initialize():
                return None
        
        self._capture_count += 1
        self._stats["captures"] += 1
        
        # Return simulated capture metadata
        return {
            "device_id": self.config.device_id,
            "timestamp": "2025-10-15T01:12:23.332Z",
            "resolution": self.config.resolution.value,
            "format": self.config.frame_format.value,
            "size_bytes": 0,  # Would contain actual image data
            "capture_number": self._capture_count,
        }
    
    def start_streaming(self) -> bool:
        """
        Start video streaming.
        
        Returns:
            True if streaming started successfully
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        self._streaming = True
        self._stats["streams"] += 1
        return True
    
    def stop_streaming(self) -> bool:
        """
        Stop video streaming.
        
        Returns:
            True if streaming stopped successfully
        """
        self._streaming = False
        return True
    
    def is_streaming(self) -> bool:
        """Check if camera is currently streaming."""
        return self._streaming
    
    def set_resolution(self, resolution: CameraResolution) -> bool:
        """
        Change camera resolution.
        
        Args:
            resolution: New resolution setting
            
        Returns:
            True if successful
        """
        self.config.resolution = resolution
        return True
    
    def set_quality(self, quality: int) -> bool:
        """
        Set JPEG quality (0-63, lower is better).
        
        Args:
            quality: Quality setting
            
        Returns:
            True if successful
        """
        if 0 <= quality <= 63:
            self.config.jpeg_quality = quality
            return True
        return False
    
    def set_brightness(self, brightness: int) -> bool:
        """
        Set camera brightness (-2 to 2).
        
        Args:
            brightness: Brightness level
            
        Returns:
            True if successful
        """
        if -2 <= brightness <= 2:
            self.config.brightness = brightness
            return True
        return False
    
    def set_flip(self, vertical: bool = False, horizontal: bool = False) -> bool:
        """
        Set image flip settings.
        
        Args:
            vertical: Enable vertical flip
            horizontal: Enable horizontal mirror
            
        Returns:
            True if successful
        """
        self.config.vertical_flip = vertical
        self.config.horizontal_mirror = horizontal
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera status and statistics.
        
        Returns:
            Status dictionary
        """
        return {
            "device_id": self.config.device_id,
            "initialized": self._initialized,
            "streaming": self._streaming,
            "resolution": self.config.resolution.value,
            "format": self.config.frame_format.value,
            "board_type": self.config.board_type,
            "camera_model": self.config.camera_model.value,
            "stats": self._stats.copy(),
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Configuration dictionary
        """
        return {
            "device_id": self.config.device_id,
            "board_type": self.config.board_type,
            "camera_model": self.config.camera_model.value,
            "resolution": self.config.resolution.value,
            "frame_format": self.config.frame_format.value,
            "jpeg_quality": self.config.jpeg_quality,
            "brightness": self.config.brightness,
            "contrast": self.config.contrast,
            "saturation": self.config.saturation,
            "vertical_flip": self.config.vertical_flip,
            "horizontal_mirror": self.config.horizontal_mirror,
            "frame_rate": self.config.frame_rate,
        }
    
    def reset(self) -> bool:
        """
        Reset camera to default settings.
        
        Returns:
            True if successful
        """
        self.config.brightness = 0
        self.config.contrast = 0
        self.config.saturation = 0
        self.config.vertical_flip = False
        self.config.horizontal_mirror = False
        return True
    
    def shutdown(self) -> bool:
        """
        Shutdown camera and release resources.
        
        Returns:
            True if successful
        """
        if self._streaming:
            self.stop_streaming()
        self._initialized = False
        return True
