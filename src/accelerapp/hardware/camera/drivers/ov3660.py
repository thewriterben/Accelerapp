"""
OV3660 camera sensor driver.
Alternative higher-resolution sensor for ESP32-CAM.
"""

from typing import Dict, Any


class OV3660Driver:
    """
    Driver for OV3660 camera sensor.
    3 Megapixel CMOS image sensor with better low-light performance.
    """
    
    SENSOR_ID = 0x3660
    SENSOR_NAME = "OV3660"
    
    # Supported resolutions
    RESOLUTIONS = {
        "VGA": (640, 480),
        "SVGA": (800, 600),
        "XGA": (1024, 768),
        "HD": (1280, 720),
        "SXGA": (1280, 1024),
        "UXGA": (1600, 1200),
        "QXGA": (2048, 1536),
    }
    
    def __init__(self):
        """Initialize OV3660 driver."""
        self._initialized = False
        self._current_resolution = "HD"
    
    def initialize(self) -> bool:
        """
        Initialize sensor hardware.
        
        Returns:
            True if initialization successful
        """
        self._initialized = True
        return True
    
    def set_resolution(self, resolution: str) -> bool:
        """
        Set image resolution.
        
        Args:
            resolution: Resolution name
            
        Returns:
            True if successful
        """
        if resolution not in self.RESOLUTIONS:
            return False
        
        self._current_resolution = resolution
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get sensor capabilities.
        
        Returns:
            Capabilities dictionary
        """
        return {
            "sensor_id": self.SENSOR_ID,
            "sensor_name": self.SENSOR_NAME,
            "max_resolution": "QXGA",
            "max_width": 2048,
            "max_height": 1536,
            "supported_resolutions": list(self.RESOLUTIONS.keys()),
            "supports_jpeg": True,
            "supports_rgb": True,
            "supports_yuv": True,
            "has_autofocus": False,
            "has_flash": False,
            "low_light_performance": "improved",
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current sensor status.
        
        Returns:
            Status dictionary
        """
        return {
            "initialized": self._initialized,
            "sensor_name": self.SENSOR_NAME,
            "current_resolution": self._current_resolution,
            "resolution_pixels": self.RESOLUTIONS.get(self._current_resolution),
        }
