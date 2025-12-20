"""
Cloud sync service for synchronizing configurations and deployments.
Provides real-time sync capabilities between local and cloud environments.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import json
import hashlib
import threading
import time


class SyncStatus(Enum):
    """Sync operation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncDirection(Enum):
    """Sync direction."""

    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"


class SyncRecord:
    """Represents a sync operation record."""

    def __init__(
        self,
        record_id: str,
        resource_type: str,
        resource_id: str,
        direction: SyncDirection,
        status: SyncStatus = SyncStatus.PENDING,
    ):
        self.record_id = record_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.direction = direction
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error_message: Optional[str] = None
        self.local_hash: Optional[str] = None
        self.remote_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "direction": self.direction.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message,
            "local_hash": self.local_hash,
            "remote_hash": self.remote_hash,
        }


class CloudSyncService:
    """
    Service for synchronizing data between local and cloud environments.
    Supports configuration sync, deployment state sync, and artifact sync.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cloud sync service.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.sync_records: Dict[str, SyncRecord] = {}
        self.sync_handlers: Dict[str, Callable] = {}
        self.conflict_resolvers: Dict[str, Callable] = {}
        self._auto_sync_enabled = False
        self._sync_interval = self.config.get("sync_interval", 60)
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._record_counter = 0
        self._lock = threading.Lock()

    def register_sync_handler(
        self, resource_type: str, handler: Callable[[str, SyncDirection], Dict[str, Any]]
    ) -> None:
        """
        Register a sync handler for a resource type.

        Args:
            resource_type: Type of resource (config, deployment, artifact, etc.)
            handler: Callable that performs the sync operation
        """
        self.sync_handlers[resource_type] = handler

    def register_conflict_resolver(
        self, resource_type: str, resolver: Callable[[Dict, Dict], Dict]
    ) -> None:
        """
        Register a conflict resolver for a resource type.

        Args:
            resource_type: Type of resource
            resolver: Callable that resolves conflicts between local and remote
        """
        self.conflict_resolvers[resource_type] = resolver

    def _generate_record_id(self) -> str:
        """Generate unique record ID."""
        with self._lock:
            self._record_counter += 1
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            return f"sync-{timestamp}-{self._record_counter:06d}"

    def _compute_hash(self, data: Any) -> str:
        """Compute hash of data for change detection."""
        if isinstance(data, bytes):
            content = data
        elif isinstance(data, str):
            content = data.encode("utf-8")
        else:
            content = json.dumps(data, sort_keys=True).encode("utf-8")

        return hashlib.sha256(content).hexdigest()

    def sync_resource(
        self,
        resource_type: str,
        resource_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        data: Optional[Any] = None,
    ) -> SyncRecord:
        """
        Sync a specific resource.

        Args:
            resource_type: Type of resource to sync
            resource_id: Identifier of the resource
            direction: Sync direction
            data: Optional data to sync

        Returns:
            SyncRecord with operation result
        """
        record_id = self._generate_record_id()
        record = SyncRecord(
            record_id=record_id,
            resource_type=resource_type,
            resource_id=resource_id,
            direction=direction,
        )

        # Compute local hash if data provided
        if data is not None:
            record.local_hash = self._compute_hash(data)

        record.status = SyncStatus.IN_PROGRESS
        self.sync_records[record_id] = record

        try:
            if resource_type in self.sync_handlers:
                handler = self.sync_handlers[resource_type]
                result = handler(resource_id, direction)

                if result.get("success"):
                    record.status = SyncStatus.COMPLETED
                    record.remote_hash = result.get("remote_hash")
                elif result.get("conflict"):
                    record.status = SyncStatus.CONFLICT
                    record.error_message = "Conflict detected"

                    # Try to resolve conflict
                    if resource_type in self.conflict_resolvers:
                        resolver = self.conflict_resolvers[resource_type]
                        resolved = resolver(
                            result.get("local_data", {}), result.get("remote_data", {})
                        )
                        if resolved:
                            record.status = SyncStatus.COMPLETED
                            record.error_message = None
                else:
                    record.status = SyncStatus.FAILED
                    record.error_message = result.get("error", "Unknown error")
            else:
                record.status = SyncStatus.FAILED
                record.error_message = f"No handler registered for {resource_type}"

        except Exception as e:
            record.status = SyncStatus.FAILED
            record.error_message = str(e)

        record.updated_at = datetime.utcnow()
        return record

    def sync_configuration(
        self,
        config_id: str,
        config_data: Dict[str, Any],
        direction: SyncDirection = SyncDirection.UPLOAD,
    ) -> SyncRecord:
        """
        Sync a configuration to/from cloud.

        Args:
            config_id: Configuration identifier
            config_data: Configuration data
            direction: Sync direction

        Returns:
            SyncRecord with operation result
        """
        return self.sync_resource("configuration", config_id, direction, config_data)

    def sync_deployment(
        self,
        deployment_id: str,
        deployment_data: Dict[str, Any],
        direction: SyncDirection = SyncDirection.UPLOAD,
    ) -> SyncRecord:
        """
        Sync deployment state to/from cloud.

        Args:
            deployment_id: Deployment identifier
            deployment_data: Deployment state data
            direction: Sync direction

        Returns:
            SyncRecord with operation result
        """
        return self.sync_resource("deployment", deployment_id, direction, deployment_data)

    def sync_artifact(
        self,
        artifact_id: str,
        artifact_data: bytes,
        direction: SyncDirection = SyncDirection.UPLOAD,
    ) -> SyncRecord:
        """
        Sync an artifact to/from cloud.

        Args:
            artifact_id: Artifact identifier
            artifact_data: Artifact binary data
            direction: Sync direction

        Returns:
            SyncRecord with operation result
        """
        return self.sync_resource("artifact", artifact_id, direction, artifact_data)

    def get_sync_status(self, record_id: str) -> Optional[SyncRecord]:
        """
        Get status of a sync operation.

        Args:
            record_id: Sync record ID

        Returns:
            SyncRecord or None
        """
        return self.sync_records.get(record_id)

    def list_sync_records(
        self,
        resource_type: Optional[str] = None,
        status: Optional[SyncStatus] = None,
        limit: int = 100,
    ) -> List[SyncRecord]:
        """
        List sync records with optional filters.

        Args:
            resource_type: Filter by resource type
            status: Filter by status
            limit: Maximum records to return

        Returns:
            List of SyncRecords
        """
        records = list(self.sync_records.values())

        if resource_type:
            records = [r for r in records if r.resource_type == resource_type]

        if status:
            records = [r for r in records if r.status == status]

        # Sort by created_at descending
        records.sort(key=lambda r: r.created_at, reverse=True)

        return records[:limit]

    def get_pending_syncs(self) -> List[SyncRecord]:
        """
        Get all pending sync operations.

        Returns:
            List of pending SyncRecords
        """
        return self.list_sync_records(status=SyncStatus.PENDING)

    def get_failed_syncs(self) -> List[SyncRecord]:
        """
        Get all failed sync operations.

        Returns:
            List of failed SyncRecords
        """
        return self.list_sync_records(status=SyncStatus.FAILED)

    def retry_sync(self, record_id: str) -> Optional[SyncRecord]:
        """
        Retry a failed sync operation.

        Args:
            record_id: ID of the sync record to retry

        Returns:
            New SyncRecord or None if original not found
        """
        original = self.sync_records.get(record_id)
        if not original:
            return None

        return self.sync_resource(
            original.resource_type, original.resource_id, original.direction
        )

    def enable_auto_sync(self, interval: Optional[int] = None) -> None:
        """
        Enable automatic background sync.

        Args:
            interval: Sync interval in seconds (default from config)
        """
        if interval:
            self._sync_interval = interval

        self._auto_sync_enabled = True
        self._stop_event.clear()

        def auto_sync_loop():
            while not self._stop_event.is_set():
                try:
                    # Process pending syncs
                    pending = self.get_pending_syncs()
                    for record in pending:
                        if self._stop_event.is_set():
                            break
                        self.retry_sync(record.record_id)

                except Exception:
                    pass  # Continue on errors

                self._stop_event.wait(self._sync_interval)

        self._sync_thread = threading.Thread(target=auto_sync_loop, daemon=True)
        self._sync_thread.start()

    def disable_auto_sync(self) -> None:
        """Disable automatic background sync."""
        self._auto_sync_enabled = False
        self._stop_event.set()

        if self._sync_thread:
            self._sync_thread.join(timeout=5.0)
            self._sync_thread = None

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get sync service status.

        Returns:
            Service status dictionary
        """
        records = list(self.sync_records.values())

        return {
            "auto_sync_enabled": self._auto_sync_enabled,
            "sync_interval": self._sync_interval,
            "registered_handlers": list(self.sync_handlers.keys()),
            "total_records": len(records),
            "pending_count": len([r for r in records if r.status == SyncStatus.PENDING]),
            "in_progress_count": len([r for r in records if r.status == SyncStatus.IN_PROGRESS]),
            "completed_count": len([r for r in records if r.status == SyncStatus.COMPLETED]),
            "failed_count": len([r for r in records if r.status == SyncStatus.FAILED]),
            "conflict_count": len([r for r in records if r.status == SyncStatus.CONFLICT]),
        }

    def clear_completed_records(self, older_than_hours: int = 24) -> int:
        """
        Clear completed sync records older than specified hours.

        Args:
            older_than_hours: Age threshold in hours

        Returns:
            Number of records cleared
        """
        cutoff = datetime.utcnow()
        from datetime import timedelta

        cutoff = cutoff - timedelta(hours=older_than_hours)

        to_remove = []
        for record_id, record in self.sync_records.items():
            if record.status == SyncStatus.COMPLETED and record.updated_at < cutoff:
                to_remove.append(record_id)

        for record_id in to_remove:
            del self.sync_records[record_id]

        return len(to_remove)
