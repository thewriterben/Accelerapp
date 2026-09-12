"""
Template marketplace for sharing and discovering code templates.
"""

from .registry import TemplateRegistry
from .search import TemplateSearch
from .template import TemplateMetadata, TemplatePackage

__all__ = [
    "TemplateRegistry",
    "TemplateMetadata",
    "TemplatePackage",
    "TemplateSearch",
]
