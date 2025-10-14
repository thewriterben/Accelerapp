"""
Meshtastic mesh communication support for Accelerapp.

This module provides comprehensive Meshtastic integration including:
- Device discovery and communication (Serial, WiFi, Bluetooth)
- Firmware management and OTA updates
- Mesh network management and monitoring
- Air-gapped deployment support
- Digital twin integration for mesh nodes
"""

from .device_interface import (
    MeshtasticDevice,
    DeviceDiscovery,
    ConnectionType,
    DeviceInfo,
)
from .firmware_manager import (
    FirmwareManager,
    FirmwareVersion,
    FirmwareUpdateStatus,
)
from .network_manager import (
    MeshNetworkManager,
    MeshNode,
    NetworkTopology,
)
from .ota_controller import (
    OTAController,
    OTAMethod,
    UpdateProgress,
)

__all__ = [
    # Device Interface
    "MeshtasticDevice",
    "DeviceDiscovery",
    "ConnectionType",
    "DeviceInfo",
    # Firmware Management
    "FirmwareManager",
    "FirmwareVersion",
    "FirmwareUpdateStatus",
    # Network Management
    "MeshNetworkManager",
    "MeshNode",
    "NetworkTopology",
    # OTA Updates
    "OTAController",
    "OTAMethod",
    "UpdateProgress",
]
