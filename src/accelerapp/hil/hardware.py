"""
Hardware abstraction for HIL testing.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum


class PinMode(Enum):
    """Pin modes for hardware interfaces."""
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    PWM = "pwm"


class HardwareInterface(ABC):
    """
    Abstract interface for hardware communication.
    Provides common interface for different hardware platforms.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the hardware.
        
        Returns:
            True if connected successfully
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the hardware."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to hardware.
        
        Returns:
            True if connected
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset the hardware."""
        pass
    
    @abstractmethod
    def digital_write(self, pin: int, value: bool):
        """
        Write digital value to pin.
        
        Args:
            pin: Pin number
            value: Digital value (True/False)
        """
        pass
    
    @abstractmethod
    def digital_read(self, pin: int) -> bool:
        """
        Read digital value from pin.
        
        Args:
            pin: Pin number
            
        Returns:
            Digital value (True/False)
        """
        pass
    
    @abstractmethod
    def analog_write(self, pin: int, value: int):
        """
        Write analog value to pin (PWM).
        
        Args:
            pin: Pin number
            value: Analog value (0-255 or 0-1023 depending on platform)
        """
        pass
    
    @abstractmethod
    def analog_read(self, pin: int) -> int:
        """
        Read analog value from pin.
        
        Args:
            pin: Pin number
            
        Returns:
            Analog value
        """
        pass
    
    @abstractmethod
    def set_pin_mode(self, pin: int, mode: PinMode):
        """
        Set pin mode.
        
        Args:
            pin: Pin number
            mode: Pin mode
        """
        pass


class DeviceAdapter:
    """
    Adapter for specific hardware devices.
    Maps device operations to hardware interface calls.
    """
    
    def __init__(
        self,
        hardware: HardwareInterface,
        device_type: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize device adapter.
        
        Args:
            hardware: Hardware interface
            device_type: Type of device (arduino, stm32, esp32, etc.)
            config: Device configuration
        """
        self.hardware = hardware
        self.device_type = device_type
        self.config = config or {}
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the device.
        
        Returns:
            True if initialized successfully
        """
        if not self.hardware.connect():
            return False
        
        self.initialized = True
        return True
    
    def shutdown(self):
        """Shutdown the device."""
        self.hardware.disconnect()
        self.initialized = False
    
    def test_led(self, pin: int, duration: float = 1.0) -> bool:
        """
        Test LED by blinking it.
        
        Args:
            pin: LED pin number
            duration: Blink duration in seconds
            
        Returns:
            True if test passed
        """
        if not self.initialized:
            return False
        
        try:
            self.hardware.set_pin_mode(pin, PinMode.OUTPUT)
            self.hardware.digital_write(pin, True)
            import time
            time.sleep(duration)
            self.hardware.digital_write(pin, False)
            return True
        except:
            return False
    
    def test_button(self, pin: int, timeout: float = 5.0) -> Optional[bool]:
        """
        Test button by reading its state.
        
        Args:
            pin: Button pin number
            timeout: Read timeout
            
        Returns:
            Button state or None if timeout
        """
        if not self.initialized:
            return None
        
        try:
            self.hardware.set_pin_mode(pin, PinMode.INPUT_PULLUP)
            return self.hardware.digital_read(pin)
        except:
            return None
    
    def test_analog_sensor(self, pin: int) -> Optional[int]:
        """
        Test analog sensor by reading its value.
        
        Args:
            pin: Sensor pin number
            
        Returns:
            Sensor value or None if error
        """
        if not self.initialized:
            return None
        
        try:
            return self.hardware.analog_read(pin)
        except:
            return None
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information.
        
        Returns:
            Device info dictionary
        """
        return {
            'device_type': self.device_type,
            'initialized': self.initialized,
            'connected': self.hardware.is_connected(),
            'config': self.config,
        }


class SimulatedHardware(HardwareInterface):
    """
    Simulated hardware interface for testing without physical hardware.
    """
    
    def __init__(self):
        """Initialize simulated hardware."""
        self.connected = False
        self.pin_states: Dict[int, bool] = {}
        self.analog_values: Dict[int, int] = {}
        self.pin_modes: Dict[int, PinMode] = {}
    
    def connect(self) -> bool:
        """Simulate connection."""
        self.connected = True
        return True
    
    def disconnect(self):
        """Simulate disconnection."""
        self.connected = False
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected
    
    def reset(self):
        """Reset simulated hardware."""
        self.pin_states.clear()
        self.analog_values.clear()
        self.pin_modes.clear()
    
    def digital_write(self, pin: int, value: bool):
        """Simulate digital write."""
        self.pin_states[pin] = value
    
    def digital_read(self, pin: int) -> bool:
        """Simulate digital read."""
        return self.pin_states.get(pin, False)
    
    def analog_write(self, pin: int, value: int):
        """Simulate analog write."""
        self.analog_values[pin] = value
    
    def analog_read(self, pin: int) -> int:
        """Simulate analog read."""
        return self.analog_values.get(pin, 0)
    
    def set_pin_mode(self, pin: int, mode: PinMode):
        """Set pin mode."""
        self.pin_modes[pin] = mode
