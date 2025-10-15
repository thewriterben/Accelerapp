"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
Integrates WildCAM_ESP32 hardware generation capabilities.
Includes ESP32 Marauder, Flipper Zero, and CYD ecosystem support.
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

# CYD (Cheap Yellow Display) ecosystem support
from .cyd import (
    # HAL Components
    DisplayDriver,
    TouchController,
    GPIOManager,
    PowerManager,
    SensorMonitor,
    # Community Integration
    CommunityIntegration,
    TemplateManager,
    ExampleLoader,
    # AI Agents
    CYDCodeGenerator,
    HardwareOptimizer,
    ProjectBuilder,
    # Digital Twin
    CYDSimulator,
    CYDTwinModel,
    CYDMonitor,
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
    # CYD Components
    "DisplayDriver",
    "TouchController",
    "GPIOManager",
    "PowerManager",
    "SensorMonitor",
    "CommunityIntegration",
    "TemplateManager",
    "ExampleLoader",
    "CYDCodeGenerator",
    "HardwareOptimizer",
    "ProjectBuilder",
    "CYDSimulator",
    "CYDTwinModel",
    "CYDMonitor",
]
