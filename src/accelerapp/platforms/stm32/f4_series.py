"""
STM32F4 series platform implementation.
Supports STM32F401, F407, F411, F429 and other F4 variants.
"""

from typing import Dict, Any
from .base import STM32BasePlatform


class STM32F4Platform(STM32BasePlatform):
    """
    STM32F4 series platform implementation.
    Optimized for STM32F4xx microcontrollers with Cortex-M4 core.
    """

    def __init__(self):
        """Initialize STM32F4 platform."""
        super().__init__()
        self.name = "stm32f4"
        self.series = "F4"
        
        # F4-specific capabilities
        self.capabilities.extend([
            "fpu",  # Hardware floating-point unit
            "dsp",  # DSP instructions
            "camera_interface",
            "sdio",
            "rng",  # Random number generator
        ])
        
    def get_series_info(self) -> Dict[str, Any]:
        """Get STM32F4 series-specific information."""
        return {
            "series": "STM32F4",
            "core": "ARM Cortex-M4",
            "max_clock": 180,  # MHz for F429/F439
            "typical_clock": 84,  # MHz for F401
            "fpu": "FPU-SP (Single Precision)",
            "flash_range": "256KB - 2MB",
            "ram_range": "64KB - 384KB",
            "voltage_range": "1.8V - 3.6V",
            "package_types": ["LQFP64", "LQFP100", "LQFP144", "LQFP176", "BGA176"],
            "common_variants": [
                "STM32F401",
                "STM32F407",
                "STM32F411",
                "STM32F429",
                "STM32F446",
            ],
            "key_features": [
                "High-performance Cortex-M4 with FPU",
                "DSP instructions",
                "Up to 180 MHz operation",
                "USB OTG FS/HS",
                "Ethernet MAC (select variants)",
                "Camera interface",
                "Hardware crypto (select variants)",
            ],
        }
    
    def get_build_config(self) -> Dict[str, Any]:
        """Get STM32F4-specific build configuration."""
        base_config = super().get_build_config()
        base_config.update({
            "board": "nucleo_f401re",
            "mcu": "STM32F401RETx",
            "cpu_flags": [
                "-mcpu=cortex-m4",
                "-mthumb",
                "-mfpu=fpv4-sp-d16",
                "-mfloat-abi=hard",
            ],
            "linker_script": "STM32F401RETx_FLASH.ld",
            "hal_driver": "STM32F4xx_HAL_Driver",
        })
        return base_config
