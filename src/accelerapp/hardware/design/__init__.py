"""
Hardware design module for enclosure generation and 3D design.
Integrates WildCAM_ESP32 production-ready hardware expertise.
"""

from .generator import EnclosureGenerator, EnclosureDesign
from .board_support import BoardSupportMatrix, ESP32BoardType

__all__ = [
    "EnclosureGenerator",
    "EnclosureDesign",
    "BoardSupportMatrix",
    "ESP32BoardType",
]
