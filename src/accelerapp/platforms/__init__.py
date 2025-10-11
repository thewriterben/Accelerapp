"""
Multi-platform support module for Accelerapp.
Provides platform abstraction and specialized implementations.
"""

from .base import BasePlatform
from .arduino import ArduinoPlatform
from .esp32 import ESP32Platform
from .stm32 import STM32Platform
from .micropython import MicroPythonPlatform

__all__ = [
    'BasePlatform',
    'ArduinoPlatform',
    'ESP32Platform',
    'STM32Platform',
    'MicroPythonPlatform',
    'get_platform',
]


def get_platform(platform_name: str) -> BasePlatform:
    """
    Factory function to get platform instance by name.
    
    Args:
        platform_name: Name of the platform (arduino, esp32, stm32, micropython)
        
    Returns:
        Platform instance
        
    Raises:
        ValueError: If platform is not supported
    """
    platforms = {
        'arduino': ArduinoPlatform,
        'esp32': ESP32Platform,
        'stm32': STM32Platform,
        'micropython': MicroPythonPlatform,
    }
    
    platform_class = platforms.get(platform_name.lower())
    if not platform_class:
        raise ValueError(f"Unsupported platform: {platform_name}")
    
    return platform_class()
