"""
Hardware Abstraction Layer (HAL) for ESP32 Cheap Yellow Display.

Provides unified interfaces for CYD hardware components:
- ILI9341 TFT display controller
- XPT2046 touch controller
- GPIO and peripheral management
- Power management
- Temperature and performance sensors
"""

from .display import ColorDepth, DisplayConfig, DisplayDriver, DisplayRotation
from .gpio import GPIOManager, PinConfig, PinMode, PinState
from .power import PowerConfig, PowerManager, PowerMode
from .sensors import SensorMonitor, SensorReading, SensorType
from .touch import TouchConfig, TouchController, TouchEvent, TouchPoint

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
