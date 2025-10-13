"""
Template marketplace for sharing and discovering code templates.
"""

from .registry import TemplateRegistry
from .template import TemplateMetadata, TemplatePackage
from .search import TemplateSearch

__all__ = [
    'TemplateRegistry',
    'TemplateMetadata',
    'TemplatePackage',
    'TemplateSearch',
]
