"""
Raspberry Pi Pico platform implementation with MicroPython and C SDK support.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class RaspberryPiPicoPlatform(BasePlatform):
    """
    Raspberry Pi Pico platform implementation.
    Supports RP2040 microcontroller with MicroPython and C SDK.
    """
    
    def __init__(self):
        """Initialize Raspberry Pi Pico platform."""
        super().__init__()
        self.name = "raspberry_pi_pico"
        self.supported_languages = ["c", "cpp", "python", "micropython"]
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "serial",
            "uart",
            "i2c",
            "spi",
            "pio",
            "adc",
            "usb",
        ]
        self.peripherals = [
            "led",
            "button",
            "sensor",
            "motor",
            "servo",
            "display",
            "temperature",
            "humidity",
        ]
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Raspberry Pi Pico platform information."""
        return {
            'name': self.name,
            'display_name': 'Raspberry Pi Pico',
            'languages': self.supported_languages,
            'capabilities': self.capabilities,
            'peripherals': self.peripherals,
            'mcu': 'RP2040',
            'cores': 2,
            'clock_speed': '133MHz',
            'voltage': '3.3V',
            'gpio_count': 26,
            'build_system': 'CMake / Pico SDK / MicroPython',
        }
    
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate Raspberry Pi Pico-specific code.
        
        Args:
            spec: Hardware specification
            output_dir: Output directory
            
        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        language = spec.get('language', 'micropython')
        
        if language in ['python', 'micropython']:
            return self._generate_micropython_code(spec, output_dir)
        else:
            return self._generate_c_code(spec, output_dir)
    
    def _generate_micropython_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate MicroPython code for Raspberry Pi Pico."""
        # Generate main file
        main_file = output_dir / "main.py"
        main_content = self._generate_pico_micropython_main(spec)
        main_file.write_text(main_content)
        
        # Generate config file
        config_file = output_dir / "config.py"
        config_content = self._generate_config_module(spec)
        config_file.write_text(config_content)
        
        return {
            'status': 'success',
            'platform': self.name,
            'language': 'micropython',
            'files_generated': [str(main_file), str(config_file)],
            'output_dir': str(output_dir),
        }
    
    def _generate_c_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate C/C++ code for Raspberry Pi Pico."""
        # Generate main file
        main_file = output_dir / "main.c"
        main_content = self._generate_pico_c_main(spec)
        main_file.write_text(main_content)
        
        # Generate CMakeLists
        cmake_file = output_dir / "CMakeLists.txt"
        cmake_content = self._generate_cmake(spec)
        cmake_file.write_text(cmake_content)
        
        return {
            'status': 'success',
            'platform': self.name,
            'language': 'c',
            'files_generated': [str(main_file), str(cmake_file)],
            'output_dir': str(output_dir),
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate Raspberry Pi Pico configuration."""
        errors = []
        
        # Check for required fields
        if 'device_name' not in config:
            errors.append("Missing required field: device_name")
        
        # Validate peripherals
        peripherals = config.get('peripherals', [])
        for peripheral in peripherals:
            if 'type' not in peripheral:
                errors.append(f"Peripheral missing type: {peripheral}")
            elif peripheral['type'] not in self.peripherals:
                errors.append(f"Unsupported peripheral type: {peripheral['type']}")
            
            # Validate pin numbers (0-28 for Pico)
            if 'pin' in peripheral:
                pin = peripheral['pin']
                if isinstance(pin, int) and (pin < 0 or pin > 28):
                    errors.append(f"Invalid pin number {pin}. Pico supports pins 0-28")
        
        return errors
    
    def get_build_config(self) -> Dict[str, Any]:
        """Get Raspberry Pi Pico build configuration."""
        return {
            'platform': 'raspberry_pi_pico',
            'build_system': 'cmake',
            'sdk': 'pico-sdk',
            'upload_tool': 'picotool / drag-and-drop',
        }
    
    def _generate_pico_micropython_main(self, spec: Dict[str, Any]) -> str:
        """Generate MicroPython main.py file for Raspberry Pi Pico."""
        lines = [
            f"# Auto-generated MicroPython firmware for {spec.get('device_name', 'Unknown')}",
            f"# Platform: Raspberry Pi Pico (RP2040)",
            "",
            "from machine import Pin, PWM, ADC",
            "import time",
            "from config import *",
            "",
        ]
        
        # Initialize peripherals
        lines.append("# Initialize peripherals")
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            name = peripheral.get('name', ptype)
            
            if ptype == 'led':
                lines.append(f"{name} = Pin({pin}, Pin.OUT)")
            elif ptype == 'button':
                lines.append(f"{name} = Pin({pin}, Pin.IN, Pin.PULL_UP)")
            elif ptype == 'sensor':
                lines.append(f"{name} = ADC({pin})")
            elif ptype == 'servo':
                lines.append(f"{name} = PWM(Pin({pin}))")
                lines.append(f"{name}.freq(50)")
        
        lines.append("")
        
        lines.extend([
            "# Main loop",
            "def main():",
        ])
        
        # Add peripheral handling
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            name = peripheral.get('name', ptype)
            
            if ptype == 'sensor':
                lines.append(f"    value = {name}.read_u16()")
                lines.append(f"    print('Sensor value:', value)")
            elif ptype == 'led':
                lines.append(f"    {name}.value(1)")
                lines.append("    time.sleep(1)")
                lines.append(f"    {name}.value(0)")
                lines.append("    time.sleep(1)")
        
        lines.extend([
            "",
            "if __name__ == '__main__':",
            "    while True:",
            "        main()",
            "        time.sleep(0.1)",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_pico_c_main(self, spec: Dict[str, Any]) -> str:
        """Generate C main.c file for Raspberry Pi Pico."""
        lines = [
            f"// Auto-generated C firmware for {spec.get('device_name', 'Unknown')}",
            f"// Platform: Raspberry Pi Pico (RP2040)",
            "",
            "#include <stdio.h>",
            '#include "pico/stdlib.h"',
            "",
        ]
        
        # Add PWM includes if needed
        has_pwm = any(p.get('type') in ['servo', 'motor'] for p in spec.get('peripherals', []))
        if has_pwm:
            lines.append('#include "hardware/pwm.h"')
        
        # Add ADC includes if needed
        has_adc = any(p.get('type') == 'sensor' for p in spec.get('peripherals', []))
        if has_adc:
            lines.append('#include "hardware/adc.h"')
        
        lines.append("")
        
        # Pin definitions
        lines.append("// Pin definitions")
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            name = peripheral.get('name', ptype).upper()
            lines.append(f"#define {name}_PIN {pin}")
        
        lines.extend([
            "",
            "int main() {",
            "    // Initialize stdio",
            "    stdio_init_all();",
            "",
        ])
        
        # Initialize GPIO
        lines.append("    // Initialize GPIO")
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            
            if ptype == 'led':
                lines.append(f"    gpio_init({pin});")
                lines.append(f"    gpio_set_dir({pin}, GPIO_OUT);")
            elif ptype == 'button':
                lines.append(f"    gpio_init({pin});")
                lines.append(f"    gpio_set_dir({pin}, GPIO_IN);")
                lines.append(f"    gpio_pull_up({pin});")
        
        # Initialize ADC if needed
        if has_adc:
            lines.extend([
                "",
                "    // Initialize ADC",
                "    adc_init();",
            ])
            for peripheral in spec.get('peripherals', []):
                if peripheral.get('type') == 'sensor':
                    pin = peripheral.get('pin')
                    if 26 <= pin <= 28:  # ADC pins
                        adc_channel = pin - 26
                        lines.append(f"    adc_gpio_init({pin});")
        
        lines.extend([
            "",
            "    // Main loop",
            "    while (1) {",
        ])
        
        # Add peripheral handling
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            
            if ptype == 'led':
                lines.append(f"        gpio_put({pin}, 1);")
                lines.append("        sleep_ms(1000);")
                lines.append(f"        gpio_put({pin}, 0);")
                lines.append("        sleep_ms(1000);")
            elif ptype == 'sensor':
                if 26 <= pin <= 28:
                    adc_channel = pin - 26
                    lines.append(f"        adc_select_input({adc_channel});")
                    lines.append(f"        uint16_t result = adc_read();")
                    lines.append(f"        printf(\"Sensor value: %d\\n\", result);")
        
        lines.extend([
            "    }",
            "",
            "    return 0;",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_cmake(self, spec: Dict[str, Any]) -> str:
        """Generate CMakeLists.txt for Raspberry Pi Pico."""
        lines = [
            f"# Auto-generated CMakeLists.txt for {spec.get('device_name', 'Unknown')}",
            "",
            "cmake_minimum_required(VERSION 3.13)",
            "",
            "# Include Pico SDK",
            "include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)",
            "",
            f"project({spec.get('device_name', 'pico_project').replace(' ', '_')})",
            "",
            "# Initialize Pico SDK",
            "pico_sdk_init()",
            "",
            "# Add executable",
            "add_executable(main",
            "    main.c",
            ")",
            "",
            "# Link libraries",
            "target_link_libraries(main",
            "    pico_stdlib",
        ]
        
        # Add PWM library if needed
        has_pwm = any(p.get('type') in ['servo', 'motor'] for p in spec.get('peripherals', []))
        if has_pwm:
            lines.append("    hardware_pwm")
        
        # Add ADC library if needed
        has_adc = any(p.get('type') == 'sensor' for p in spec.get('peripherals', []))
        if has_adc:
            lines.append("    hardware_adc")
        
        lines.extend([
            ")",
            "",
            "# Enable USB output, disable UART output",
            "pico_enable_stdio_usb(main 1)",
            "pico_enable_stdio_uart(main 0)",
            "",
            "# Create map/bin/hex/uf2 files",
            "pico_add_extra_outputs(main)",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_config_module(self, spec: Dict[str, Any]) -> str:
        """Generate config.py module."""
        lines = [
            "# Auto-generated configuration module",
            "",
            "# Device configuration",
            f"DEVICE_NAME = '{spec.get('device_name', 'Unknown')}'",
            "",
        ]
        
        # Add pin definitions
        if 'pins' in spec:
            lines.append("# Pin definitions")
            for name, value in spec['pins'].items():
                lines.append(f"{name} = {value}")
            lines.append("")
        
        # Add timing configurations
        if 'timing' in spec:
            lines.append("# Timing configurations")
            for name, value in spec['timing'].items():
                lines.append(f"{name} = {value}")
            lines.append("")
        
        return "\n".join(lines)
