"""
Hardware Abstraction Layer (HAL) for ESP32 Cheap Yellow Display.

Provides unified interfaces for CYD hardware components:
- ILI9341 TFT display controller
- XPT2046 touch controller
- GPIO and peripheral management
- Power management
- Temperature and performance sensors
"""

from .display import DisplayDriver, DisplayRotation, ColorDepth, DisplayConfig
from .touch import TouchController, TouchEvent, TouchPoint, TouchConfig
from .gpio import GPIOManager, PinMode, PinState, PinConfig
from .power import PowerManager, PowerMode, PowerConfig
from .sensors import SensorMonitor, SensorType, SensorReading

__all__ = [
    # Drivers
    "DisplayDriver",
    "TouchController",
    "GPIOManager",
    "PowerManager",
    "SensorMonitor",
    # Display
    "DisplayRotation",
    "ColorDepth",
    "DisplayConfig",
    # Touch
    "TouchEvent",
    "TouchPoint",
    "TouchConfig",
    # GPIO
    "PinMode",
    "PinState",
    "PinConfig",
    # Power
    "PowerMode",
    "PowerConfig",
    # Sensors
    "SensorType",
    "SensorReading",
]
