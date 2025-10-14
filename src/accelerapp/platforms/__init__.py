"""
Multi-platform support module for Accelerapp.
Provides platform abstraction and specialized implementations.
"""

from .base import BasePlatform
from .arduino import ArduinoPlatform
from .esp32 import ESP32Platform
from .stm32 import STM32Platform
from .micropython import MicroPythonPlatform
from .raspberry_pi_pico import RaspberryPiPicoPlatform
from .raspberry_pi import RaspberryPiPlatform

# Enhanced STM32 platforms
from .stm32.f4_series import STM32F4Platform
from .stm32.h7_series import STM32H7Platform

# Nordic nRF platforms
from .nordic.nrf52 import NRF52Platform
from .nordic.nrf53 import NRF53Platform



__all__ = [
    "BasePlatform",
    "ArduinoPlatform",
    "ESP32Platform",
    "STM32Platform",
    "MicroPythonPlatform",
    "RaspberryPiPicoPlatform",
    "RaspberryPiPlatform",
    "STM32F4Platform",
    "STM32H7Platform",
    "NRF52Platform",
    "NRF53Platform",

    "get_platform",
]


def get_platform(platform_name: str) -> BasePlatform:
    """
    Factory function to get platform instance by name.

    Args:
        platform_name: Name of the platform (arduino, esp32, stm32, micropython, raspberry_pi_pico, raspberry_pi)

    Returns:
        Platform instance

    Raises:
        ValueError: If platform is not supported
    """
    platforms = {
        "arduino": ArduinoPlatform,
        "esp32": ESP32Platform,
        "stm32": STM32Platform,
        "stm32f4": STM32F4Platform,
        "stm32h7": STM32H7Platform,
        "micropython": MicroPythonPlatform,
        "raspberry_pi_pico": RaspberryPiPicoPlatform,
        "raspberry_pi": RaspberryPiPlatform,
        "nrf52": NRF52Platform,
        "nrf52840": NRF52Platform,
        "nrf53": NRF53Platform,
        "nrf5340": NRF53Platform,

    }

    platform_class = platforms.get(platform_name.lower())
    if not platform_class:
        raise ValueError(f"Unsupported platform: {platform_name}")

    return platform_class()
