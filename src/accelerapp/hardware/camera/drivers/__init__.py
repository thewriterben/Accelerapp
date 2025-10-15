"""
Camera sensor drivers for ESP32-CAM.
"""

from .ov2640 import OV2640Driver
from .ov3660 import OV3660Driver

__all__ = [
    "OV2640Driver",
    "OV3660Driver",
]
