"""
Hardware design module for enclosure generation and 3D design.
Integrates WildCAM_ESP32 production-ready hardware expertise.
"""

from .board_support import BoardSupportMatrix, ESP32BoardType
from .generator import EnclosureDesign, EnclosureGenerator

__all__ = [
    "EnclosureGenerator",
    "EnclosureDesign",
    "BoardSupportMatrix",
    "ESP32BoardType",
]
