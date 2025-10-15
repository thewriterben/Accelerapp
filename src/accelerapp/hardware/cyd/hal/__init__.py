"""
Hardware Abstraction Layer (HAL) for ESP32 Cheap Yellow Display.

Provides unified interfaces for CYD hardware components:
- ILI9341 TFT display controller
- XPT2046 touch controller
- GPIO and peripheral management
- Power management
- Temperature and performance sensors
"""

from .display import DisplayDriver
from .touch import TouchController
from .gpio import GPIOManager
from .power import PowerManager
from .sensors import SensorMonitor

__all__ = [
    "DisplayDriver",
    "TouchController",
    "GPIOManager",
    "PowerManager",
    "SensorMonitor",
]
