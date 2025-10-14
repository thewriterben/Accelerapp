"""
STM32 platform implementation for industrial applications.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base import BasePlatform


class STM32Platform(BasePlatform):
    """
    STM32 platform implementation.
    Supports STM32F, STM32L, and STM32H series microcontrollers.
    """

    def __init__(self):
        """Initialize STM32 platform."""
        super().__init__()
        self.name = "stm32"
        self.supported_languages = ["c", "cpp"]
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "serial",
            "i2c",
            "spi",
            "can",
            "usb",
            "ethernet",
            "dma",
            "rtc",
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
            "can_transceiver",
            "ethernet_phy",
        ]

    def get_platform_info(self) -> Dict[str, Any]:
        """Get STM32 platform information."""
        return {
            "name": self.name,
            "display_name": "STM32",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": "ARM Cortex-M",
            "clock_speeds": ["48MHz", "72MHz", "84MHz", "168MHz", "216MHz"],
            "voltage": "3.3V",
            "build_system": "STM32CubeIDE / PlatformIO",
        }

    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate STM32-specific code.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main file
        main_file = output_dir / "main.c"
        main_content = self._generate_stm32_main(spec)
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
        """Validate STM32 configuration."""
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
        """Get STM32 build configuration."""
        return {
            "platform": "stm32",
            "build_system": "platformio",
            "board": "nucleo_f401re",
            "framework": "stm32cube",
        }

    def _generate_stm32_main(self, spec: Dict[str, Any]) -> str:
        """Generate STM32 main.c file."""
        lines = [
            f"// Auto-generated STM32 firmware for {spec.get('device_name', 'Unknown')}",
            f"// Platform: STM32",
            "",
            "#include <stdint.h>",
            "#include <stdbool.h>",
            '#include "config.h"',
            "",
            "// HAL includes would go here",
            '// #include "stm32f4xx_hal.h"',
            "",
            "void SystemClock_Config(void);",
            "void GPIO_Init(void);",
            "",
            "int main(void) {",
            "    // Initialize HAL",
            "    // HAL_Init();",
            "",
            "    // Configure system clock",
            "    // SystemClock_Config();",
            "",
            "    // Initialize GPIO",
            "    // GPIO_Init();",
            "",
        ]

        # Initialize peripherals
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"    // Initialize {ptype}")

        lines.extend(
            [
                "",
                "    // Main loop",
                "    while (1) {",
                "        // Main control logic",
            ]
        )

        # Add peripheral handling
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"        // Handle {ptype}")

        lines.extend(
            [
                "    }",
                "}",
                "",
                "void SystemClock_Config(void) {",
                "    // Clock configuration",
                "}",
                "",
                "void GPIO_Init(void) {",
                "    // GPIO initialization",
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
