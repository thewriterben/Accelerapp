"""
GPIO Management for CYD.

Provides unified GPIO control and peripheral management
for ESP32-2432S028 (CYD) boards.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class PinMode(Enum):
    """GPIO pin modes."""
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    INPUT_PULLDOWN = "input_pulldown"
    ANALOG = "analog"


class PinState(Enum):
    """GPIO pin states."""
    LOW = 0
    HIGH = 1


@dataclass
class PinConfig:
    """GPIO pin configuration."""
    pin_number: int
    mode: PinMode
    initial_state: Optional[PinState] = None
    label: Optional[str] = None


class GPIOManager:
    """
    GPIO manager for CYD hardware.
    
    Provides unified interface for GPIO operations including:
    - Pin configuration and management
    - Digital I/O operations
    - Analog input (ADC)
    - PWM output
    - Pin conflict detection
    - Peripheral mapping
    """

    # Standard CYD pin assignments (ESP32-2432S028)
    RESERVED_PINS = {
        # Display pins
        2: "TFT_DC",
        15: "TFT_CS",
        21: "TFT_BL",
        13: "TFT_MOSI",
        14: "TFT_SCK",
        12: "TFT_MISO",
        # Touch pins
        33: "TOUCH_CS",
        36: "TOUCH_IRQ",
        32: "TOUCH_MOSI",
        39: "TOUCH_MISO",
        25: "TOUCH_SCK",
        # SD Card (optional)
        5: "SD_CS",
        # Built-in LED
        17: "LED",
        # LDR (Light Dependent Resistor)
        34: "LDR",
    }

    # Available GPIO pins for user applications
    AVAILABLE_PINS = [0, 4, 16, 22, 23, 26, 27, 35]

    def __init__(self):
        """Initialize GPIO manager."""
        self._pins: Dict[int, PinConfig] = {}
        self._pin_states: Dict[int, PinState] = {}

    def configure_pin(
        self,
        pin: int,
        mode: PinMode,
        initial_state: Optional[PinState] = None,
        label: Optional[str] = None
    ) -> bool:
        """
        Configure a GPIO pin.
        
        Args:
            pin: Pin number
            mode: Pin mode (input/output)
            initial_state: Initial pin state (for outputs)
            label: Optional label for the pin
            
        Returns:
            True if configuration successful
        """
        if pin in self.RESERVED_PINS:
            return False
            
        config = PinConfig(
            pin_number=pin,
            mode=mode,
            initial_state=initial_state,
            label=label
        )
        
        self._pins[pin] = config
        if initial_state is not None:
            self._pin_states[pin] = initial_state
            
        return True

    def digital_write(self, pin: int, state: PinState) -> bool:
        """
        Write digital value to pin.
        
        Args:
            pin: Pin number
            state: Pin state (HIGH/LOW)
            
        Returns:
            True if write successful
        """
        if pin not in self._pins:
            return False
            
        config = self._pins[pin]
        if config.mode != PinMode.OUTPUT:
            return False
            
        self._pin_states[pin] = state
        return True

    def digital_read(self, pin: int) -> Optional[PinState]:
        """
        Read digital value from pin.
        
        Args:
            pin: Pin number
            
        Returns:
            Pin state or None if error
        """
        if pin not in self._pins:
            return None
            
        return self._pin_states.get(pin, PinState.LOW)

    def analog_read(self, pin: int) -> Optional[int]:
        """
        Read analog value from pin (ADC).
        
        Args:
            pin: Pin number (must be ADC-capable)
            
        Returns:
            ADC value (0-4095 for 12-bit) or None if error
        """
        # ESP32 ADC capable pins: 32-39, 34-36
        adc_pins = [32, 33, 34, 35, 36, 39]
        if pin not in adc_pins:
            return None
            
        # Simulated value
        return 0

    def pwm_write(self, pin: int, duty_cycle: int, frequency: int = 5000) -> bool:
        """
        Write PWM signal to pin.
        
        Args:
            pin: Pin number
            duty_cycle: Duty cycle (0-255)
            frequency: PWM frequency in Hz
            
        Returns:
            True if write successful
        """
        if pin not in self._pins:
            return False
            
        # Validate duty cycle
        if not 0 <= duty_cycle <= 255:
            return False
            
        return True

    def get_pin_info(self, pin: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a pin.
        
        Args:
            pin: Pin number
            
        Returns:
            Pin information dictionary or None
        """
        if pin in self.RESERVED_PINS:
            return {
                "pin": pin,
                "status": "reserved",
                "function": self.RESERVED_PINS[pin],
                "available": False,
            }
        elif pin in self._pins:
            config = self._pins[pin]
            return {
                "pin": pin,
                "status": "configured",
                "mode": config.mode.value,
                "label": config.label,
                "available": False,
            }
        elif pin in self.AVAILABLE_PINS:
            return {
                "pin": pin,
                "status": "available",
                "available": True,
            }
        else:
            return None

    def get_available_pins(self) -> List[int]:
        """
        Get list of available GPIO pins.
        
        Returns:
            List of available pin numbers
        """
        return [p for p in self.AVAILABLE_PINS if p not in self._pins]

    def get_reserved_pins(self) -> Dict[int, str]:
        """
        Get dictionary of reserved pins.
        
        Returns:
            Dictionary mapping pin numbers to functions
        """
        return self.RESERVED_PINS.copy()

    def generate_code(self, platform: str = "arduino") -> str:
        """
        Generate platform-specific GPIO initialization code.
        
        Args:
            platform: Target platform (arduino, esp-idf, micropython)
            
        Returns:
            Generated code string
        """
        if platform == "arduino":
            return self._generate_arduino_code()
        elif platform == "esp-idf":
            return self._generate_esp_idf_code()
        elif platform == "micropython":
            return self._generate_micropython_code()
        else:
            return ""

    def _generate_arduino_code(self) -> str:
        """Generate Arduino GPIO configuration code."""
        lines = ["// GPIO Configuration"]
        
        for pin, config in self._pins.items():
            mode_map = {
                PinMode.INPUT: "INPUT",
                PinMode.OUTPUT: "OUTPUT",
                PinMode.INPUT_PULLUP: "INPUT_PULLUP",
                PinMode.INPUT_PULLDOWN: "INPUT_PULLDOWN",
            }
            
            comment = f" // {config.label}" if config.label else ""
            lines.append(f"pinMode({pin}, {mode_map[config.mode]});{comment}")
            
            if config.initial_state and config.mode == PinMode.OUTPUT:
                state = "HIGH" if config.initial_state == PinState.HIGH else "LOW"
                lines.append(f"digitalWrite({pin}, {state});")
        
        return "\n".join(lines)

    def _generate_esp_idf_code(self) -> str:
        """Generate ESP-IDF GPIO configuration code."""
        lines = [
            "// GPIO Configuration for ESP-IDF",
            '#include "driver/gpio.h"',
            "",
            "void gpio_init() {",
        ]
        
        for pin, config in self._pins.items():
            mode_map = {
                PinMode.INPUT: "GPIO_MODE_INPUT",
                PinMode.OUTPUT: "GPIO_MODE_OUTPUT",
                PinMode.INPUT_PULLUP: "GPIO_MODE_INPUT",
                PinMode.INPUT_PULLDOWN: "GPIO_MODE_INPUT",
            }
            
            comment = f" // {config.label}" if config.label else ""
            lines.append(f"    gpio_set_direction(GPIO_NUM_{pin}, {mode_map[config.mode]});{comment}")
            
            if config.mode == PinMode.INPUT_PULLUP:
                lines.append(f"    gpio_set_pull_mode(GPIO_NUM_{pin}, GPIO_PULLUP_ONLY);")
            elif config.mode == PinMode.INPUT_PULLDOWN:
                lines.append(f"    gpio_set_pull_mode(GPIO_NUM_{pin}, GPIO_PULLDOWN_ONLY);")
            
            if config.initial_state and config.mode == PinMode.OUTPUT:
                level = 1 if config.initial_state == PinState.HIGH else 0
                lines.append(f"    gpio_set_level(GPIO_NUM_{pin}, {level});")
        
        lines.append("}")
        return "\n".join(lines)

    def _generate_micropython_code(self) -> str:
        """Generate MicroPython GPIO configuration code."""
        lines = [
            "# GPIO Configuration for MicroPython",
            "from machine import Pin",
            "",
        ]
        
        for pin, config in self._pins.items():
            mode_map = {
                PinMode.INPUT: "Pin.IN",
                PinMode.OUTPUT: "Pin.OUT",
                PinMode.INPUT_PULLUP: "Pin.IN, Pin.PULL_UP",
                PinMode.INPUT_PULLDOWN: "Pin.IN, Pin.PULL_DOWN",
            }
            
            var_name = config.label.lower().replace(" ", "_") if config.label else f"pin_{pin}"
            comment = f"  # {config.label}" if config.label else ""
            
            lines.append(f"{var_name} = Pin({pin}, {mode_map[config.mode]}){comment}")
            
            if config.initial_state and config.mode == PinMode.OUTPUT:
                value = 1 if config.initial_state == PinState.HIGH else 0
                lines.append(f"{var_name}.value({value})")
        
        return "\n".join(lines)
