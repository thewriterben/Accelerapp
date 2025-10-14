"""
STM32H7 series platform implementation.
Supports high-performance STM32H7xx microcontrollers.
"""

from typing import Dict, Any
from .base import STM32BasePlatform


class STM32H7Platform(STM32BasePlatform):
    """
    STM32H7 series platform implementation.
    Optimized for high-performance applications with Cortex-M7 core.
    """

    def __init__(self):
        """Initialize STM32H7 platform."""
        super().__init__()
        self.name = "stm32h7"
        self.series = "H7"
        
        # H7-specific capabilities
        self.capabilities.extend([
            "fpu_dp",  # Double-precision FPU
            "dsp",
            "cache",  # I-Cache and D-Cache
            "mpu",  # Memory Protection Unit
            "art_accelerator",
            "dual_core",  # Some variants have dual-core
            "high_speed_external_memory",
            "jpeg_codec",
            "chrom_art",  # Graphics accelerator
        ])
        
    def get_series_info(self) -> Dict[str, Any]:
        """Get STM32H7 series-specific information."""
        return {
            "series": "STM32H7",
            "core": "ARM Cortex-M7",
            "max_clock": 480,  # MHz for H7A3/H7B0/H7B3
            "typical_clock": 400,  # MHz for H743/H753
            "fpu": "FPU-DP (Double Precision)",
            "flash_range": "512KB - 2MB",
            "ram_range": "128KB - 1MB",
            "voltage_range": "1.62V - 3.6V",
            "package_types": ["LQFP100", "LQFP144", "LQFP176", "BGA240", "TFBGA240"],
            "common_variants": [
                "STM32H743",
                "STM32H753",
                "STM32H750",
                "STM32H7A3",
                "STM32H7B0",
            ],
            "key_features": [
                "Ultra-high performance Cortex-M7 core",
                "Up to 480 MHz operation",
                "Double-precision FPU",
                "L1 cache (16KB I-cache + 16KB D-cache)",
                "Dual Quad-SPI with XIP",
                "Hardware JPEG codec",
                "Chrom-ART graphics accelerator",
                "High-resolution timer (184 ps)",
                "Up to 3 ADCs with 3.6 MSPS",
            ],
        }
    
    def get_build_config(self) -> Dict[str, Any]:
        """Get STM32H7-specific build configuration."""
        base_config = super().get_build_config()
        base_config.update({
            "board": "nucleo_h743zi",
            "mcu": "STM32H743ZITx",
            "cpu_flags": [
                "-mcpu=cortex-m7",
                "-mthumb",
                "-mfpu=fpv5-d16",
                "-mfloat-abi=hard",
            ],
            "linker_script": "STM32H743ZITx_FLASH.ld",
            "hal_driver": "STM32H7xx_HAL_Driver",
            "optimization": "-O3",  # Higher optimization for H7
            "cache_config": {
                "icache": "enabled",
                "dcache": "enabled",
            },
        })
        return base_config
