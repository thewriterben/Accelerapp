"""
Hardware-in-the-Loop (HIL) testing framework.
"""

from .framework import HILTestFramework, TestCase, TestResult
from .hardware import HardwareInterface, DeviceAdapter
from .runner import TestRunner

__all__ = [
    'HILTestFramework',
    'TestCase',
    'TestResult',
    'HardwareInterface',
    'DeviceAdapter',
    'TestRunner',
]
