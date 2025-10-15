"""
Community integration for CYD ecosystem.

Provides integration with popular CYD projects and templates
from the witnessmenow/ESP32-Cheap-Yellow-Display community.
"""

from .integrations import CommunityIntegration
from .templates import TemplateManager
from .examples import ExampleLoader

__all__ = [
    "CommunityIntegration",
    "TemplateManager",
    "ExampleLoader",
]
