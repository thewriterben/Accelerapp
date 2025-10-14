"""
STM32 platform module with comprehensive series support.
Supports STM32F4, F7, H7, L4 series with HAL integration.
"""

from .base import STM32BasePlatform
from .f4_series import STM32F4Platform
from .h7_series import STM32H7Platform
from .hal_generator import STM32HALGenerator
from .cubemx_integration import CubeMXIntegration

# Backward compatibility: alias F4 as the default STM32Platform
STM32Platform = STM32F4Platform

__all__ = [
    "STM32BasePlatform",
    "STM32Platform",  # For backward compatibility
    "STM32F4Platform",
    "STM32H7Platform",
    "STM32HALGenerator",
    "CubeMXIntegration",
]
