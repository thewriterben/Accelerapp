"""
Community integration for CYD ecosystem.

Provides integration with popular CYD projects and templates
from the witnessmenow/ESP32-Cheap-Yellow-Display community.
"""

from .examples import Example, ExampleCategory, ExampleLoader
from .integrations import CommunityIntegration, ProjectInfo, ProjectType
from .templates import Template, TemplateManager, TemplateType

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
