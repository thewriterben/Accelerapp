"""
FreeRTOS integration module.
Provides task generation, configuration, and IPC primitives.
"""

from .task_generator import FreeRTOSTaskGenerator
from .config_generator import FreeRTOSConfigGenerator
from .ipc_primitives import IPCPrimitives

__all__ = [
    "FreeRTOSTaskGenerator",
    "FreeRTOSConfigGenerator",
    "IPCPrimitives",
]
