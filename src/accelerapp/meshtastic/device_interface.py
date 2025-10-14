"""
Device interface layer for Meshtastic devices.
Handles device discovery and communication via Serial, WiFi, and Bluetooth.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import serial
import serial.tools.list_ports


class ConnectionType(Enum):
    """Supported connection types for Meshtastic devices."""
    SERIAL = "serial"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"


@dataclass
class DeviceInfo:
    """Information about a discovered Meshtastic device."""
    
    device_id: str
    connection_type: ConnectionType
    port: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    hardware_model: Optional[str] = None
    firmware_version: Optional[str] = None
    node_id: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "device_id": self.device_id,
            "connection_type": self.connection_type.value,
            "port": self.port,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hardware_model": self.hardware_model,
            "firmware_version": self.firmware_version,
            "node_id": self.node_id,
            "discovered_at": self.discovered_at.isoformat(),
        }


class MeshtasticDevice:
    """
    Interface for communicating with a Meshtastic device.
    Supports Serial, WiFi, and Bluetooth connections.
    """
    
    def __init__(self, device_info: DeviceInfo):
        """
        Initialize Meshtastic device interface.
        
        Args:
            device_info: Device information
        """
        self.device_info = device_info
        self.connection = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Connect to the Meshtastic device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.device_info.connection_type == ConnectionType.SERIAL:
                return self._connect_serial()
            elif self.device_info.connection_type == ConnectionType.WIFI:
                return self._connect_wifi()
            elif self.device_info.connection_type == ConnectionType.BLUETOOTH:
                return self._connect_bluetooth()
            else:
                return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _connect_serial(self) -> bool:
        """Connect via serial port."""
        if not self.device_info.port:
            return False
        
        try:
            self.connection = serial.Serial(
                self.device_info.port,
                baudrate=115200,
                timeout=1
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Serial connection failed: {e}")
            return False
    
    def _connect_wifi(self) -> bool:
        """Connect via WiFi/TCP."""
        # Placeholder for WiFi connection implementation
        # Would use TCP socket to connect to device IP
        self.is_connected = True
        return True
    
    def _connect_bluetooth(self) -> bool:
        """Connect via Bluetooth."""
        # Placeholder for Bluetooth connection implementation
        # Would use BLE library to connect
        self.is_connected = True
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.connection:
            try:
                if isinstance(self.connection, serial.Serial):
                    self.connection.close()
            except Exception:
                pass
        self.is_connected = False
        self.connection = None
    
    def send_command(self, command: str) -> Optional[str]:
        """
        Send command to device.
        
        Args:
            command: Command to send
            
        Returns:
            Response from device or None if failed
        """
        if not self.is_connected:
            return None
        
        try:
            if isinstance(self.connection, serial.Serial):
                self.connection.write(f"{command}\n".encode())
                response = self.connection.readline().decode().strip()
                return response
        except Exception as e:
            print(f"Command failed: {e}")
            return None
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get detailed device information.
        
        Returns:
            Dictionary with device details
        """
        return self.device_info.to_dict()
    
    def configure_channel(self, channel_config: Dict[str, Any]) -> bool:
        """
        Configure a mesh channel.
        
        Args:
            channel_config: Channel configuration
            
        Returns:
            True if successful, False otherwise
        """
        # Placeholder for channel configuration
        return True
    
    def set_region(self, region: str) -> bool:
        """
        Set device region for frequency compliance.
        
        Args:
            region: Region code (US, EU, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        # Placeholder for region configuration
        return True
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class DeviceDiscovery:
    """
    Discovers Meshtastic devices via multiple connection methods.
    """
    
    @staticmethod
    def discover_serial() -> List[DeviceInfo]:
        """
        Discover Meshtastic devices on serial ports.
        
        Returns:
            List of discovered devices
        """
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Check for common Meshtastic device identifiers
            if any(vid in [0x239A, 0x10C4, 0x1A86] for vid in [port.vid] if port.vid):
                device_info = DeviceInfo(
                    device_id=f"serial_{port.device}",
                    connection_type=ConnectionType.SERIAL,
                    port=port.device,
                    hardware_model=port.product or "Unknown"
                )
                devices.append(device_info)
        
        return devices
    
    @staticmethod
    def discover_wifi(network_range: str = "192.168.1.0/24") -> List[DeviceInfo]:
        """
        Discover Meshtastic devices on local network.
        
        Args:
            network_range: Network range to scan
            
        Returns:
            List of discovered devices
        """
        # Placeholder for WiFi discovery
        # Would implement mDNS/network scanning
        devices = []
        return devices
    
    @staticmethod
    def discover_bluetooth() -> List[DeviceInfo]:
        """
        Discover Meshtastic devices via Bluetooth.
        
        Returns:
            List of discovered devices
        """
        # Placeholder for Bluetooth discovery
        # Would use BLE scanning
        devices = []
        return devices
    
    @staticmethod
    def discover_all() -> List[DeviceInfo]:
        """
        Discover Meshtastic devices via all methods.
        
        Returns:
            List of all discovered devices
        """
        devices = []
        devices.extend(DeviceDiscovery.discover_serial())
        devices.extend(DeviceDiscovery.discover_wifi())
        devices.extend(DeviceDiscovery.discover_bluetooth())
        return devices
