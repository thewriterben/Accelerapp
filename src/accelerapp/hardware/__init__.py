"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
Integrates WildCAM_ESP32 hardware generation capabilities.

"""

from .abstraction import ComponentFactory, HardwareAbstractionLayer, HardwareComponent
from .camera import (
    CameraConfig,
    CameraResolution,
    ESP32Camera,
)
from .camera.esp32_cam import (
    CameraVariant,
)

# CYD (Cheap Yellow Display) integration
from .cyd import (
    CommunityIntegration,
    CYDCodeGenerator,
    CYDMonitor,
    CYDSimulator,
    CYDTwinModel,
    DisplayDriver,
    ExampleLoader,
    GPIOManager,
    HardwareOptimizer,
    PowerManager,
    ProjectBuilder,
    SensorMonitor,
    TemplateManager,
    TouchController,
)
from .design import BoardSupportMatrix, EnclosureDesign, EnclosureGenerator, ESP32BoardType
from .environmental import EnvironmentalValidator, EnvironmentType, ValidationResult
from .esp32_marauder import (
    AttackType,
    BluetoothDevice,
    ESP32Marauder,
    MarauderCommand,
    PacketCapture,
    WiFiNetwork,
)
from .flipper_zero import (
    FlipperProtocol,
    FlipperZero,
    IRSignal,
    NFCTag,
    NFCType,
    RFIDTag,
    RFIDType,
    SubGHzSignal,
)
from .protocols import (
    CANConfig,
    DeviceDriverGenerator,
    I2CConfig,
    ProtocolGenerator,
    ProtocolType,
    SPIConfig,
)

# OBC hardware registry (single source of truth, Ecosystem Integration I1)
from .registry import (
    Accessory,
    Board,
    Registry,
    RegistrySchemaError,
    boards_for_platform,
    default_registry,
    load_registry,
    platform_for_board,
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
    "CameraConfig",
    "CameraResolution",
    "CameraVariant",
    # CYD components
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
    # OBC registry consumer
    "Accessory",
    "Board",
    "Registry",
    "RegistrySchemaError",
    "boards_for_platform",
    "default_registry",
    "load_registry",
    "platform_for_board",
]
