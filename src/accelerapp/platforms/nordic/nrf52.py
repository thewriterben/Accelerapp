"""
Nordic nRF52 series platform implementation.
Supports nRF52832, nRF52840 with BLE stack and Zephyr RTOS.
"""

from typing import Dict, Any, List
from pathlib import Path
from ..base import BasePlatform


class NRF52Platform(BasePlatform):
    """
    Nordic nRF52 series platform implementation.
    Optimized for Bluetooth Low Energy and IoT applications.
    """

    def __init__(self):
        """Initialize nRF52 platform."""
        super().__init__()
        self.name = "nrf52"
        self.supported_languages = ["c", "cpp"]
        
        # nRF52 capabilities
        self.capabilities = [
            "gpio",
            "pwm",
            "adc",
            "uart",
            "i2c",
            "spi",
            "ble",  # Bluetooth Low Energy
            "nfc",  # NFC (nRF52840)
            "usb",  # USB 2.0 (nRF52840)
            "timer",
            "rtc",
            "wdt",  # Watchdog timer
            "radio",  # 2.4GHz radio
            "crypto",  # ARM CryptoCell
            "ppi",  # Programmable Peripheral Interconnect
        ]
        
        self.peripherals = [
            "led",
            "button",
            "sensor",
            "ble_peripheral",
            "ble_central",
            "nfc_tag",
            "temperature_sensor",
            "battery_monitor",
        ]
        
        # RTOS and SDK support
        self.rtos_support = ["zephyr", "freertos", "nordic_sdk", "bare_metal"]
        self.sdk_versions = ["nRF5_SDK_17.1.0", "nRF_Connect_SDK_2.0"]
        
    def get_platform_info(self) -> Dict[str, Any]:
        """Get nRF52 platform information."""
        return {
            "name": self.name,
            "display_name": "Nordic nRF52",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "mcu_family": "ARM Cortex-M4F",
            "variants": ["nRF52832", "nRF52840"],
            "core": "ARM Cortex-M4 with FPU",
            "max_clock": 64,  # MHz
            "flash_range": "256KB - 1MB",
            "ram_range": "32KB - 256KB",
            "voltage_range": "1.7V - 3.6V",
            "wireless": {
                "ble": "Bluetooth 5.3 compatible",
                "protocols": ["BLE", "ANT", "IEEE 802.15.4", "Thread", "Zigbee"],
                "tx_power": "+8 dBm (nRF52840)",
                "rx_sensitivity": "-95 dBm",
            },
            "build_system": "nRF Connect SDK / PlatformIO / Segger",
            "rtos_support": self.rtos_support,
            "power_modes": ["Active", "Idle", "System ON sleep", "System OFF"],
            "key_features": [
                "Bluetooth 5.3 Low Energy",
                "Ultra-low power consumption",
                "ARM TrustZone security",
                "Hardware cryptographic acceleration",
                "NFC-A tag (nRF52840)",
                "USB 2.0 device (nRF52840)",
            ],
        }
    
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate nRF52-specific code.

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

        # Generate SDK configuration
        sdk_config_file = output_dir / "sdk_config.h"
        sdk_config_content = self._generate_sdk_config(spec)
        sdk_config_file.write_text(sdk_config_content)
        files_generated.append(str(sdk_config_file))
        
        # Generate BLE services if BLE is enabled
        if self._has_ble_peripherals(spec):
            ble_service_file = output_dir / "ble_service.c"
            ble_service_content = self._generate_ble_service(spec)
            ble_service_file.write_text(ble_service_content)
            files_generated.append(str(ble_service_file))

        return {
            "status": "success",
            "platform": self.name,
            "files_generated": files_generated,
            "output_dir": str(output_dir),
            "sdk_version": self.sdk_versions[0],
        }

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate nRF52 configuration."""
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
        """Get nRF52 build configuration."""
        return {
            "platform": "nordicnrf52",
            "board": "nrf52840_dk",
            "build_system": "cmake",
            "framework": "zephyr",
            "toolchain": "arm-none-eabi-gcc",
            "sdk": "nRF_Connect_SDK",
            "optimization": "-Os",  # Optimize for size (important for nRF)
            "softdevice": "s140",  # BLE stack
        }

    def _generate_main_file(self, spec: Dict[str, Any]) -> str:
        """Generate main.c file."""
        lines = [
            f"/* Auto-generated nRF52 firmware for {spec.get('device_name', 'Unknown')} */",
            f"/* Platform: Nordic nRF52 */",
            f"/* Generated by Accelerapp v2.0 */",
            "",
            "#include <stdint.h>",
            "#include <stdbool.h>",
            '#include "nrf.h"',
            '#include "nrf_gpio.h"',
            '#include "nrf_delay.h"',
            '#include "boards.h"',
            "",
        ]
        
        # Add BLE includes if needed
        if self._has_ble_peripherals(spec):
            lines.extend([
                '#include "ble.h"',
                '#include "ble_advertising.h"',
                '#include "ble_conn_params.h"',
                "",
            ])
        
        lines.extend([
            "/* Application main function */",
            "int main(void) {",
            "    /* Initialize */",
            "    nrf_gpio_cfg_output(LED_1);",
            "",
        ])

        # Initialize peripherals
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"    /* Initialize {ptype} */")

        lines.extend([
            "",
            "    /* Enter main loop */",
            "    while (1) {",
        ])

        # Main loop logic
        for peripheral in spec.get("peripherals", []):
            ptype = peripheral.get("type")
            lines.append(f"        /* Process {ptype} */")

        lines.extend([
            "        nrf_delay_ms(100);",
            "    }",
            "}",
            "",
        ])

        return "\n".join(lines)

    def _generate_sdk_config(self, spec: Dict[str, Any]) -> str:
        """Generate SDK configuration header."""
        lines = [
            "/* nRF52 SDK Configuration */",
            "#ifndef SDK_CONFIG_H",
            "#define SDK_CONFIG_H",
            "",
            "/* Clock configuration */",
            "#define NRF_SDH_CLOCK_LF_SRC 1",
            "#define NRF_SDH_CLOCK_LF_RC_CTIV 0",
            "#define NRF_SDH_CLOCK_LF_RC_TEMP_CTIV 0",
            "#define NRF_SDH_CLOCK_LF_ACCURACY 7",
            "",
        ]
        
        # BLE configuration
        if self._has_ble_peripherals(spec):
            lines.extend([
                "/* BLE Stack Configuration */",
                "#define NRF_SDH_BLE_ENABLED 1",
                "#define NRF_SDH_BLE_GAP_DATA_LENGTH 251",
                "#define NRF_SDH_BLE_PERIPHERAL_LINK_COUNT 1",
                "#define NRF_SDH_BLE_CENTRAL_LINK_COUNT 0",
                "#define NRF_SDH_BLE_TOTAL_LINK_COUNT 1",
                "",
            ])
        
        lines.extend([
            "#endif /* SDK_CONFIG_H */",
            "",
        ])
        
        return "\n".join(lines)

    def _generate_ble_service(self, spec: Dict[str, Any]) -> str:
        """Generate BLE service implementation."""
        lines = [
            "/* BLE Service Implementation */",
            '#include "ble_service.h"',
            '#include "ble.h"',
            "",
            "/* Service UUID */",
            "#define CUSTOM_SERVICE_UUID 0x1234",
            "",
            "void ble_service_init(void) {",
            "    /* Initialize BLE service */",
            "}",
            "",
            "void ble_service_on_ble_evt(ble_evt_t const * p_ble_evt) {",
            "    /* Handle BLE events */",
            "}",
            "",
        ]
        return "\n".join(lines)

    def _has_ble_peripherals(self, spec: Dict[str, Any]) -> bool:
        """Check if spec includes BLE peripherals."""
        for peripheral in spec.get("peripherals", []):
            if "ble" in peripheral.get("type", "").lower():
                return True
        return False
