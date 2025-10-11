"""
Hardware abstraction layer module for Accelerapp.
Provides unified hardware component interfaces and conflict detection.
"""

from .abstraction import HardwareAbstractionLayer, HardwareComponent, ComponentFactory

__all__ = [
    'HardwareAbstractionLayer',
    'HardwareComponent',
    'ComponentFactory',
]
