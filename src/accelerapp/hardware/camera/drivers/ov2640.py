"""
OV2640 camera sensor driver.
Supports the most common sensor used in ESP32-CAM modules.
"""

from typing import Dict, Any


class OV2640Driver:
    """
    Driver for OV2640 camera sensor.
    2 Megapixel CMOS image sensor with UXGA resolution.
    """
    
    SENSOR_ID = 0x2642
    SENSOR_NAME = "OV2640"
    
    # Supported resolutions
    RESOLUTIONS = {
        "QVGA": (320, 240),
        "VGA": (640, 480),
        "SVGA": (800, 600),
        "XGA": (1024, 768),
        "SXGA": (1280, 1024),
        "UXGA": (1600, 1200),
    }
    
    def __init__(self):
        """Initialize OV2640 driver."""
        self._initialized = False
        self._current_resolution = "VGA"
    
    def initialize(self) -> bool:
        """
        Initialize sensor hardware.
        
        Returns:
            True if initialization successful
        """
        # In real implementation, would configure I2C communication
        # and initialize sensor registers
        self._initialized = True
        return True
    
    def set_resolution(self, resolution: str) -> bool:
        """
        Set image resolution.
        
        Args:
            resolution: Resolution name (QVGA, VGA, etc.)
            
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
            "max_resolution": "UXGA",
            "max_width": 1600,
            "max_height": 1200,
            "supported_resolutions": list(self.RESOLUTIONS.keys()),
            "supports_jpeg": True,
            "supports_rgb": True,
            "supports_yuv": True,
            "has_autofocus": False,
            "has_flash": False,
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
