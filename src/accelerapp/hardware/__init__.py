"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
"""

from .abstraction import HardwareAbstractionLayer, HardwareComponent, ComponentFactory
from .protocols import (
    ProtocolType, I2CConfig, SPIConfig, CANConfig,
    ProtocolGenerator, DeviceDriverGenerator
)

__all__ = [
    'HardwareAbstractionLayer',
    'HardwareComponent',
    'ComponentFactory',
    'ProtocolType',
    'I2CConfig',
    'SPIConfig',
    'CANConfig',
    'ProtocolGenerator',
    'DeviceDriverGenerator',
]
