"""
Cloud-based generation service and storage.
Provides infrastructure for remote code generation, distributed processing,
cloud storage for artifacts, and sync capabilities.
"""

from .api import CloudAPIHandler
from .auth import AuthenticationManager
from .queue import JobQueue
from .service import CloudGenerationService
from .storage import (
    CloudStorageBackend,
    CloudStorageProvider,
    CloudStorageService,
    LocalStorageBackend,
    StorageObject,
)
from .sync import (
    CloudSyncService,
    SyncDirection,
    SyncRecord,
    SyncStatus,
)

__all__ = [
    # Core services
    "CloudGenerationService",
    "CloudAPIHandler",
    "AuthenticationManager",
    "JobQueue",
    # Storage
    "CloudStorageService",
    "CloudStorageProvider",
    "CloudStorageBackend",
    "LocalStorageBackend",
    "StorageObject",
    # Sync
    "CloudSyncService",
    "SyncStatus",
    "SyncDirection",
    "SyncRecord",
]
