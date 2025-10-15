"""
Unified Hardware Manager for coordinating multiple hardware devices.
Supports ESP32 Marauder, Flipper Zero, and other hardware platforms.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable

from ..hardware.esp32_marauder import ESP32Marauder, WiFiNetwork, BluetoothDevice
from ..hardware.flipper_zero import FlipperZero, RFIDTag, NFCTag, SubGHzSignal, IRSignal
from ..monitoring import get_logger


class DeviceType(Enum):
    """Supported device types."""
    
    ESP32_MARAUDER = "esp32_marauder"
    FLIPPER_ZERO = "flipper_zero"
    MESHTASTIC = "meshtastic"
    GENERIC_ESP32 = "generic_esp32"
    ARDUINO = "arduino"


class DeviceCapability(Enum):
    """Device capabilities."""
    
    WIFI_SCAN = "wifi_scan"
    BLUETOOTH_SCAN = "bluetooth_scan"
    RFID_125KHZ = "rfid_125khz"
    RFID_HF = "rfid_hf"
    NFC = "nfc"
    SUBGHZ = "subghz"
    INFRARED = "infrared"
    GPIO = "gpio"
    DEAUTH_ATTACK = "deauth_attack"
    PACKET_CAPTURE = "packet_capture"
    IBUTTON = "ibutton"
    BADUSB = "badusb"


class DeviceStatus(Enum):
    """Device status."""
    
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    BUSY = "busy"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ManagedDevice:
    """Managed device information."""
    
    device_id: str
    device_type: DeviceType
    device: Any
    capabilities: Set[DeviceCapability]
    status: DeviceStatus = DeviceStatus.DISCONNECTED
    port: Optional[str] = None
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "status": self.status.value,
            "port": self.port,
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ScanResults:
    """Aggregated scan results from multiple devices."""
    
    wifi_networks: List[WiFiNetwork] = field(default_factory=list)
    bluetooth_devices: List[BluetoothDevice] = field(default_factory=list)
    rfid_tags: List[RFIDTag] = field(default_factory=list)
    nfc_tags: List[NFCTag] = field(default_factory=list)
    subghz_signals: List[SubGHzSignal] = field(default_factory=list)
    ir_signals: List[IRSignal] = field(default_factory=list)
    scan_time: datetime = field(default_factory=datetime.now)
    devices_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "wifi_networks": [net.to_dict() for net in self.wifi_networks],
            "bluetooth_devices": [dev.to_dict() for dev in self.bluetooth_devices],
            "rfid_tags": [tag.to_dict() for tag in self.rfid_tags],
            "nfc_tags": [tag.to_dict() for tag in self.nfc_tags],
            "subghz_signals": [sig.to_dict() for sig in self.subghz_signals],
            "ir_signals": [sig.to_dict() for sig in self.ir_signals],
            "scan_time": self.scan_time.isoformat(),
            "devices_used": self.devices_used,
        }


class HardwareManager:
    """
    Unified hardware manager for coordinating multiple devices.
    Provides device discovery, registration, and coordinated operations.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize hardware manager.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or get_logger(__name__)
        self.devices: Dict[str, ManagedDevice] = {}
        self._auto_discovery_enabled = True
        self._callbacks: Dict[str, List[Callable]] = {
            "device_connected": [],
            "device_disconnected": [],
            "scan_complete": [],
            "error": [],
        }
    
    async def discover_devices(self) -> List[ManagedDevice]:
        """
        Discover all available hardware devices.
        
        Returns:
            List of discovered devices
        """
        discovered = []
        
        try:
            # Discover ESP32 Marauder devices
            marauder_devices = ESP32Marauder.discover_devices()
            for device_info in marauder_devices:
                device_id = f"marauder_{device_info['port']}"
                if device_id not in self.devices:
                    managed_device = ManagedDevice(
                        device_id=device_id,
                        device_type=DeviceType.ESP32_MARAUDER,
                        device=None,  # Will be created on connect
                        capabilities={
                            DeviceCapability.WIFI_SCAN,
                            DeviceCapability.BLUETOOTH_SCAN,
                            DeviceCapability.DEAUTH_ATTACK,
                            DeviceCapability.PACKET_CAPTURE,
                        },
                        port=device_info["port"],
                        metadata=device_info,
                    )
                    discovered.append(managed_device)
                    self.logger.info(f"Discovered ESP32 Marauder: {device_id}")
            
            # Discover Flipper Zero devices
            flipper_devices = FlipperZero.discover_devices()
            for device_info in flipper_devices:
                device_id = f"flipper_{device_info['port']}"
                if device_id not in self.devices:
                    managed_device = ManagedDevice(
                        device_id=device_id,
                        device_type=DeviceType.FLIPPER_ZERO,
                        device=None,  # Will be created on connect
                        capabilities={
                            DeviceCapability.RFID_125KHZ,
                            DeviceCapability.RFID_HF,
                            DeviceCapability.NFC,
                            DeviceCapability.SUBGHZ,
                            DeviceCapability.INFRARED,
                            DeviceCapability.GPIO,
                            DeviceCapability.IBUTTON,
                            DeviceCapability.BADUSB,
                        },
                        port=device_info["port"],
                        metadata=device_info,
                    )
                    discovered.append(managed_device)
                    self.logger.info(f"Discovered Flipper Zero: {device_id}")
        
        except Exception as e:
            self.logger.error(f"Device discovery failed: {e}")
        
        return discovered
    
    def register_device(
        self,
        device_id: str,
        device_type: DeviceType,
        device: Any,
        capabilities: Set[DeviceCapability],
        port: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a hardware device.
        
        Args:
            device_id: Unique device identifier
            device_type: Type of device
            device: Device instance
            capabilities: Set of device capabilities
            port: Serial port (if applicable)
            metadata: Additional device metadata
        
        Returns:
            True if registered successfully
        """
        try:
            if device_id in self.devices:
                self.logger.warning(f"Device {device_id} already registered")
                return False
            
            managed_device = ManagedDevice(
                device_id=device_id,
                device_type=device_type,
                device=device,
                capabilities=capabilities,
                port=port,
                metadata=metadata or {},
            )
            
            self.devices[device_id] = managed_device
            self.logger.info(f"Registered device: {device_id}")
            
            # Trigger callbacks
            self._trigger_callbacks("device_connected", managed_device)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Device registration failed: {e}")
            return False
    
    async def connect_device(self, device_id: str) -> bool:
        """
        Connect to a registered device.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if connected successfully
        """
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not registered")
            return False
        
        managed_device = self.devices[device_id]
        
        try:
            # Create device instance if not exists
            if managed_device.device is None:
                if managed_device.device_type == DeviceType.ESP32_MARAUDER:
                    managed_device.device = ESP32Marauder(
                        port=managed_device.port,
                        logger=self.logger,
                    )
                elif managed_device.device_type == DeviceType.FLIPPER_ZERO:
                    managed_device.device = FlipperZero(
                        port=managed_device.port,
                        logger=self.logger,
                    )
                else:
                    self.logger.error(f"Unsupported device type: {managed_device.device_type}")
                    return False
            
            # Connect to device
            success = managed_device.device.connect(managed_device.port)
            
            if success:
                managed_device.status = DeviceStatus.CONNECTED
                managed_device.last_seen = datetime.now()
                self.logger.info(f"Connected to device: {device_id}")
                self._trigger_callbacks("device_connected", managed_device)
            else:
                managed_device.status = DeviceStatus.ERROR
            
            return success
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            managed_device.status = DeviceStatus.ERROR
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """
        Disconnect from a device.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if disconnected successfully
        """
        if device_id not in self.devices:
            self.logger.error(f"Device {device_id} not registered")
            return False
        
        managed_device = self.devices[device_id]
        
        try:
            if managed_device.device:
                managed_device.device.disconnect()
            
            managed_device.status = DeviceStatus.DISCONNECTED
            self.logger.info(f"Disconnected from device: {device_id}")
            self._trigger_callbacks("device_disconnected", managed_device)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Disconnect failed: {e}")
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if unregistered successfully
        """
        if device_id not in self.devices:
            return False
        
        # Disconnect first
        self.disconnect_device(device_id)
        
        # Remove from registry
        del self.devices[device_id]
        self.logger.info(f"Unregistered device: {device_id}")
        
        return True
    
    async def unified_scan(
        self,
        capabilities: Optional[Set[DeviceCapability]] = None,
        duration: float = 10.0,
    ) -> ScanResults:
        """
        Perform unified scan across all capable devices.
        
        Args:
            capabilities: Specific capabilities to scan (all if None)
            duration: Scan duration in seconds
        
        Returns:
            Aggregated scan results
        """
        results = ScanResults()
        
        # Determine which capabilities to scan
        scan_caps = capabilities or {
            DeviceCapability.WIFI_SCAN,
            DeviceCapability.BLUETOOTH_SCAN,
            DeviceCapability.RFID_125KHZ,
            DeviceCapability.NFC,
        }
        
        tasks = []
        
        # Create scan tasks for each device
        for device_id, managed_device in self.devices.items():
            if managed_device.status != DeviceStatus.CONNECTED:
                continue
            
            # WiFi scan
            if (DeviceCapability.WIFI_SCAN in scan_caps and
                DeviceCapability.WIFI_SCAN in managed_device.capabilities):
                if isinstance(managed_device.device, ESP32Marauder):
                    tasks.append(self._scan_wifi(device_id, duration, results))
            
            # Bluetooth scan
            if (DeviceCapability.BLUETOOTH_SCAN in scan_caps and
                DeviceCapability.BLUETOOTH_SCAN in managed_device.capabilities):
                if isinstance(managed_device.device, ESP32Marauder):
                    tasks.append(self._scan_bluetooth(device_id, duration, results))
            
            # RFID scan
            if (DeviceCapability.RFID_125KHZ in scan_caps and
                DeviceCapability.RFID_125KHZ in managed_device.capabilities):
                if isinstance(managed_device.device, FlipperZero):
                    tasks.append(self._scan_rfid(device_id, duration, results))
            
            # NFC scan
            if (DeviceCapability.NFC in scan_caps and
                DeviceCapability.NFC in managed_device.capabilities):
                if isinstance(managed_device.device, FlipperZero):
                    tasks.append(self._scan_nfc(device_id, duration, results))
        
        # Run all scans concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Trigger callbacks
        self._trigger_callbacks("scan_complete", results)
        
        return results
    
    async def _scan_wifi(
        self,
        device_id: str,
        duration: float,
        results: ScanResults,
    ) -> None:
        """Internal WiFi scan task."""
        try:
            managed_device = self.devices[device_id]
            managed_device.status = DeviceStatus.BUSY
            
            networks = await managed_device.device.scan_wifi_networks(duration)
            results.wifi_networks.extend(networks)
            results.devices_used.append(device_id)
            
            managed_device.status = DeviceStatus.CONNECTED
            
        except Exception as e:
            self.logger.error(f"WiFi scan failed on {device_id}: {e}")
            self._trigger_callbacks("error", {"device_id": device_id, "error": str(e)})
    
    async def _scan_bluetooth(
        self,
        device_id: str,
        duration: float,
        results: ScanResults,
    ) -> None:
        """Internal Bluetooth scan task."""
        try:
            managed_device = self.devices[device_id]
            managed_device.status = DeviceStatus.BUSY
            
            devices = await managed_device.device.scan_bluetooth_devices(duration)
            results.bluetooth_devices.extend(devices)
            results.devices_used.append(device_id)
            
            managed_device.status = DeviceStatus.CONNECTED
            
        except Exception as e:
            self.logger.error(f"Bluetooth scan failed on {device_id}: {e}")
            self._trigger_callbacks("error", {"device_id": device_id, "error": str(e)})
    
    async def _scan_rfid(
        self,
        device_id: str,
        duration: float,
        results: ScanResults,
    ) -> None:
        """Internal RFID scan task."""
        try:
            managed_device = self.devices[device_id]
            managed_device.status = DeviceStatus.BUSY
            
            tag = await managed_device.device.read_rfid_125khz(duration)
            if tag:
                results.rfid_tags.append(tag)
                results.devices_used.append(device_id)
            
            managed_device.status = DeviceStatus.CONNECTED
            
        except Exception as e:
            self.logger.error(f"RFID scan failed on {device_id}: {e}")
            self._trigger_callbacks("error", {"device_id": device_id, "error": str(e)})
    
    async def _scan_nfc(
        self,
        device_id: str,
        duration: float,
        results: ScanResults,
    ) -> None:
        """Internal NFC scan task."""
        try:
            managed_device = self.devices[device_id]
            managed_device.status = DeviceStatus.BUSY
            
            tag = await managed_device.device.read_nfc(duration)
            if tag:
                results.nfc_tags.append(tag)
                results.devices_used.append(device_id)
            
            managed_device.status = DeviceStatus.CONNECTED
            
        except Exception as e:
            self.logger.error(f"NFC scan failed on {device_id}: {e}")
            self._trigger_callbacks("error", {"device_id": device_id, "error": str(e)})
    
    def get_device(self, device_id: str) -> Optional[ManagedDevice]:
        """
        Get device by ID.
        
        Args:
            device_id: Device identifier
        
        Returns:
            Managed device or None
        """
        return self.devices.get(device_id)
    
    def list_devices(
        self,
        device_type: Optional[DeviceType] = None,
        capability: Optional[DeviceCapability] = None,
    ) -> List[ManagedDevice]:
        """
        List registered devices with optional filtering.
        
        Args:
            device_type: Filter by device type
            capability: Filter by capability
        
        Returns:
            List of matching devices
        """
        devices = list(self.devices.values())
        
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        
        if capability:
            devices = [d for d in devices if capability in d.capabilities]
        
        return devices
    
    def get_capabilities(self) -> Set[DeviceCapability]:
        """
        Get all available capabilities across registered devices.
        
        Returns:
            Set of available capabilities
        """
        capabilities = set()
        for device in self.devices.values():
            capabilities.update(device.capabilities)
        return capabilities
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """
        Add event callback.
        
        Args:
            event_type: Event type (device_connected, device_disconnected, etc.)
            callback: Callback function
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable) -> None:
        """
        Remove event callback.
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger callbacks for an event."""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Callback failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get manager status.
        
        Returns:
            Status dictionary
        """
        return {
            "total_devices": len(self.devices),
            "connected_devices": sum(
                1 for d in self.devices.values()
                if d.status == DeviceStatus.CONNECTED
            ),
            "busy_devices": sum(
                1 for d in self.devices.values()
                if d.status == DeviceStatus.BUSY
            ),
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "devices": {
                device_id: device.to_dict()
                for device_id, device in self.devices.items()
            },
        }
    
    async def shutdown(self) -> None:
        """Shutdown manager and disconnect all devices."""
        self.logger.info("Shutting down hardware manager")
        
        for device_id in list(self.devices.keys()):
            self.disconnect_device(device_id)
        
        self.devices.clear()
