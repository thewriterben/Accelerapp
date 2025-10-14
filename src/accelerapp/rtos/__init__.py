"""
Real-Time Operating System (RTOS) support module.
Provides FreeRTOS, Zephyr, and ThreadX integration.
"""

from .freertos.task_generator import FreeRTOSTaskGenerator
from .freertos.config_generator import FreeRTOSConfigGenerator
from .freertos.ipc_primitives import IPCPrimitives

__all__ = [
    "FreeRTOSTaskGenerator",
    "FreeRTOSConfigGenerator",
    "IPCPrimitives",
]
