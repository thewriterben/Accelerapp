"""
Community integration for CYD ecosystem.

Provides integration with popular CYD projects and templates
from the witnessmenow/ESP32-Cheap-Yellow-Display community.
"""

from .integrations import CommunityIntegration, ProjectType, ProjectInfo
from .templates import TemplateManager, TemplateType, Template
from .examples import ExampleLoader, ExampleCategory, Example

__all__ = [
    "CommunityIntegration",
    "TemplateManager",
    "ExampleLoader",
    "ProjectType",
    "ProjectInfo",
    "TemplateType",
    "Template",
    "ExampleCategory",
    "Example",
]
