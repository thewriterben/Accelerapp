"""
Base platform implementation for STM32 series.
Provides common functionality for all STM32 variants.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import abstractmethod
from ..base import BasePlatform


class STM32BasePlatform(BasePlatform):
    """
    Base class for all STM32 platform implementations.
    Provides common functionality and HAL integration support.
    """

    def __init__(self):
        """Initialize STM32 base platform."""
        super().__init__()
        self.name = "stm32"
        self.supported_languages = ["c", "cpp"]
        self.mcu_family = "ARM Cortex-M"
        self.voltage = "3.3V"
        
        # Common STM32 capabilities
        self.capabilities = [
            "gpio",
            "pwm",
            "analog_input",
            "adc",
            "dac",
            "serial",
            "uart",
            "i2c",
            "spi",
            "can",
            "usb",
            "ethernet",
            "dma",
            "rtc",
            "timer",
            "watchdog",
        ]
        
        # Common peripheral support
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
            "adc_sensor",
            "dac_output",
        ]
        
        # RTOS support
        self.rtos_support = ["freertos", "threadx", "bare_metal"]
        
    @abstractmethod
    def get_series_info(self) -> Dict[str, Any]:
        """
        Get series-specific information.
        
        Returns:
            Dictionary with series-specific details
        """
        pass
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get STM32 platform information."""
        base_info = {
            "name": self.name,
            "display_name": "STM32",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": self.mcu_family,
            "voltage": self.voltage,
            "build_system": "STM32CubeIDE / PlatformIO",
            "rtos_support": self.rtos_support,
        }
        
        # Merge with series-specific info
        series_info = self.get_series_info()
        base_info.update(series_info)
        
        return base_info
    
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate STM32-specific code with HAL integration.

        Args:
            spec: Hardware specification
            output_dir: Output directory

        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        files_generated = []
        
        # Generate main file
        main_file = output_dir / "main.c"
        main_content = self._generate_main_file(spec)
        main_file.write_text(main_content)
        files_generated.append(str(main_file))

        # Generate config header
        config_file = output_dir / "config.h"
        config_content = self._generate_config_header(spec)
        config_file.write_text(config_content)
        files_generated.append(str(config_file))
        
        # Generate HAL initialization
        hal_init_file = output_dir / "hal_init.c"
        hal_init_content = self._generate_hal_init(spec)
        hal_init_file.write_text(hal_init_content)
        files_generated.append(str(hal_init_file))
        
        # Generate peripheral drivers
        if spec.get("peripherals"):
            drivers_dir = output_dir / "drivers"
            drivers_dir.mkdir(exist_ok=True)
            driver_files = self._generate_peripheral_drivers(spec, drivers_dir)
            files_generated.extend(driver_files)

        return {
            "status": "success",
            "platform": self.name,
            "series": self.get_series_info().get("series", "generic"),
            "files_generated": files_generated,
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

        # Validate RTOS if specified
        rtos = config.get("rtos")
        if rtos and rtos not in self.rtos_support:
            errors.append(f"Unsupported RTOS: {rtos}. Supported: {self.rtos_support}")

        return errors

    def get_build_config(self) -> Dict[str, Any]:
        """Get STM32 build configuration."""
        return {
            "platform": "stm32",
            "build_system": "platformio",
            "framework": "stm32cube",
            "toolchain": "arm-none-eabi-gcc",
            "optimization": "-O2",
        }

    def _generate_main_file(self, spec: Dict[str, Any]) -> str:
        """Generate main.c file with HAL integration."""
        lines = [
            f"/* Auto-generated STM32 firmware for {spec.get('device_name', 'Unknown')} */",
            f"/* Platform: {self.get_series_info().get('series', 'STM32')} */",
            f"/* Generated by Accelerapp v2.0 */",
            "",
            "#include <stdint.h>",
            "#include <stdbool.h>",
            '#include "main.h"',
            '#include "config.h"',
            '#include "hal_init.h"',
            "",
        ]
        
        # Add peripheral driver includes
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f'#include "drivers/{ptype}_driver.h"')
        
        lines.extend([
            "",
            "/* Private function prototypes */",
            "void SystemClock_Config(void);",
            "void Error_Handler(void);",
            "",
            "int main(void) {",
            "    /* Reset of all peripherals, Initializes the Flash interface and the Systick */",
            "    HAL_Init();",
            "",
            "    /* Configure the system clock */",
            "    SystemClock_Config();",
            "",
            "    /* Initialize all configured peripherals */",
            "    HAL_GPIO_Init();",
        ])

        # Initialize peripherals
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"    {ptype}_init();")

        lines.extend([
            "",
            "    /* Infinite loop */",
            "    while (1) {",
        ])

        # Main loop logic
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"        {ptype}_process();")

        lines.extend([
            "    }",
            "}",
            "",
            "void SystemClock_Config(void) {",
            "    /* System Clock Configuration */",
            "    /* This should be generated based on CubeMX settings */",
            "}",
            "",
            "void Error_Handler(void) {",
            "    /* User can add his own implementation to report the HAL error return state */",
            "    __disable_irq();",
            "    while (1) {",
            "        /* Error loop */",
            "    }",
            "}",
            "",
        ])

        return "\n".join(lines)

    def _generate_config_header(self, spec: Dict[str, Any]) -> str:
        """Generate config.h header file."""
        lines = [
            "/* Auto-generated configuration header */",
            "#ifndef CONFIG_H",
            "#define CONFIG_H",
            "",
            "/* Device configuration */",
            f"#define DEVICE_NAME \"{spec.get('device_name', 'Unknown')}\"",
            f"#define PLATFORM \"{self.name}\"",
            "",
        ]

        # Add series-specific defines
        series_info = self.get_series_info()
        if "series" in series_info:
            lines.append(f"#define STM32_SERIES \"{series_info['series']}\"")
        if "max_clock" in series_info:
            lines.append(f"#define MAX_CLOCK_MHZ {series_info['max_clock']}")
        lines.append("")

        # Add peripheral count
        peripheral_count = len(spec.get("peripherals", []))
        lines.extend([
            "/* Peripheral configuration */",
            f"#define PERIPHERAL_COUNT {peripheral_count}",
            "",
        ])

        # Add pin definitions
        if "pins" in spec:
            lines.append("/* Pin definitions */")
            for name, value in spec["pins"].items():
                lines.append(f"#define {name} {value}")
            lines.append("")

        # Add timing configurations
        if "timing" in spec:
            lines.append("/* Timing configurations */")
            for name, value in spec["timing"].items():
                lines.append(f"#define {name} {value}")
            lines.append("")

        # RTOS configuration
        if spec.get("rtos"):
            lines.extend([
                "/* RTOS configuration */",
                f"#define USE_RTOS 1",
                f"#define RTOS_TYPE \"{spec['rtos']}\"",
                "",
            ])

        lines.extend([
            "#endif /* CONFIG_H */",
            "",
        ])

        return "\n".join(lines)

    def _generate_hal_init(self, spec: Dict[str, Any]) -> str:
        """Generate HAL initialization code."""
        lines = [
            "/* HAL initialization code */",
            '#include "hal_init.h"',
            '#include "stm32_hal.h"',
            "",
            "void HAL_GPIO_Init(void) {",
            "    /* GPIO Ports Clock Enable */",
            "    __HAL_RCC_GPIOA_CLK_ENABLE();",
            "    __HAL_RCC_GPIOB_CLK_ENABLE();",
            "    __HAL_RCC_GPIOC_CLK_ENABLE();",
            "",
            "    /* GPIO Configuration */",
            "    /* Add GPIO initialization based on peripherals */",
            "}",
            "",
        ]
        return "\n".join(lines)

    def _generate_peripheral_drivers(self, spec: Dict[str, Any], drivers_dir: Path) -> List[str]:
        """Generate peripheral driver files."""
        files = []
        
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type", "unknown")
            
            # Generate driver header
            header_file = drivers_dir / f"{ptype}_driver.h"
            header_content = self._generate_driver_header(ptype, peripheral)
            header_file.write_text(header_content)
            files.append(str(header_file))
            
            # Generate driver implementation
            source_file = drivers_dir / f"{ptype}_driver.c"
            source_content = self._generate_driver_source(ptype, peripheral)
            source_file.write_text(source_content)
            files.append(str(source_file))
        
        return files

    def _generate_driver_header(self, ptype: str, config: Dict[str, Any]) -> str:
        """Generate driver header file."""
        header_guard = f"{ptype.upper()}_DRIVER_H"
        lines = [
            f"/* {ptype.title()} driver header */",
            f"#ifndef {header_guard}",
            f"#define {header_guard}",
            "",
            '#include <stdint.h>',
            '#include <stdbool.h>',
            "",
            f"/* {ptype.title()} initialization */",
            f"void {ptype}_init(void);",
            "",
            f"/* {ptype.title()} processing */",
            f"void {ptype}_process(void);",
            "",
            f"#endif /* {header_guard} */",
            "",
        ]
        return "\n".join(lines)

    def _generate_driver_source(self, ptype: str, config: Dict[str, Any]) -> str:
        """Generate driver source file."""
        lines = [
            f"/* {ptype.title()} driver implementation */",
            f'#include "{ptype}_driver.h"',
            '#include "stm32_hal.h"',
            "",
            f"void {ptype}_init(void) {{",
            f"    /* Initialize {ptype} */",
            f"    /* Add HAL-specific initialization code */",
            "}",
            "",
            f"void {ptype}_process(void) {{",
            f"    /* Process {ptype} logic */",
            "}",
            "",
        ]
        return "\n".join(lines)
