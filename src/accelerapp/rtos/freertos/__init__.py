"""
FreeRTOS integration module.
Provides task generation, configuration, and IPC primitives.
"""

from .config_generator import FreeRTOSConfigGenerator
from .ipc_primitives import IPCPrimitives
from .task_generator import FreeRTOSTaskGenerator

__all__ = [
    "FreeRTOSTaskGenerator",
    "FreeRTOSConfigGenerator",
    "IPCPrimitives",
]
