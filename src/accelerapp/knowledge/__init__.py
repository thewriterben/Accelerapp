"""
Offline template and knowledge management module.
Provides local knowledge base, template management, and pattern learning.
"""

from .knowledge_base import KnowledgeBase, KnowledgeEntry
from .offline_docs import DocEntry, OfflineDocumentation
from .pattern_analyzer import CodePattern, PatternAnalyzer
from .template_manager import Template, TemplateCategory, TemplateManager

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
