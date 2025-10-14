"""
ESP32 platform implementation with WiFi, Bluetooth, and Camera support.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class ESP32Platform(BasePlatform):
    """
    ESP32 platform implementation.
    Supports ESP32, ESP32-CAM, ESP32-S2, and ESP32-C3 variants.
    """

    def __init__(self):
        """Initialize ESP32 platform."""
        super().__init__()
        self.name = "esp32"
        self.supported_languages = ["c", "cpp", "micropython"]
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "serial",
            "i2c",
            "spi",
            "wifi",
            "bluetooth",
            "ble",
            "camera",
            "rtsp_streaming",
            "websocket",
            "http_server",
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
        """Get ESP32 platform information."""
        return {
            "name": self.name,
            "display_name": "ESP32",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": "Xtensa LX6",
            "clock_speeds": ["80MHz", "160MHz", "240MHz"],
            "voltage": "3.3V",
            "wifi": "IEEE 802.11 b/g/n",
            "bluetooth": "Bluetooth 4.2 BR/EDR and BLE",
            "build_system": "ESP-IDF / PlatformIO / Arduino",
        }

    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate ESP32-specific code.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main file
        main_file = output_dir / "main.cpp"
        main_content = self._generate_esp32_main(spec)
        main_file.write_text(main_content)

        # Generate config header
        config_file = output_dir / "config.h"
        config_content = self._generate_config_header(spec)
        config_file.write_text(config_content)

        # Generate WiFi configuration if needed
        files_generated = [str(main_file), str(config_file)]
        if self._has_wifi_capability(spec):
            wifi_file = output_dir / "wifi_config.h"
            wifi_content = self._generate_wifi_config(spec)
            wifi_file.write_text(wifi_content)
            files_generated.append(str(wifi_file))

        return {
            "status": "success",
            "platform": self.name,
            "files_generated": files_generated,
            "output_dir": str(output_dir),
        }

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate ESP32 configuration."""
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

        # Validate WiFi config if present
        if "wifi" in config:
            wifi = config["wifi"]
            if "ssid" not in wifi:
                errors.append("WiFi configuration missing SSID")

        return errors

    def get_build_config(self) -> Dict[str, Any]:
        """Get ESP32 build configuration."""
        return {
            "platform": "esp32",
            "build_system": "platformio",
            "board": "esp32dev",
            "framework": "arduino",
            "upload_speed": 921600,
        }

    def _has_wifi_capability(self, spec: Dict[str, Any]) -> bool:
        """Check if WiFi is configured."""
        return "wifi" in spec or any(
            p.get("type") == "wifi_module" for p in spec.get("peripherals", [])
        )

    def _generate_esp32_main(self, spec: Dict[str, Any]) -> str:
        """Generate ESP32 main.cpp file."""
        lines = [
            f"// Auto-generated ESP32 firmware for {spec.get('device_name', 'Unknown')}",
            f"// Platform: ESP32",
            "",
            "#include <Arduino.h>",
            '#include "config.h"',
        ]

        # Add WiFi includes if needed
        if self._has_wifi_capability(spec):
            lines.extend(
                [
                    "#include <WiFi.h>",
                    '#include "wifi_config.h"',
                ]
            )

        lines.extend(
            [
                "",
                "void setup() {",
                "    // Initialize serial communication",
                f"    Serial.begin({spec.get('timing', {}).get('BAUD_RATE', 115200)});",
                "",
            ]
        )

        # WiFi initialization
        if self._has_wifi_capability(spec):
            lines.extend(
                [
                    "    // Initialize WiFi",
                    "    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);",
                    "    while (WiFi.status() != WL_CONNECTED) {",
                    '        Serial.println("Connecting to WiFi...");',
                    "        delay(1000);",
                    "    }",
                    '    Serial.println("Connected to WiFi");',
                    "",
                ]
            )

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
            elif ptype == "camera":
                lines.append("    // Camera initialization would go here")

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
                "    delay(100);",
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

    def _generate_wifi_config(self, spec: Dict[str, Any]) -> str:
        """Generate WiFi configuration header."""
        wifi = spec.get("wifi", {})
        lines = [
            "// WiFi configuration",
            "#ifndef WIFI_CONFIG_H",
            "#define WIFI_CONFIG_H",
            "",
            f"#define WIFI_SSID \"{wifi.get('ssid', 'YOUR_SSID')}\"",
            f"#define WIFI_PASSWORD \"{wifi.get('password', 'YOUR_PASSWORD')}\"",
            "",
            "#endif // WIFI_CONFIG_H",
            "",
        ]

        return "\n".join(lines)
