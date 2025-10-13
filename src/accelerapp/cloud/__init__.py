"""
Cloud-based generation service foundation.
Provides infrastructure for remote code generation and distributed processing.
"""

from .service import CloudGenerationService
from .api import CloudAPIHandler
from .auth import AuthenticationManager
from .queue import JobQueue

__all__ = [
    'CloudGenerationService',
    'CloudAPIHandler', 
    'AuthenticationManager',
    'JobQueue',
]
