"""
Arduino platform implementation with comprehensive peripheral support.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class ArduinoPlatform(BasePlatform):
    """
    Arduino platform implementation.
    Supports Arduino Uno, Mega, Nano, and compatible boards.
    """

    def __init__(self):
        """Initialize Arduino platform."""
        super().__init__()
        self.name = "arduino"
        self.supported_languages = ["c", "cpp"]
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "serial",
            "i2c",
            "spi",
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
        """Get Arduino platform information."""
        return {
            "name": self.name,
            "display_name": "Arduino",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": "AVR",
            "clock_speeds": ["8MHz", "16MHz"],
            "voltage": "5V",
            "build_system": "Arduino IDE / PlatformIO",
        }

    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate Arduino-specific code.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main sketch file
        main_file = output_dir / f"{spec.get('device_name', 'sketch')}.ino"
        main_content = self._generate_arduino_sketch(spec)
        main_file.write_text(main_content)

        # Generate config header
        config_file = output_dir / "config.h"
        config_content = self._generate_config_header(spec)
        config_file.write_text(config_content)

        return {
            "status": "success",
            "platform": self.name,
            "files_generated": [str(main_file), str(config_file)],
            "output_dir": str(output_dir),
        }

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate Arduino configuration."""
        errors = []

        # Check for required fields
        if "device_name" not in config:
            errors.append("Missing required field: device_name")

        # Validate peripherals
        peripherals = config.get("peripherals", [])
        for peripheral in peripherals:
            if "type" not in peripheral:
                errors.append(f"Peripheral missing type: {peripheral}")
            elif peripheral["type"] not in self.peripherals:
                errors.append(f"Unsupported peripheral type: {peripheral['type']}")

            if "pin" not in peripheral:
                errors.append(f"Peripheral missing pin assignment: {peripheral}")

        return errors

    def get_build_config(self) -> Dict[str, Any]:
        """Get Arduino build configuration."""
        return {
            "platform": "arduino",
            "build_system": "arduino-cli",
            "board": "arduino:avr:uno",
            "framework": "arduino",
        }

    def _generate_arduino_sketch(self, spec: Dict[str, Any]) -> str:
        """Generate Arduino sketch (.ino) file."""
        lines = [
            f"// Auto-generated Arduino sketch for {spec.get('device_name', 'Unknown')}",
            f"// Platform: Arduino",
            "",
            '#include "config.h"',
            "",
            "void setup() {",
            "    // Initialize serial communication",
            f"    Serial.begin({spec.get('timing', {}).get('BAUD_RATE', 9600)});",
            "",
        ]

        # Initialize peripherals
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            pin = peripheral.get("pin")

            if ptype == "led":
                lines.append(f"    pinMode({pin}, OUTPUT);")
            elif ptype == "button":
                lines.append(f"    pinMode({pin}, INPUT_PULLUP);")
            elif ptype == "sensor":
                lines.append(f"    pinMode({pin}, INPUT);")

        lines.extend(
            [
                "}",
                "",
                "void loop() {",
                "    // Main control loop",
            ]
        )

        # Add peripheral handling
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            pin = peripheral.get("pin")

            if ptype == "sensor":
                lines.append(f"    int sensorValue = analogRead({pin});")
                lines.append(f"    Serial.println(sensorValue);")
            elif ptype == "led":
                lines.append(f"    digitalWrite({pin}, HIGH);")
                lines.append(f"    delay(1000);")
                lines.append(f"    digitalWrite({pin}, LOW);")
                lines.append(f"    delay(1000);")

        lines.extend(
            [
                "}",
                "",
            ]
        )

        return "\n".join(lines)

    def _generate_config_header(self, spec: Dict[str, Any]) -> str:
        """Generate config.h header file."""
        lines = [
            "// Auto-generated configuration header",
            "#ifndef CONFIG_H",
            "#define CONFIG_H",
            "",
            "// Device configuration",
            f"#define DEVICE_NAME \"{spec.get('device_name', 'Unknown')}\"",
            "",
        ]

        # Add pin definitions
        if "pins" in spec:
            lines.append("// Pin definitions")
            for name, value in spec["pins"].items():
                lines.append(f"#define {name} {value}")
            lines.append("")

        # Add timing configurations
        if "timing" in spec:
            lines.append("// Timing configurations")
            for name, value in spec["timing"].items():
                lines.append(f"#define {name} {value}")
            lines.append("")

        lines.extend(
            [
                "#endif // CONFIG_H",
                "",
            ]
        )

        return "\n".join(lines)
