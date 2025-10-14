"""
MicroPython platform implementation for rapid prototyping.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class MicroPythonPlatform(BasePlatform):
    """
    MicroPython platform implementation.
    Supports ESP32, Pyboard, and other MicroPython-compatible boards.
    """

    def __init__(self):
        """Initialize MicroPython platform."""
        super().__init__()
        self.name = "micropython"
        self.supported_languages = ["python", "micropython"]
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "serial",
            "i2c",
            "spi",
            "wifi",
            "bluetooth",
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
        """Get MicroPython platform information."""
        return {
            "name": self.name,
            "display_name": "MicroPython",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "build_system": "MicroPython / Thonny",
        }

    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate MicroPython-specific code.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main file
        main_file = output_dir / "main.py"
        main_content = self._generate_micropython_main(spec)
        main_file.write_text(main_content)

        # Generate config file
        config_file = output_dir / "config.py"
        config_content = self._generate_config_module(spec)
        config_file.write_text(config_content)

        return {
            "status": "success",
            "platform": self.name,
            "files_generated": [str(main_file), str(config_file)],
            "output_dir": str(output_dir),
        }

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate MicroPython configuration."""
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

        return errors

    def get_build_config(self) -> Dict[str, Any]:
        """Get MicroPython build configuration."""
        return {
            "platform": "micropython",
            "build_system": "micropython",
            "upload_tool": "ampy / rshell",
        }

    def _generate_micropython_main(self, spec: Dict[str, Any]) -> str:
        """Generate MicroPython main.py file."""
        lines = [
            f"# Auto-generated MicroPython firmware for {spec.get('device_name', 'Unknown')}",
            f"# Platform: MicroPython",
            "",
            "import machine",
            "import time",
            "from config import *",
            "",
        ]

        # Add WiFi imports if needed
        if "wifi" in spec:
            lines.extend(
                [
                    "import network",
                    "",
                ]
            )

        # Initialize peripherals
        lines.append("# Initialize peripherals")
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            pin = peripheral.get("pin")
            name = peripheral.get("name", ptype)

            if ptype == "led":
                lines.append(f"{name} = machine.Pin({pin}, machine.Pin.OUT)")
            elif ptype == "button":
                lines.append(f"{name} = machine.Pin({pin}, machine.Pin.IN, machine.Pin.PULL_UP)")
            elif ptype == "sensor":
                lines.append(f"{name} = machine.ADC(machine.Pin({pin}))")

        lines.append("")

        # WiFi setup if configured
        if "wifi" in spec:
            wifi = spec["wifi"]
            lines.extend(
                [
                    "# Setup WiFi",
                    "def connect_wifi():",
                    "    wlan = network.WLAN(network.STA_IF)",
                    "    wlan.active(True)",
                    f"    wlan.connect('{wifi.get('ssid', 'YOUR_SSID')}', '{wifi.get('password', 'YOUR_PASSWORD')}')",
                    "    while not wlan.isconnected():",
                    "        print('Connecting to WiFi...')",
                    "        time.sleep(1)",
                    "    print('Connected to WiFi')",
                    "    print('IP:', wlan.ifconfig()[0])",
                    "",
                    "# Connect to WiFi",
                    "connect_wifi()",
                    "",
                ]
            )

        lines.extend(
            [
                "# Main loop",
                "def main():",
            ]
        )

        # Add peripheral handling
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            name = peripheral.get("name", ptype)

            if ptype == "sensor":
                lines.append(f"    value = {name}.read()")
                lines.append(f"    print('Sensor value:', value)")
            elif ptype == "led":
                lines.append(f"    {name}.value(1)")
                lines.append("    time.sleep(1)")
                lines.append(f"    {name}.value(0)")
                lines.append("    time.sleep(1)")

        lines.extend(
            [
                "",
                "if __name__ == '__main__':",
                "    while True:",
                "        main()",
                "        time.sleep(0.1)",
                "",
            ]
        )

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
        if "pins" in spec:
            lines.append("# Pin definitions")
            for name, value in spec["pins"].items():
                lines.append(f"{name} = {value}")
            lines.append("")

        # Add timing configurations
        if "timing" in spec:
            lines.append("# Timing configurations")
            for name, value in spec["timing"].items():
                lines.append(f"{name} = {value}")
            lines.append("")

        return "\n".join(lines)
