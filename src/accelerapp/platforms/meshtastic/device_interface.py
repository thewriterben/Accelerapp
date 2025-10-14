"""
Meshtastic device interface module.
Handles device discovery, connection, and communication.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Meshtastic connection types."""
    SERIAL = "serial"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"


@dataclass
class MeshtasticDevice:
    """Represents a discovered Meshtastic device."""
    device_id: str
    connection_type: ConnectionType
    device_name: Optional[str] = None
    hardware_model: Optional[str] = None
    firmware_version: Optional[str] = None
    connection_info: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "device_id": self.device_id,
            "connection_type": self.connection_type.value,
            "device_name": self.device_name,
            "hardware_model": self.hardware_model,
            "firmware_version": self.firmware_version,
            "connection_info": self.connection_info,
            "discovered_at": self.discovered_at.isoformat(),
        }


class DeviceDiscovery:
    """Device discovery service for Meshtastic devices."""
    
    def __init__(self):
        """Initialize device discovery."""
        self._discovered_devices: Dict[str, MeshtasticDevice] = {}
        
    def discover_serial_devices(self) -> List[MeshtasticDevice]:
        """
        Discover Meshtastic devices connected via serial.
        
        Returns:
            List of discovered devices
        """
        devices = []
        try:
            # Try to import pyserial
            import serial.tools.list_ports
            
            # Look for common Meshtastic device patterns
            for port in serial.tools.list_ports.comports():
                # Check for ESP32, nRF52, or other common patterns
                if any(pattern in str(port.description).lower() for pattern in 
                       ["esp32", "nrf52", "ch340", "cp210", "ftdi"]):
                    device = MeshtasticDevice(
                        device_id=port.device,
                        connection_type=ConnectionType.SERIAL,
                        connection_info={
                            "port": port.device,
                            "description": port.description,
                            "hwid": port.hwid,
                        }
                    )
                    devices.append(device)
                    self._discovered_devices[device.device_id] = device
                    logger.info(f"Discovered serial device: {port.device}")
        except ImportError:
            logger.warning("pyserial not available, skipping serial discovery")
        except Exception as e:
            logger.error(f"Error during serial discovery: {e}")
            
        return devices
    
    def discover_wifi_devices(self, timeout: float = 5.0) -> List[MeshtasticDevice]:
        """
        Discover Meshtastic devices on WiFi network.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices
        """
        devices = []
        # Placeholder for WiFi discovery implementation
        # Would use mDNS/Bonjour or network scanning
        logger.info("WiFi device discovery not yet implemented")
        return devices
    
    def discover_bluetooth_devices(self, timeout: float = 10.0) -> List[MeshtasticDevice]:
        """
        Discover Meshtastic devices via Bluetooth.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices
        """
        devices = []
        # Placeholder for Bluetooth discovery
        # Would use BLE scanning
        logger.info("Bluetooth device discovery not yet implemented")
        return devices
    
    def discover_all(self) -> List[MeshtasticDevice]:
        """
        Discover devices on all available interfaces.
        
        Returns:
            List of all discovered devices
        """
        devices = []
        devices.extend(self.discover_serial_devices())
        devices.extend(self.discover_wifi_devices())
        devices.extend(self.discover_bluetooth_devices())
        return devices
    
    def get_discovered_devices(self) -> List[MeshtasticDevice]:
        """Get list of all discovered devices."""
        return list(self._discovered_devices.values())


class MeshtasticDeviceInterface:
    """
    Interface for communicating with Meshtastic devices.
    Supports Serial, WiFi, and Bluetooth connections.
    """
    
    def __init__(self, device: MeshtasticDevice):
        """
        Initialize device interface.
        
        Args:
            device: Meshtastic device to connect to
        """
        self.device = device
        self.connected = False
        self._interface = None
        
    def connect(self) -> bool:
        """
        Connect to the Meshtastic device.
        
        Returns:
            True if connected successfully
        """
        try:
            if self.device.connection_type == ConnectionType.SERIAL:
                return self._connect_serial()
            elif self.device.connection_type == ConnectionType.WIFI:
                return self._connect_wifi()
            elif self.device.connection_type == ConnectionType.BLUETOOTH:
                return self._connect_bluetooth()
            else:
                logger.error(f"Unsupported connection type: {self.device.connection_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False
    
    def _connect_serial(self) -> bool:
        """Connect via serial port."""
        try:
            # Placeholder for actual meshtastic library integration
            # from meshtastic import SerialInterface
            # self._interface = SerialInterface(self.device.device_id)
            port = self.device.connection_info.get("port", self.device.device_id)
            logger.info(f"Connecting to serial port: {port}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Serial connection failed: {e}")
            return False
    
    def _connect_wifi(self) -> bool:
        """Connect via WiFi."""
        logger.info("WiFi connection not yet implemented")
        return False
    
    def _connect_bluetooth(self) -> bool:
        """Connect via Bluetooth."""
        logger.info("Bluetooth connection not yet implemented")
        return False
    
    def disconnect(self):
        """Disconnect from the device."""
        if self._interface:
            try:
                # Close the interface
                if hasattr(self._interface, 'close'):
                    self._interface.close()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
        self.connected = False
        self._interface = None
        
    def is_connected(self) -> bool:
        """Check if connected to device."""
        return self.connected
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information.
        
        Returns:
            Device information dictionary
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
            
        # Placeholder for actual implementation
        return {
            "device_id": self.device.device_id,
            "connection_type": self.device.connection_type.value,
            "hardware_model": self.device.hardware_model or "unknown",
            "firmware_version": self.device.firmware_version or "unknown",
        }
    
    def configure_device(self, config: Dict[str, Any]) -> bool:
        """
        Configure device settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration successful
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
            
        logger.info(f"Configuring device with: {config}")
        # Placeholder for actual configuration
        return True
    
    def send_message(self, message: str, channel: int = 0) -> bool:
        """
        Send a message over the mesh network.
        
        Args:
            message: Message to send
            channel: Channel number
            
        Returns:
            True if message sent successfully
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
            
        logger.info(f"Sending message on channel {channel}: {message}")
        # Placeholder for actual message sending
        return True
