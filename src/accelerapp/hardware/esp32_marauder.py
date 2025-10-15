"""
ESP32 Marauder integration module.
Provides WiFi/Bluetooth scanning, packet capture, and penetration testing capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

import serial
import serial.tools.list_ports


class MarauderCommand(Enum):
    """ESP32 Marauder command types."""
    
    WIFI_SCAN = "scan"
    WIFI_SCAN_AP = "scanap"
    WIFI_SCAN_STA = "scansta"
    BT_SCAN = "ble"
    DEAUTH = "attack -t deauth"
    BEACON = "attack -t beacon"
    PROBE = "attack -t probe"
    RICKROLL = "attack -t rickroll"
    PACKET_MONITOR = "sniff"
    STOP_ATTACK = "stopscan"
    HELP = "help"
    REBOOT = "reboot"
    UPDATE = "update"
    SETTINGS = "settings"


class AttackType(Enum):
    """Supported attack types."""
    
    DEAUTH = "deauth"
    BEACON = "beacon"
    PROBE = "probe"
    RICKROLL = "rickroll"


@dataclass
class WiFiNetwork:
    """WiFi network information."""
    
    ssid: str
    bssid: str
    channel: int
    rssi: int
    encryption: str
    hidden: bool = False
    vendor: Optional[str] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "rssi": self.rssi,
            "encryption": self.encryption,
            "hidden": self.hidden,
            "vendor": self.vendor,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }


@dataclass
class BluetoothDevice:
    """Bluetooth device information."""
    
    name: str
    address: str
    rssi: int
    device_type: str
    manufacturer: Optional[str] = None
    services: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "rssi": self.rssi,
            "device_type": self.device_type,
            "manufacturer": self.manufacturer,
            "services": self.services,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }


@dataclass
class PacketCapture:
    """Captured packet information."""
    
    timestamp: datetime
    packet_type: str
    source: str
    destination: str
    channel: int
    data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "packet_type": self.packet_type,
            "source": self.source,
            "destination": self.destination,
            "channel": self.channel,
            "data": self.data.hex(),
            "metadata": self.metadata,
        }


class ESP32Marauder:
    """
    Interface for ESP32 Marauder device.
    Supports WiFi scanning, Bluetooth discovery, and penetration testing.
    """
    
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 115200,
        timeout: float = 5.0,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize ESP32 Marauder interface.
        
        Args:
            port: Serial port path (auto-detect if None)
            baudrate: Serial communication speed
            timeout: Command timeout in seconds
            logger: Logger instance
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        
        self.connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_scanning = False
        self.is_attacking = False
        
        # Scan results
        self.wifi_networks: Dict[str, WiFiNetwork] = {}
        self.bluetooth_devices: Dict[str, BluetoothDevice] = {}
        self.packet_captures: List[PacketCapture] = []
        
        # Callbacks
        self._scan_callbacks: List[Callable] = []
        self._packet_callbacks: List[Callable] = []
    
    @staticmethod
    def discover_devices() -> List[Dict[str, Any]]:
        """
        Discover ESP32 Marauder devices on serial ports.
        
        Returns:
            List of discovered device information
        """
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Check for ESP32 VID/PIDs
            if port.vid in [0x10C4, 0x1A86, 0x303A]:  # Common ESP32 VIDs
                device_info = {
                    "port": port.device,
                    "description": port.description,
                    "hwid": port.hwid,
                    "vid": port.vid,
                    "pid": port.pid,
                    "serial_number": port.serial_number,
                    "manufacturer": port.manufacturer,
                    "product": port.product,
                }
                devices.append(device_info)
        
        return devices
    
    def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to ESP32 Marauder device.
        
        Args:
            port: Serial port (uses auto-detected if None)
        
        Returns:
            True if connected successfully
        """
        try:
            if port:
                self.port = port
            
            if not self.port:
                # Auto-detect
                devices = self.discover_devices()
                if not devices:
                    self.logger.error("No ESP32 devices found")
                    return False
                self.port = devices[0]["port"]
                self.logger.info(f"Auto-detected device on {self.port}")
            
            self.connection = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            self.is_connected = True
            self.logger.info(f"Connected to ESP32 Marauder on {self.port}")
            
            # Send test command
            self._send_command(MarauderCommand.HELP.value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self.connection and self.connection.is_open:
            try:
                # Stop any ongoing operations
                if self.is_attacking or self.is_scanning:
                    self.stop_operation()
                self.connection.close()
            except Exception as e:
                self.logger.error(f"Disconnect error: {e}")
        
        self.is_connected = False
        self.connection = None
        self.logger.info("Disconnected from ESP32 Marauder")
    
    def _send_command(self, command: str) -> Optional[str]:
        """
        Send command to device and get response.
        
        Args:
            command: Command string
        
        Returns:
            Response string or None if failed
        """
        if not self.is_connected or not self.connection:
            self.logger.error("Device not connected")
            return None
        
        try:
            # Send command
            self.connection.write(f"{command}\n".encode())
            self.connection.flush()
            
            # Read response
            response = self.connection.read_until(b'\n').decode().strip()
            return response
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return None
    
    def _read_output(self, duration: float = 5.0) -> List[str]:
        """
        Read output from device for specified duration.
        
        Args:
            duration: Read duration in seconds
        
        Returns:
            List of output lines
        """
        lines = []
        end_time = datetime.now().timestamp() + duration
        
        while datetime.now().timestamp() < end_time:
            if self.connection and self.connection.in_waiting:
                try:
                    line = self.connection.readline().decode().strip()
                    if line:
                        lines.append(line)
                except Exception as e:
                    self.logger.error(f"Read error: {e}")
        
        return lines
    
    async def scan_wifi_networks(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> List[WiFiNetwork]:
        """
        Scan for WiFi networks.
        
        Args:
            duration: Scan duration in seconds
            callback: Optional callback for real-time results
        
        Returns:
            List of discovered WiFi networks
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return []
        
        try:
            self.is_scanning = True
            self.wifi_networks.clear()
            
            # Start WiFi scan
            self._send_command(MarauderCommand.WIFI_SCAN.value)
            
            # Read scan results
            await asyncio.sleep(duration)
            lines = self._read_output(1.0)
            
            # Parse scan results
            for line in lines:
                network = self._parse_wifi_result(line)
                if network:
                    self.wifi_networks[network.bssid] = network
                    if callback:
                        callback(network)
            
            self.is_scanning = False
            return list(self.wifi_networks.values())
            
        except Exception as e:
            self.logger.error(f"WiFi scan failed: {e}")
            self.is_scanning = False
            return []
    
    async def scan_bluetooth_devices(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> List[BluetoothDevice]:
        """
        Scan for Bluetooth devices.
        
        Args:
            duration: Scan duration in seconds
            callback: Optional callback for real-time results
        
        Returns:
            List of discovered Bluetooth devices
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return []
        
        try:
            self.is_scanning = True
            self.bluetooth_devices.clear()
            
            # Start BLE scan
            self._send_command(MarauderCommand.BT_SCAN.value)
            
            # Read scan results
            await asyncio.sleep(duration)
            lines = self._read_output(1.0)
            
            # Parse scan results
            for line in lines:
                device = self._parse_bluetooth_result(line)
                if device:
                    self.bluetooth_devices[device.address] = device
                    if callback:
                        callback(device)
            
            self.is_scanning = False
            return list(self.bluetooth_devices.values())
            
        except Exception as e:
            self.logger.error(f"Bluetooth scan failed: {e}")
            self.is_scanning = False
            return []
    
    def start_attack(
        self,
        attack_type: AttackType,
        targets: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        Start penetration testing attack.
        
        Args:
            attack_type: Type of attack to perform
            targets: Target MAC addresses (for deauth)
            **kwargs: Additional attack parameters
        
        Returns:
            True if attack started successfully
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return False
        
        if self.is_attacking:
            self.logger.warning("Attack already in progress")
            return False
        
        try:
            command = self._build_attack_command(attack_type, targets, **kwargs)
            response = self._send_command(command)
            
            if response:
                self.is_attacking = True
                self.logger.info(f"Started {attack_type.value} attack")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Attack start failed: {e}")
            return False
    
    def stop_operation(self) -> bool:
        """
        Stop current scanning or attack operation.
        
        Returns:
            True if stopped successfully
        """
        if not self.is_connected:
            return False
        
        try:
            self._send_command(MarauderCommand.STOP_ATTACK.value)
            self.is_scanning = False
            self.is_attacking = False
            self.logger.info("Stopped operation")
            return True
            
        except Exception as e:
            self.logger.error(f"Stop failed: {e}")
            return False
    
    def start_packet_capture(
        self,
        channel: Optional[int] = None,
        callback: Optional[Callable] = None,
    ) -> bool:
        """
        Start packet capture/monitoring.
        
        Args:
            channel: WiFi channel to monitor (all if None)
            callback: Callback for captured packets
        
        Returns:
            True if capture started successfully
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return False
        
        try:
            command = MarauderCommand.PACKET_MONITOR.value
            if channel:
                command += f" -c {channel}"
            
            self._send_command(command)
            
            if callback:
                self._packet_callbacks.append(callback)
            
            self.logger.info("Started packet capture")
            return True
            
        except Exception as e:
            self.logger.error(f"Packet capture start failed: {e}")
            return False
    
    def stop_packet_capture(self) -> bool:
        """
        Stop packet capture.
        
        Returns:
            True if stopped successfully
        """
        return self.stop_operation()
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information.
        
        Returns:
            Device information dictionary
        """
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "is_connected": self.is_connected,
            "is_scanning": self.is_scanning,
            "is_attacking": self.is_attacking,
            "wifi_networks": len(self.wifi_networks),
            "bluetooth_devices": len(self.bluetooth_devices),
            "packet_captures": len(self.packet_captures),
        }
    
    def _parse_wifi_result(self, line: str) -> Optional[WiFiNetwork]:
        """Parse WiFi scan result line."""
        try:
            # Expected format: SSID|BSSID|CHANNEL|RSSI|ENCRYPTION
            parts = line.split("|")
            if len(parts) >= 5:
                return WiFiNetwork(
                    ssid=parts[0].strip(),
                    bssid=parts[1].strip(),
                    channel=int(parts[2].strip()),
                    rssi=int(parts[3].strip()),
                    encryption=parts[4].strip(),
                )
        except Exception:
            pass
        return None
    
    def _parse_bluetooth_result(self, line: str) -> Optional[BluetoothDevice]:
        """Parse Bluetooth scan result line."""
        try:
            # Expected format: NAME|ADDRESS|RSSI|TYPE
            parts = line.split("|")
            if len(parts) >= 4:
                return BluetoothDevice(
                    name=parts[0].strip(),
                    address=parts[1].strip(),
                    rssi=int(parts[2].strip()),
                    device_type=parts[3].strip(),
                )
        except Exception:
            pass
        return None
    
    def _build_attack_command(
        self,
        attack_type: AttackType,
        targets: Optional[List[str]],
        **kwargs,
    ) -> str:
        """Build attack command string."""
        if attack_type == AttackType.DEAUTH:
            command = MarauderCommand.DEAUTH.value
            if targets:
                command += f" -t {','.join(targets)}"
        elif attack_type == AttackType.BEACON:
            command = MarauderCommand.BEACON.value
        elif attack_type == AttackType.PROBE:
            command = MarauderCommand.PROBE.value
        elif attack_type == AttackType.RICKROLL:
            command = MarauderCommand.RICKROLL.value
        else:
            command = ""
        
        return command
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
