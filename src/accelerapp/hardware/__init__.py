"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
Integrates WildCAM_ESP32 hardware generation capabilities.
"""

from .abstraction import HardwareAbstractionLayer, HardwareComponent, ComponentFactory
from .protocols import (
    ProtocolType,
    I2CConfig,
    SPIConfig,
    CANConfig,
    ProtocolGenerator,
    DeviceDriverGenerator,
)
from .design import EnclosureGenerator, EnclosureDesign, BoardSupportMatrix, ESP32BoardType
from .environmental import EnvironmentalValidator, ValidationResult, EnvironmentType

__all__ = [
    "HardwareAbstractionLayer",
    "HardwareComponent",
    "ComponentFactory",
    "ProtocolType",
    "I2CConfig",
    "SPIConfig",
    "CANConfig",
    "ProtocolGenerator",
    "DeviceDriverGenerator",
    "EnclosureGenerator",
    "EnclosureDesign",
    "BoardSupportMatrix",
    "ESP32BoardType",
    "EnvironmentalValidator",
    "ValidationResult",
    "EnvironmentType",
]
