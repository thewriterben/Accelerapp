"""
Advanced peripheral abstraction layer.
Provides comprehensive peripheral support with conflict resolution.
"""

from .conflict_resolver import PeripheralConflictResolver
from .resource_manager import PeripheralResourceManager

__all__ = [
    "PeripheralConflictResolver",
    "PeripheralResourceManager",
]
