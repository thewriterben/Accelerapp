"""
Plugin system for Accelerapp.
Provides plugin infrastructure for extensibility.
"""

from .base import BasePlugin, PluginMetadata
from .registry import PluginRegistry

__all__ = [
    "BasePlugin",
    "PluginMetadata",
    "PluginRegistry",
]
