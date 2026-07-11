"""
Firmware generation module.
Generates embedded firmware for hardware control.
"""

from .generator import FirmwareGenerator
from .obc_templates import (
    FirmwareTemplate,
    TemplatesSchemaError,
    codegen_route,
    load_templates,
    template_for_board,
)

__all__ = [
    "FirmwareGenerator",
    "FirmwareTemplate",
    "TemplatesSchemaError",
    "codegen_route",
    "load_templates",
    "template_for_board",
]
