"""
Offline template and knowledge management module.
Provides local knowledge base, template management, and pattern learning.
"""

from .knowledge_base import KnowledgeBase, KnowledgeEntry
from .template_manager import TemplateManager, Template, TemplateCategory
from .pattern_analyzer import PatternAnalyzer, CodePattern
from .offline_docs import OfflineDocumentation, DocEntry

__all__ = [
    "KnowledgeBase",
    "KnowledgeEntry",
    "TemplateManager",
    "Template",
    "TemplateCategory",
    "PatternAnalyzer",
    "CodePattern",
    "OfflineDocumentation",
    "DocEntry",
]
