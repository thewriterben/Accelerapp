"""
Nordic nRF53 series platform implementation.
Dual-core Cortex-M33 with enhanced security and performance.
"""

from typing import Dict, Any
from .nrf52 import NRF52Platform


class NRF53Platform(NRF52Platform):
    """
    Nordic nRF53 series platform implementation.
    Dual-core ARM Cortex-M33 with TrustZone and enhanced BLE.
    """

    def __init__(self):
        """Initialize nRF53 platform."""
        super().__init__()
        self.name = "nrf53"
        
        # nRF53-specific capabilities
        self.capabilities.extend([
            "dual_core",  # Application and Network cores
            "trustzone",  # ARM TrustZone
            "bluetooth_le_audio",  # LE Audio support
            "802_15_4",  # IEEE 802.15.4
            "qspi",  # Quad SPI
        ])
        
    def get_platform_info(self) -> Dict[str, Any]:
        """Get nRF53 platform information."""
        base_info = super().get_platform_info()
        
        # Override with nRF53-specific info
        base_info.update({
            "name": self.name,
            "display_name": "Nordic nRF53",
            "variants": ["nRF5340"],
            "core": "Dual ARM Cortex-M33 (App + Net)",
            "max_clock_app": 128,  # MHz for Application core
            "max_clock_net": 64,   # MHz for Network core
            "flash_range": "1MB",
            "ram_range": "512KB (App) + 64KB (Net)",
            "wireless": {
                "ble": "Bluetooth 5.3 with LE Audio",
                "protocols": ["BLE", "Thread", "Zigbee", "Matter"],
                "tx_power": "+8 dBm",
                "rx_sensitivity": "-97 dBm",
                "concurrent": "BLE + Thread/Zigbee simultaneous operation",
            },
            "security": [
                "ARM TrustZone",
                "Secure Boot",
                "Hardware root of trust",
                "ARM CryptoCell-312",
            ],
            "key_features": [
                "Dual Cortex-M33 cores with TrustZone",
                "Bluetooth 5.3 with LE Audio and Direction Finding",
                "Concurrent BLE and 802.15.4 operation",
                "Advanced security with TrustZone",
                "1MB Flash, 512KB RAM",
                "Ultra-low power consumption",
            ],
        })
        
        return base_info
    
    def get_build_config(self) -> Dict[str, Any]:
        """Get nRF53 build configuration."""
        config = super().get_build_config()
        config.update({
            "board": "nrf5340dk_nrf5340_cpuapp",
            "cores": ["app", "net"],
            "softdevice": "s340",
            "trustzone": "enabled",
        })
        return config
