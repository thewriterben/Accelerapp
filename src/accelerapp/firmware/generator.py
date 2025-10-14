"""
Firmware generator using template-based and AI-assisted generation.
"""

from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


class FirmwareGenerator:
    """
    Generates firmware code for embedded systems based on hardware specifications.
    Supports multiple platforms (Arduino, STM32, ESP32, etc.)
    """

    def __init__(self, hardware_spec: Dict[str, Any]):
        """
        Initialize firmware generator.

        Args:
            hardware_spec: Hardware specification dictionary
        """
        self.hardware_spec = hardware_spec
        self.platform = hardware_spec.get("platform", "arduino")
        self.template_env = self._setup_templates()
        self.ml_config = hardware_spec.get("ml_config", None)

    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment."""
        # Get the templates directory relative to this file
        template_dir = Path(__file__).parent.parent / "templates" / "firmware"

        # Create environment with autoescape for safety
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        return env

    def generate(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate firmware based on hardware specification.

        Args:
            output_dir: Directory to write generated firmware

        Returns:
            Dictionary with generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate main firmware file
        main_code = self._generate_main()
        main_file = output_dir / f"main.{self._get_file_extension()}"
        main_file.write_text(main_code)

        # Generate peripheral drivers if specified
        drivers = self._generate_drivers(output_dir)

        # Generate configuration header
        config = self._generate_config()
        config_file = output_dir / f"config.{self._get_header_extension()}"
        config_file.write_text(config)

        # Generate ML inference code if ML config is present
        ml_files = []
        if self.ml_config:
            ml_files = self._generate_ml_integration(output_dir)

        return {
            "status": "success",
            "platform": self.platform,
            "files_generated": [str(f) for f in [main_file, config_file] + drivers + ml_files],
            "output_dir": str(output_dir),
            "ml_enabled": self.ml_config is not None,
        }

    def _generate_main(self) -> str:
        """Generate main firmware entry point."""
        # Template-based generation with hardware-specific code
        peripherals = self.hardware_spec.get("peripherals", [])

        code_parts = [
            f"// Auto-generated firmware for {self.platform}",
            f"// Hardware: {self.hardware_spec.get('device_name', 'Unknown')}",
            "",
            "#include <stdint.h>",
            '#include "config.h"',
            "",
        ]

        # Add peripheral includes
        for peripheral in peripherals:
            code_parts.append(f'#include "{peripheral["type"]}.h"')

        # Add ML includes if ML is enabled
        if self.ml_config:
            code_parts.append('#include "ml_inference.h"')

        code_parts.extend(
            [
                "",
                "void setup() {",
                "    // Initialize system",
            ]
        )

        # Initialize each peripheral
        for peripheral in peripherals:
            code_parts.append(f"    init_{peripheral['type']}();")

        # Initialize ML if enabled
        if self.ml_config:
            code_parts.extend(
                [
                    "",
                    "    // Initialize ML inference",
                    "    ml_inference_init();",
                ]
            )

        code_parts.extend(
            [
                "}",
                "",
                "void loop() {",
                "    // Main control loop",
            ]
        )

        # Add peripheral handling
        for peripheral in peripherals:
            code_parts.append(f"    handle_{peripheral['type']}();")

        code_parts.extend(
            [
                "}",
                "",
                "int main(void) {",
                "    setup();",
                "    while (1) {",
                "        loop();",
                "    }",
                "    return 0;",
                "}",
                "",
            ]
        )

        return "\n".join(code_parts)

    def _generate_config(self) -> str:
        """Generate configuration header file."""
        config_parts = [
            "#ifndef CONFIG_H",
            "#define CONFIG_H",
            "",
            f"// Configuration for {self.hardware_spec.get('device_name', 'Device')}",
            "",
        ]

        # Add pin definitions
        pins = self.hardware_spec.get("pins", {})
        if pins:
            config_parts.append("// Pin definitions")
            for pin_name, pin_number in pins.items():
                config_parts.append(f"#define {pin_name.upper()} {pin_number}")
            config_parts.append("")

        # Add timing configurations
        timing = self.hardware_spec.get("timing", {})
        if timing:
            config_parts.append("// Timing configurations")
            for param, value in timing.items():
                config_parts.append(f"#define {param.upper()} {value}")
            config_parts.append("")

        config_parts.extend(["#endif // CONFIG_H", ""])

        return "\n".join(config_parts)

    def _generate_drivers(self, output_dir: Path) -> list:
        """Generate peripheral driver files."""
        generated_files = []
        peripherals = self.hardware_spec.get("peripherals", [])

        for peripheral in peripherals:
            driver_code = self._generate_peripheral_driver(peripheral)
            driver_file = output_dir / f"{peripheral['type']}.{self._get_file_extension()}"
            driver_file.write_text(driver_code)

            # Generate header
            header_code = self._generate_peripheral_header(peripheral)
            header_file = output_dir / f"{peripheral['type']}.{self._get_header_extension()}"
            header_file.write_text(header_code)

            generated_files.extend([driver_file, header_file])

        return generated_files

    def _generate_peripheral_driver(self, peripheral: Dict[str, Any]) -> str:
        """Generate driver implementation for a peripheral."""
        p_type = peripheral["type"]

        code = [
            f'#include "{p_type}.h"',
            "",
            f"void init_{p_type}(void) {{",
            f"    // Initialize {p_type}",
            "}",
            "",
            f"void handle_{p_type}(void) {{",
            f"    // Handle {p_type} operations",
            "}",
            "",
        ]

        return "\n".join(code)

    def _generate_peripheral_header(self, peripheral: Dict[str, Any]) -> str:
        """Generate header file for a peripheral."""
        p_type = peripheral["type"]
        guard = f"{p_type.upper()}_H"

        code = [
            f"#ifndef {guard}",
            f"#define {guard}",
            "",
            "#include <stdint.h>",
            "",
            f"void init_{p_type}(void);",
            f"void handle_{p_type}(void);",
            "",
            f"#endif // {guard}",
            "",
        ]

        return "\n".join(code)

    def _get_file_extension(self) -> str:
        """Get the appropriate source file extension for the platform."""
        return "c" if self.platform in ["stm32", "esp32"] else "ino"

    def _get_header_extension(self) -> str:
        """Get the appropriate header file extension."""
        return "h"

    def _generate_ml_integration(self, output_dir: Path) -> list:
        """
        Generate ML inference integration code.

        Args:
            output_dir: Directory to write ML files

        Returns:
            List of generated ML files
        """
        try:
            from accelerapp.agents.tinyml_agent import TinyMLAgent
        except ImportError:
            # TinyML agent not available
            return []

        agent = TinyMLAgent()

        # Prepare ML specification from config
        ml_spec = {
            "task_type": self.ml_config.get("task_type", "inference"),
            "platform": self.platform,
            "model_type": self.ml_config.get("model_type", "classification"),
            "input_shape": self.ml_config.get("input_shape", [1, 28, 28, 1]),
            "num_classes": self.ml_config.get("num_classes", 10),
        }

        # Generate ML code
        result = agent.generate(ml_spec)

        if result["status"] != "success":
            return []

        # Save generated ML files
        generated_files = []
        for filename, content in result["files"].items():
            filepath = output_dir / filename
            filepath.write_text(content)
            generated_files.append(filepath)

        return generated_files
