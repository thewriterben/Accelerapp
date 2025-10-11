"""
Raspberry Pi platform implementation with Python and C++ support.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class RaspberryPiPlatform(BasePlatform):
    """
    Raspberry Pi platform implementation.
    Supports Raspberry Pi 3, 4, 5, and Zero models with Linux OS.
    """
    
    def __init__(self):
        """Initialize Raspberry Pi platform."""
        super().__init__()
        self.name = "raspberry_pi"
        self.supported_languages = ["python", "cpp", "c"]
        self.capabilities = [
            "gpio",
            "pwm",
            "serial",
            "uart",
            "i2c",
            "spi",
            "usb",
            "ethernet",
            "wifi",
            "bluetooth",
            "camera",
            "audio",
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
            "camera",
            "wifi_module",
            "bluetooth_module",
        ]
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Raspberry Pi platform information."""
        return {
            'name': self.name,
            'display_name': 'Raspberry Pi',
            'languages': self.supported_languages,
            'capabilities': self.capabilities,
            'peripherals': self.peripherals,
            'cpu': 'ARM Cortex (BCM2835/2711/2712)',
            'os': 'Linux (Raspberry Pi OS)',
            'voltage': '3.3V (GPIO)',
            'gpio_count': 40,
            'build_system': 'Python / GCC / CMake',
        }
    
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate Raspberry Pi-specific code.
        
        Args:
            spec: Hardware specification
            output_dir: Output directory
            
        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        language = spec.get('language', 'python')
        
        if language == 'python':
            return self._generate_python_code(spec, output_dir)
        else:
            return self._generate_cpp_code(spec, output_dir)
    
    def _generate_python_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate Python code for Raspberry Pi."""
        # Generate main file
        main_file = output_dir / "main.py"
        main_content = self._generate_pi_python_main(spec)
        main_file.write_text(main_content)
        
        # Generate config file
        config_file = output_dir / "config.py"
        config_content = self._generate_config_module(spec)
        config_file.write_text(config_content)
        
        # Generate requirements file
        requirements_file = output_dir / "requirements.txt"
        requirements_content = self._generate_requirements(spec)
        requirements_file.write_text(requirements_content)
        
        return {
            'status': 'success',
            'platform': self.name,
            'language': 'python',
            'files_generated': [str(main_file), str(config_file), str(requirements_file)],
            'output_dir': str(output_dir),
        }
    
    def _generate_cpp_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate C++ code for Raspberry Pi."""
        # Generate main file
        main_file = output_dir / "main.cpp"
        main_content = self._generate_pi_cpp_main(spec)
        main_file.write_text(main_content)
        
        # Generate Makefile
        makefile = output_dir / "Makefile"
        makefile_content = self._generate_makefile(spec)
        makefile.write_text(makefile_content)
        
        return {
            'status': 'success',
            'platform': self.name,
            'language': 'cpp',
            'files_generated': [str(main_file), str(makefile)],
            'output_dir': str(output_dir),
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate Raspberry Pi configuration."""
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
            
            # Validate GPIO pin numbers (BCM numbering: 0-27 for most Pis)
            if 'pin' in peripheral:
                pin = peripheral['pin']
                if isinstance(pin, int):
                    # BCM GPIO pins typically 0-27, but some boards have more
                    if pin < 0 or pin > 27:
                        errors.append(f"Warning: GPIO pin {pin} may not be available on all Raspberry Pi models")
        
        return errors
    
    def get_build_config(self) -> Dict[str, Any]:
        """Get Raspberry Pi build configuration."""
        return {
            'platform': 'raspberry_pi',
            'build_system': 'python / gcc',
            'deployment': 'direct execution',
        }
    
    def _generate_pi_python_main(self, spec: Dict[str, Any]) -> str:
        """Generate Python main.py file for Raspberry Pi."""
        lines = [
            f"#!/usr/bin/env python3",
            f"# Auto-generated Python code for {spec.get('device_name', 'Unknown')}",
            f"# Platform: Raspberry Pi",
            "",
            "import time",
            "import signal",
            "import sys",
        ]
        
        # Add GPIO imports
        has_gpio = any(p.get('type') in ['led', 'button', 'sensor'] for p in spec.get('peripherals', []))
        if has_gpio:
            lines.extend([
                "try:",
                "    import RPi.GPIO as GPIO",
                "except ImportError:",
                "    print('RPi.GPIO not installed. Install with: pip install RPi.GPIO')",
                "    sys.exit(1)",
            ])
        
        lines.extend([
            "",
            "from config import *",
            "",
        ])
        
        # Add cleanup handler
        lines.extend([
            "def cleanup(signum=None, frame=None):",
            "    \"\"\"Cleanup GPIO on exit\"\"\"",
            "    print('\\nCleaning up...')",
        ])
        
        if has_gpio:
            lines.append("    GPIO.cleanup()")
        
        lines.extend([
            "    sys.exit(0)",
            "",
            "# Register cleanup handler",
            "signal.signal(signal.SIGINT, cleanup)",
            "signal.signal(signal.SIGTERM, cleanup)",
            "",
        ])
        
        # Initialize GPIO
        if has_gpio:
            lines.extend([
                "# Initialize GPIO",
                "GPIO.setmode(GPIO.BCM)",
                "GPIO.setwarnings(False)",
                "",
            ])
        
        # Initialize peripherals
        lines.append("# Initialize peripherals")
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            name = peripheral.get('name', ptype).upper()
            
            if ptype == 'led':
                lines.append(f"{name}_PIN = {pin}")
                lines.append(f"GPIO.setup({name}_PIN, GPIO.OUT)")
            elif ptype == 'button':
                lines.append(f"{name}_PIN = {pin}")
                lines.append(f"GPIO.setup({name}_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)")
        
        lines.extend([
            "",
            "def main():",
            "    \"\"\"Main control loop\"\"\"",
        ])
        
        # Add peripheral handling
        has_content = False
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            name = peripheral.get('name', ptype).upper()
            
            if ptype == 'led':
                lines.append(f"    GPIO.output({name}_PIN, GPIO.HIGH)")
                lines.append("    time.sleep(1)")
                lines.append(f"    GPIO.output({name}_PIN, GPIO.LOW)")
                lines.append("    time.sleep(1)")
                has_content = True
            elif ptype == 'button':
                lines.append(f"    if GPIO.input({name}_PIN) == GPIO.LOW:")
                lines.append(f"        print('Button pressed')")
                has_content = True
        
        if not has_content:
            lines.append("    pass")
        
        lines.extend([
            "",
            "if __name__ == '__main__':",
            "    print(f'Starting {DEVICE_NAME}...')",
            "    try:",
            "        while True:",
            "            main()",
            "            time.sleep(0.1)",
            "    except KeyboardInterrupt:",
            "        cleanup()",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_pi_cpp_main(self, spec: Dict[str, Any]) -> str:
        """Generate C++ main.cpp file for Raspberry Pi."""
        lines = [
            f"// Auto-generated C++ code for {spec.get('device_name', 'Unknown')}",
            f"// Platform: Raspberry Pi",
            "",
            "#include <iostream>",
            "#include <signal.h>",
            "#include <unistd.h>",
            "#include <wiringPi.h>",
            "",
            "using namespace std;",
            "",
        ]
        
        # Pin definitions
        lines.append("// Pin definitions (BCM numbering)")
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            pin = peripheral.get('pin')
            name = peripheral.get('name', ptype).upper()
            lines.append(f"#define {name}_PIN {pin}")
        
        lines.extend([
            "",
            "void cleanup(int signum) {",
            "    cout << \"\\nCleaning up...\" << endl;",
            "    exit(0);",
            "}",
            "",
            "int main() {",
            "    // Setup signal handlers",
            "    signal(SIGINT, cleanup);",
            "    signal(SIGTERM, cleanup);",
            "",
            "    // Initialize wiringPi (using BCM GPIO numbering)",
            "    wiringPiSetupGpio();",
            "",
            "    // Initialize GPIO",
        ])
        
        # Initialize peripherals
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            name = peripheral.get('name', ptype).upper()
            
            if ptype == 'led':
                lines.append(f"    pinMode({name}_PIN, OUTPUT);")
            elif ptype == 'button':
                lines.append(f"    pinMode({name}_PIN, INPUT);")
                lines.append(f"    pullUpDnControl({name}_PIN, PUD_UP);")
        
        lines.extend([
            "",
            f"    cout << \"Starting {spec.get('device_name', 'device')}...\" << endl;",
            "",
            "    // Main loop",
            "    while (true) {",
        ])
        
        # Add peripheral handling
        for peripheral in spec.get('peripherals', []):
            ptype = peripheral.get('type')
            name = peripheral.get('name', ptype).upper()
            
            if ptype == 'led':
                lines.append(f"        digitalWrite({name}_PIN, HIGH);")
                lines.append("        delay(1000);")
                lines.append(f"        digitalWrite({name}_PIN, LOW);")
                lines.append("        delay(1000);")
            elif ptype == 'button':
                lines.append(f"        if (digitalRead({name}_PIN) == LOW) {{")
                lines.append(f"            cout << \"Button pressed\" << endl;")
                lines.append("        }")
        
        lines.extend([
            "        delay(100);",
            "    }",
            "",
            "    return 0;",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_requirements(self, spec: Dict[str, Any]) -> str:
        """Generate requirements.txt for Python."""
        lines = [
            "# Auto-generated requirements.txt",
            "",
        ]
        
        # Add GPIO library
        has_gpio = any(p.get('type') in ['led', 'button', 'sensor'] for p in spec.get('peripherals', []))
        if has_gpio:
            lines.append("RPi.GPIO>=0.7.0")
        
        # Add other libraries as needed
        if any(p.get('type') == 'camera' for p in spec.get('peripherals', [])):
            lines.append("picamera>=1.13")
        
        lines.append("")
        return "\n".join(lines)
    
    def _generate_makefile(self, spec: Dict[str, Any]) -> str:
        """Generate Makefile for C++ compilation."""
        lines = [
            f"# Auto-generated Makefile for {spec.get('device_name', 'Unknown')}",
            "",
            "CXX = g++",
            "CXXFLAGS = -Wall -O2",
            "LDFLAGS = -lwiringPi",
            "",
            "TARGET = main",
            "SOURCES = main.cpp",
            "OBJECTS = $(SOURCES:.cpp=.o)",
            "",
            "all: $(TARGET)",
            "",
            "$(TARGET): $(OBJECTS)",
            "\t$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)",
            "",
            "%.o: %.cpp",
            "\t$(CXX) $(CXXFLAGS) -c $<",
            "",
            "clean:",
            "\trm -f $(OBJECTS) $(TARGET)",
            "",
            "run: $(TARGET)",
            "\tsudo ./$(TARGET)",
            "",
            ".PHONY: all clean run",
            "",
        ]
        
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
