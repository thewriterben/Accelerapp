"""
STM32 platform module with comprehensive series support.
Supports STM32F4, F7, H7, L4 series with HAL integration.
"""

from typing import Dict, Any

from .base import STM32BasePlatform
from .f4_series import STM32F4Platform
from .h7_series import STM32H7Platform
from .hal_generator import STM32HALGenerator
from .cubemx_integration import CubeMXIntegration


class STM32Platform(STM32BasePlatform):
    """
    Generic STM32 platform implementation for backward compatibility.
    Use STM32F4Platform or STM32H7Platform for series-specific features.
    """

    def __init__(self):
        """Initialize generic STM32 platform."""
        super().__init__()
        self.name = "stm32"

    def get_series_info(self) -> Dict[str, Any]:
        """Get generic STM32 series information."""
        return {
            "series": "STM32",
            "core": "ARM Cortex-M",
            "description": "Generic STM32 platform",
            "supported_series": ["F4", "F7", "H7", "L4", "G0", "G4"],
        }


__all__ = [
    "STM32BasePlatform",
    "STM32Platform",
    "STM32F4Platform",
    "STM32H7Platform",
    "STM32HALGenerator",
    "CubeMXIntegration",
]
