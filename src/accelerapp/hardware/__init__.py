"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
Integrates WildCAM_ESP32 hardware generation capabilities.
Includes ESP32 Marauder, Flipper Zero, and ESP32-CAM support.
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
from .esp32_marauder import (
    ESP32Marauder,
    MarauderCommand,
    AttackType,
    WiFiNetwork,
    BluetoothDevice,
    PacketCapture,
)
from .flipper_zero import (
    FlipperZero,
    FlipperProtocol,
    RFIDType,
    NFCType,
    RFIDTag,
    NFCTag,
    SubGHzSignal,
    IRSignal,
)
from .camera import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
    StreamingProtocol,
)

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
    "ESP32Marauder",
    "MarauderCommand",
    "AttackType",
    "WiFiNetwork",
    "BluetoothDevice",
    "PacketCapture",
    "FlipperZero",
    "FlipperProtocol",
    "RFIDType",
    "NFCType",
    "RFIDTag",
    "NFCTag",
    "SubGHzSignal",
    "IRSignal",
    "ESP32Camera",
    "CameraVariant",
    "CameraConfig",
    "StreamingProtocol",
]
