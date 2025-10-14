"""
M5Stack platform implementation.
M5Stack is an ESP32-based modular development platform with built-in display, buttons, and sensors.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class M5StackPlatform(BasePlatform):
    """
    M5Stack platform implementation.
    Supports M5Stack Core, Core2, StickC, and other M5Stack variants.
    Built on ESP32 with integrated display, buttons, and speaker.
    """

    def __init__(self):
        """Initialize M5Stack platform."""
        super().__init__()
        self.name = "m5stack"
        self.supported_languages = ["c", "cpp", "arduino"]
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
            "display",
            "tft",
            "touch",
            "buttons",
            "speaker",
            "sd_card",
            "battery",
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
            "accelerometer",
            "gyroscope",
            "magnetometer",
            "wifi_module",
            "bluetooth_module",
            "speaker",
        ]

    def get_platform_info(self) -> Dict[str, Any]:
        """Get M5Stack platform information."""
        return {
            "name": self.name,
            "display_name": "M5Stack",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": "ESP32 (Xtensa LX6)",
            "clock_speeds": ["80MHz", "160MHz", "240MHz"],
            "voltage": "3.3V",
            "display": "320x240 TFT (ILI9341)",
            "buttons": "A (GPIO39), B (GPIO38), C (GPIO37)",
            "speaker": "GPIO25",
            "i2c": "SDA (GPIO21), SCL (GPIO22)",
            "wifi": "IEEE 802.11 b/g/n",
            "bluetooth": "Bluetooth 4.2 BR/EDR and BLE",
            "build_system": "PlatformIO / Arduino",
            "library": "M5Stack Arduino Library",
        }

    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate M5Stack-specific code.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main file
        main_file = output_dir / "main.cpp"
        main_content = self._generate_m5stack_main(spec)
        main_file.write_text(main_content)

        # Generate config header
        config_file = output_dir / "config.h"
        config_content = self._generate_config_header(spec)
        config_file.write_text(config_content)

        # Generate platformio.ini for easy building
        platformio_file = output_dir / "platformio.ini"
        platformio_content = self._generate_platformio_config(spec)
        platformio_file.write_text(platformio_content)

        files_generated = [str(main_file), str(config_file), str(platformio_file)]

        # Generate WiFi configuration if needed
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
        """Validate M5Stack configuration."""
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

        # Validate M5Stack model if specified
        if "m5stack_model" in config:
            valid_models = ["core", "core2", "stickc", "stickc_plus", "atom", "stamp"]
            if config["m5stack_model"].lower() not in valid_models:
                errors.append(
                    f"Unsupported M5Stack model: {config['m5stack_model']}. "
                    f"Valid models: {', '.join(valid_models)}"
                )

        return errors

    def get_build_config(self) -> Dict[str, Any]:
        """Get M5Stack build configuration."""
        return {
            "platform": "m5stack",
            "build_system": "platformio",
            "board": "m5stack-core-esp32",
            "framework": "arduino",
            "upload_speed": 921600,
            "lib_deps": ["M5Stack", "M5EPD", "M5Core2"],
        }

    def _has_wifi_capability(self, spec: Dict[str, Any]) -> bool:
        """Check if WiFi is configured."""
        return "wifi" in spec or any(
            p.get("type") == "wifi_module" for p in spec.get("peripherals", [])
        )

    def _generate_m5stack_main(self, spec: Dict[str, Any]) -> str:
        """Generate M5Stack main.cpp file."""
        model = spec.get("m5stack_model", "core").lower()
        
        lines = [
            f"// Auto-generated M5Stack firmware for {spec.get('device_name', 'Unknown')}",
            f"// Platform: M5Stack {model.capitalize()}",
            "",
            "#include <M5Stack.h>",
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
                "    // Initialize M5Stack",
                "    M5.begin();",
                "    M5.Power.begin();",
                "",
                "    // Initialize display",
                "    M5.Lcd.fillScreen(BLACK);",
                "    M5.Lcd.setTextColor(WHITE);",
                "    M5.Lcd.setTextSize(2);",
                "    M5.Lcd.setCursor(10, 10);",
                f"    M5.Lcd.println(\"{spec.get('device_name', 'M5Stack Device')}\");",
                "",
            ]
        )

        # WiFi initialization
        if self._has_wifi_capability(spec):
            lines.extend(
                [
                    "    // Initialize WiFi",
                    "    M5.Lcd.println(\"Connecting to WiFi...\");",
                    "    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);",
                    "    while (WiFi.status() != WL_CONNECTED) {",
                    "        delay(500);",
                    '        M5.Lcd.print(".");',
                    "    }",
                    '    M5.Lcd.println("");',
                    '    M5.Lcd.println("WiFi Connected!");',
                    "    M5.Lcd.print(\"IP: \");",
                    "    M5.Lcd.println(WiFi.localIP());",
                    "",
                ]
            )

        # Initialize peripherals (non-built-in)
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            pin = peripheral.get("pin")

            if ptype == "led" and pin:
                lines.append(f"    pinMode({pin}, OUTPUT);")
            elif ptype == "sensor" and pin:
                lines.append(f"    pinMode({pin}, INPUT);")

        lines.extend(
            [
                "",
                "    M5.Lcd.println(\"Ready!\");",
                "}",
                "",
                "void loop() {",
                "    // Update M5Stack hardware",
                "    M5.update();",
                "",
                "    // Handle button presses",
                "    if (M5.BtnA.wasPressed()) {",
                '        M5.Lcd.println("Button A pressed");',
                "    }",
                "    if (M5.BtnB.wasPressed()) {",
                '        M5.Lcd.println("Button B pressed");',
                "    }",
                "    if (M5.BtnC.wasPressed()) {",
                '        M5.Lcd.println("Button C pressed");',
                "    }",
                "",
            ]
        )

        # Add peripheral handling
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            pin = peripheral.get("pin")

            if ptype == "sensor" and pin:
                lines.extend(
                    [
                        f"    // Read sensor on pin {pin}",
                        f"    int sensorValue = analogRead({pin});",
                        "    M5.Lcd.setCursor(10, 100);",
                        '    M5.Lcd.printf("Sensor: %d    ", sensorValue);',
                        "",
                    ]
                )

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
            "// Auto-generated M5Stack configuration header",
            "#ifndef CONFIG_H",
            "#define CONFIG_H",
            "",
            "// Device configuration",
            f"#define DEVICE_NAME \"{spec.get('device_name', 'Unknown')}\"",
            f"#define M5STACK_MODEL \"{spec.get('m5stack_model', 'core').upper()}\"",
            "",
            "// M5Stack hardware pins",
            "#define M5_BUTTON_A 39",
            "#define M5_BUTTON_B 38",
            "#define M5_BUTTON_C 37",
            "#define M5_SPEAKER_PIN 25",
            "#define M5_I2C_SDA 21",
            "#define M5_I2C_SCL 22",
            "",
        ]

        # Add pin definitions
        if "pins" in spec:
            lines.append("// Custom pin definitions")
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
            "// WiFi configuration for M5Stack",
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

    def _generate_platformio_config(self, spec: Dict[str, Any]) -> str:
        """Generate PlatformIO configuration for M5Stack."""
        model = spec.get("m5stack_model", "core").lower()
        
        # Select appropriate board
        board_mapping = {
            "core": "m5stack-core-esp32",
            "core2": "m5stack-core2",
            "stickc": "m5stick-c",
            "stickc_plus": "m5stick-c",
            "atom": "m5stack-atom",
            "stamp": "m5stack-stamps3",
        }
        board = board_mapping.get(model, "m5stack-core-esp32")

        lines = [
            "; PlatformIO Project Configuration for M5Stack",
            "; Auto-generated configuration",
            "",
            "[env:m5stack]",
            "platform = espressif32",
            f"board = {board}",
            "framework = arduino",
            "",
            "; Monitor settings",
            "monitor_speed = 115200",
            "",
            "; Upload settings",
            "upload_speed = 921600",
            "",
            "; Build settings",
            "build_flags = ",
            "    -DCORE_DEBUG_LEVEL=0",
            "    -DBOARD_HAS_PSRAM",
            "",
            "; Library dependencies",
            "lib_deps = ",
            "    M5Stack",
        ]

        # Add model-specific libraries
        if model == "core2":
            lines.append("    M5Core2")
        elif model in ["stickc", "stickc_plus"]:
            lines.append("    M5StickC")
        elif model == "atom":
            lines.append("    M5Atom")

        lines.append("")

        return "\n".join(lines)
