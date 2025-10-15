"""
Flipper Zero integration module.
Provides RFID, NFC, Sub-GHz, IR, and GPIO capabilities.
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


class FlipperProtocol(Enum):
    """Flipper Zero protocol types."""
    
    RFID_125KHZ = "rfid_125khz"
    RFID_HF = "rfid_hf"
    NFC = "nfc"
    SUBGHZ = "subghz"
    INFRARED = "infrared"
    GPIO = "gpio"
    IBUTTON = "ibutton"
    BADUSB = "badusb"


class RFIDType(Enum):
    """RFID tag types."""
    
    EM4100 = "EM4100"
    HID_PROX = "HIDProx"
    INDALA = "Indala"
    AWID = "AWID"
    VIKING = "Viking"
    JABLOTRON = "Jablotron"
    MIFARE_CLASSIC = "MifareClassic"
    MIFARE_ULTRALIGHT = "MifareUltralight"
    MIFARE_DESFIRE = "MifareDESFire"


class NFCType(Enum):
    """NFC tag types."""
    
    NTAG = "NTAG"
    MIFARE_CLASSIC = "MifareClassic"
    MIFARE_ULTRALIGHT = "MifareUltralight"
    ISO14443A = "ISO14443A"
    ISO14443B = "ISO14443B"
    ISO15693 = "ISO15693"


@dataclass
class RFIDTag:
    """RFID tag information."""
    
    tag_type: str
    uid: str
    protocol: FlipperProtocol
    data: Optional[str] = None
    blocks: Dict[int, str] = field(default_factory=dict)
    read_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tag_type": self.tag_type,
            "uid": self.uid,
            "protocol": self.protocol.value,
            "data": self.data,
            "blocks": self.blocks,
            "read_time": self.read_time.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class NFCTag:
    """NFC tag information."""
    
    tag_type: str
    uid: str
    atqa: str
    sak: str
    data: Optional[str] = None
    ndef_records: List[Dict[str, Any]] = field(default_factory=list)
    read_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tag_type": self.tag_type,
            "uid": self.uid,
            "atqa": self.atqa,
            "sak": self.sak,
            "data": self.data,
            "ndef_records": self.ndef_records,
            "read_time": self.read_time.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class SubGHzSignal:
    """Sub-GHz signal information."""
    
    frequency: float
    modulation: str
    protocol: str
    data: str
    rssi: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "frequency": self.frequency,
            "modulation": self.modulation,
            "protocol": self.protocol,
            "data": self.data,
            "rssi": self.rssi,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class IRSignal:
    """Infrared signal information."""
    
    protocol: str
    address: str
    command: str
    raw_data: Optional[List[int]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "protocol": self.protocol,
            "address": self.address,
            "command": self.command,
            "raw_data": self.raw_data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class FlipperZero:
    """
    Interface for Flipper Zero device.
    Supports RFID, NFC, Sub-GHz, IR, and GPIO operations.
    """
    
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 230400,
        timeout: float = 5.0,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize Flipper Zero interface.
        
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
        self.is_reading = False
        
        # Scan results
        self.rfid_tags: List[RFIDTag] = []
        self.nfc_tags: List[NFCTag] = []
        self.subghz_signals: List[SubGHzSignal] = []
        self.ir_signals: List[IRSignal] = []
        
        # Callbacks
        self._tag_callbacks: List[Callable] = []
        self._signal_callbacks: List[Callable] = []
    
    @staticmethod
    def discover_devices() -> List[Dict[str, Any]]:
        """
        Discover Flipper Zero devices on serial ports.
        
        Returns:
            List of discovered device information
        """
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Check for Flipper Zero VID/PID
            if port.vid == 0x0483 and port.pid == 0x5740:  # Flipper Zero
                device_info = {
                    "port": port.device,
                    "description": port.description,
                    "hwid": port.hwid,
                    "vid": port.vid,
                    "pid": port.pid,
                    "serial_number": port.serial_number,
                    "manufacturer": port.manufacturer,
                    "product": port.product or "Flipper Zero",
                }
                devices.append(device_info)
        
        return devices
    
    def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to Flipper Zero device.
        
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
                    self.logger.error("No Flipper Zero devices found")
                    return False
                self.port = devices[0]["port"]
                self.logger.info(f"Auto-detected Flipper Zero on {self.port}")
            
            self.connection = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            self.is_connected = True
            self.logger.info(f"Connected to Flipper Zero on {self.port}")
            
            # Initialize CLI mode
            self._enter_cli_mode()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self.connection and self.connection.is_open:
            try:
                # Stop any ongoing operations
                if self.is_reading:
                    self.stop_reading()
                self.connection.close()
            except Exception as e:
                self.logger.error(f"Disconnect error: {e}")
        
        self.is_connected = False
        self.connection = None
        self.logger.info("Disconnected from Flipper Zero")
    
    def _enter_cli_mode(self) -> bool:
        """Enter CLI mode for command execution."""
        try:
            # Send empty line to enter CLI
            self.connection.write(b"\n")
            self.connection.flush()
            asyncio.sleep(0.5)
            
            # Clear buffer
            self.connection.reset_input_buffer()
            
            return True
        except Exception as e:
            self.logger.error(f"CLI mode failed: {e}")
            return False
    
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
            self.connection.write(f"{command}\r\n".encode())
            self.connection.flush()
            
            # Read response
            response_lines = []
            while True:
                line = self.connection.readline().decode().strip()
                if not line:
                    break
                response_lines.append(line)
                if line.startswith(">:"):  # CLI prompt
                    break
            
            return "\n".join(response_lines)
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return None
    
    async def read_rfid_125khz(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> Optional[RFIDTag]:
        """
        Read 125kHz RFID tag.
        
        Args:
            duration: Read timeout in seconds
            callback: Optional callback when tag detected
        
        Returns:
            RFID tag information or None
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return None
        
        try:
            self.is_reading = True
            
            # Start RFID read
            response = self._send_command("rfid read")
            
            # Wait for tag detection
            await asyncio.sleep(duration)
            
            # Parse response
            tag = self._parse_rfid_response(response, FlipperProtocol.RFID_125KHZ)
            
            if tag:
                self.rfid_tags.append(tag)
                if callback:
                    callback(tag)
            
            self.is_reading = False
            return tag
            
        except Exception as e:
            self.logger.error(f"RFID read failed: {e}")
            self.is_reading = False
            return None
    
    async def read_nfc(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> Optional[NFCTag]:
        """
        Read NFC tag.
        
        Args:
            duration: Read timeout in seconds
            callback: Optional callback when tag detected
        
        Returns:
            NFC tag information or None
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return None
        
        try:
            self.is_reading = True
            
            # Start NFC read
            response = self._send_command("nfc detect")
            
            # Wait for tag detection
            await asyncio.sleep(duration)
            
            # Parse response
            tag = self._parse_nfc_response(response)
            
            if tag:
                self.nfc_tags.append(tag)
                if callback:
                    callback(tag)
            
            self.is_reading = False
            return tag
            
        except Exception as e:
            self.logger.error(f"NFC read failed: {e}")
            self.is_reading = False
            return None
    
    async def receive_subghz(
        self,
        frequency: float = 433.92,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> List[SubGHzSignal]:
        """
        Receive Sub-GHz signals.
        
        Args:
            frequency: Frequency in MHz (e.g., 433.92, 315.00)
            duration: Receive duration in seconds
            callback: Optional callback for detected signals
        
        Returns:
            List of received signals
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return []
        
        try:
            self.is_reading = True
            signals = []
            
            # Set frequency and start receiving
            self._send_command(f"subghz rx {frequency}")
            
            # Receive for specified duration
            await asyncio.sleep(duration)
            
            # Stop receiving
            response = self._send_command("subghz stop")
            
            # Parse received signals
            parsed_signals = self._parse_subghz_response(response, frequency)
            
            for signal in parsed_signals:
                self.subghz_signals.append(signal)
                signals.append(signal)
                if callback:
                    callback(signal)
            
            self.is_reading = False
            return signals
            
        except Exception as e:
            self.logger.error(f"Sub-GHz receive failed: {e}")
            self.is_reading = False
            return []
    
    def transmit_subghz(
        self,
        frequency: float,
        protocol: str,
        data: str,
    ) -> bool:
        """
        Transmit Sub-GHz signal.
        
        Args:
            frequency: Frequency in MHz
            protocol: Protocol name
            data: Data to transmit
        
        Returns:
            True if transmitted successfully
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return False
        
        try:
            # Build transmit command
            command = f"subghz tx {frequency} {protocol} {data}"
            response = self._send_command(command)
            
            success = response and "OK" in response
            if success:
                self.logger.info(f"Transmitted Sub-GHz signal on {frequency} MHz")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Sub-GHz transmit failed: {e}")
            return False
    
    async def receive_infrared(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None,
    ) -> Optional[IRSignal]:
        """
        Receive infrared signal.
        
        Args:
            duration: Receive timeout in seconds
            callback: Optional callback when signal detected
        
        Returns:
            IR signal information or None
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return None
        
        try:
            self.is_reading = True
            
            # Start IR receive
            response = self._send_command("ir rx")
            
            # Wait for signal
            await asyncio.sleep(duration)
            
            # Stop receiving
            self._send_command("ir stop")
            
            # Parse response
            signal = self._parse_ir_response(response)
            
            if signal:
                self.ir_signals.append(signal)
                if callback:
                    callback(signal)
            
            self.is_reading = False
            return signal
            
        except Exception as e:
            self.logger.error(f"IR receive failed: {e}")
            self.is_reading = False
            return None
    
    def transmit_infrared(
        self,
        protocol: str,
        address: str,
        command: str,
    ) -> bool:
        """
        Transmit infrared signal.
        
        Args:
            protocol: IR protocol name
            address: Device address
            command: Command code
        
        Returns:
            True if transmitted successfully
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return False
        
        try:
            # Build transmit command
            cmd = f"ir tx {protocol} {address} {command}"
            response = self._send_command(cmd)
            
            success = response and "OK" in response
            if success:
                self.logger.info(f"Transmitted IR signal: {protocol}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"IR transmit failed: {e}")
            return False
    
    def set_gpio(self, pin: int, state: bool) -> bool:
        """
        Set GPIO pin state.
        
        Args:
            pin: GPIO pin number
            state: True for HIGH, False for LOW
        
        Returns:
            True if set successfully
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return False
        
        try:
            state_str = "1" if state else "0"
            command = f"gpio set {pin} {state_str}"
            response = self._send_command(command)
            
            success = response and "OK" in response
            return success
            
        except Exception as e:
            self.logger.error(f"GPIO set failed: {e}")
            return False
    
    def read_gpio(self, pin: int) -> Optional[bool]:
        """
        Read GPIO pin state.
        
        Args:
            pin: GPIO pin number
        
        Returns:
            Pin state (True=HIGH, False=LOW) or None if failed
        """
        if not self.is_connected:
            self.logger.error("Device not connected")
            return None
        
        try:
            command = f"gpio read {pin}"
            response = self._send_command(command)
            
            if response and "1" in response:
                return True
            elif response and "0" in response:
                return False
            
            return None
            
        except Exception as e:
            self.logger.error(f"GPIO read failed: {e}")
            return None
    
    def stop_reading(self) -> bool:
        """
        Stop current reading operation.
        
        Returns:
            True if stopped successfully
        """
        if not self.is_connected:
            return False
        
        try:
            # Send stop commands for various protocols
            self._send_command("rfid stop")
            self._send_command("nfc stop")
            self._send_command("subghz stop")
            self._send_command("ir stop")
            
            self.is_reading = False
            self.logger.info("Stopped reading")
            return True
            
        except Exception as e:
            self.logger.error(f"Stop failed: {e}")
            return False
    
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
            "is_reading": self.is_reading,
            "rfid_tags": len(self.rfid_tags),
            "nfc_tags": len(self.nfc_tags),
            "subghz_signals": len(self.subghz_signals),
            "ir_signals": len(self.ir_signals),
        }
    
    def _parse_rfid_response(
        self,
        response: Optional[str],
        protocol: FlipperProtocol,
    ) -> Optional[RFIDTag]:
        """Parse RFID response."""
        if not response:
            return None
        
        try:
            # Basic parsing - would need actual Flipper response format
            lines = response.split("\n")
            for line in lines:
                if "UID:" in line:
                    uid = line.split("UID:")[-1].strip()
                    return RFIDTag(
                        tag_type="Unknown",
                        uid=uid,
                        protocol=protocol,
                    )
        except Exception:
            pass
        
        return None
    
    def _parse_nfc_response(self, response: Optional[str]) -> Optional[NFCTag]:
        """Parse NFC response."""
        if not response:
            return None
        
        try:
            # Basic parsing - would need actual Flipper response format
            lines = response.split("\n")
            uid = ""
            atqa = ""
            sak = ""
            
            for line in lines:
                if "UID:" in line:
                    uid = line.split("UID:")[-1].strip()
                elif "ATQA:" in line:
                    atqa = line.split("ATQA:")[-1].strip()
                elif "SAK:" in line:
                    sak = line.split("SAK:")[-1].strip()
            
            if uid:
                return NFCTag(
                    tag_type="Unknown",
                    uid=uid,
                    atqa=atqa,
                    sak=sak,
                )
        except Exception:
            pass
        
        return None
    
    def _parse_subghz_response(
        self,
        response: Optional[str],
        frequency: float,
    ) -> List[SubGHzSignal]:
        """Parse Sub-GHz response."""
        signals = []
        if not response:
            return signals
        
        try:
            # Basic parsing - would need actual Flipper response format
            lines = response.split("\n")
            for line in lines:
                if "Protocol:" in line:
                    signal = SubGHzSignal(
                        frequency=frequency,
                        modulation="ASK/OOK",
                        protocol=line.split("Protocol:")[-1].strip(),
                        data="",
                    )
                    signals.append(signal)
        except Exception:
            pass
        
        return signals
    
    def _parse_ir_response(self, response: Optional[str]) -> Optional[IRSignal]:
        """Parse IR response."""
        if not response:
            return None
        
        try:
            # Basic parsing - would need actual Flipper response format
            lines = response.split("\n")
            for line in lines:
                if "Protocol:" in line:
                    protocol = line.split("Protocol:")[-1].strip()
                    return IRSignal(
                        protocol=protocol,
                        address="",
                        command="",
                    )
        except Exception:
            pass
        
        return None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
