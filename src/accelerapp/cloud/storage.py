"""
Cloud storage service for managing generated code artifacts.
Supports multiple cloud storage providers (S3, Azure Blob, GCS).
"""

from typing import Dict, Any, Optional, List, BinaryIO
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import os
import json
import hashlib
from pathlib import Path


class CloudStorageProvider(Enum):
    """Supported cloud storage providers."""

    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    LOCAL = "local"  # For testing and air-gapped environments


class StorageObject:
    """Represents an object in cloud storage."""

    def __init__(
        self,
        key: str,
        size: int,
        content_type: str,
        last_modified: datetime,
        etag: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        self.key = key
        self.size = size
        self.content_type = content_type
        self.last_modified = last_modified
        self.etag = etag
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "size": self.size,
            "content_type": self.content_type,
            "last_modified": self.last_modified.isoformat(),
            "etag": self.etag,
            "metadata": self.metadata,
        }


class CloudStorageBackend(ABC):
    """Abstract base class for cloud storage backends."""

    @abstractmethod
    def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Upload data to storage."""
        pass

    @abstractmethod
    def download(self, key: str) -> Optional[bytes]:
        """Download data from storage."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete object from storage."""
        pass

    @abstractmethod
    def list_objects(self, prefix: str = "") -> List[StorageObject]:
        """List objects in storage."""
        pass

    @abstractmethod
    def get_object_info(self, key: str) -> Optional[StorageObject]:
        """Get object metadata."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if object exists."""
        pass


class LocalStorageBackend(CloudStorageBackend):
    """
    Local filesystem storage backend.
    Used for testing and air-gapped environments.
    """

    def __init__(self, base_path: str):
        """
        Initialize local storage backend.

        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_path / ".metadata.json"
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._load_metadata()

    def _load_metadata(self):
        """Load metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                self._metadata = json.load(f)

    def _save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self._metadata, f, indent=2, default=str)

    def _get_full_path(self, key: str) -> Path:
        """Get full filesystem path for key."""
        return self.base_path / key

    def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Upload data to local storage."""
        try:
            full_path = self._get_full_path(key)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "wb") as f:
                f.write(data)

            # Calculate etag (MD5 hash)
            etag = hashlib.md5(data).hexdigest()

            self._metadata[key] = {
                "content_type": content_type,
                "size": len(data),
                "etag": etag,
                "last_modified": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
            self._save_metadata()

            return True
        except Exception:
            return False

    def download(self, key: str) -> Optional[bytes]:
        """Download data from local storage."""
        try:
            full_path = self._get_full_path(key)
            if full_path.exists():
                with open(full_path, "rb") as f:
                    return f.read()
            return None
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        """Delete object from local storage."""
        try:
            full_path = self._get_full_path(key)
            if full_path.exists():
                full_path.unlink()

            if key in self._metadata:
                del self._metadata[key]
                self._save_metadata()

            return True
        except Exception:
            return False

    def list_objects(self, prefix: str = "") -> List[StorageObject]:
        """List objects in local storage."""
        objects = []

        for key, meta in self._metadata.items():
            if key.startswith(prefix):
                objects.append(
                    StorageObject(
                        key=key,
                        size=meta.get("size", 0),
                        content_type=meta.get("content_type", "application/octet-stream"),
                        last_modified=datetime.fromisoformat(meta.get("last_modified", "")),
                        etag=meta.get("etag"),
                        metadata=meta.get("metadata", {}),
                    )
                )

        return objects

    def get_object_info(self, key: str) -> Optional[StorageObject]:
        """Get object metadata from local storage."""
        if key in self._metadata:
            meta = self._metadata[key]
            return StorageObject(
                key=key,
                size=meta.get("size", 0),
                content_type=meta.get("content_type", "application/octet-stream"),
                last_modified=datetime.fromisoformat(meta.get("last_modified", "")),
                etag=meta.get("etag"),
                metadata=meta.get("metadata", {}),
            )
        return None

    def exists(self, key: str) -> bool:
        """Check if object exists in local storage."""
        return key in self._metadata and self._get_full_path(key).exists()


class CloudStorageService:
    """
    Main cloud storage service for managing generated code artifacts.
    Supports multiple providers with automatic failover.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cloud storage service.

        Args:
            config: Configuration dictionary with storage settings
        """
        self.config = config or {}
        self.backends: Dict[str, CloudStorageBackend] = {}
        self.active_provider: Optional[str] = None
        self.bucket_name = self.config.get("bucket_name", "accelerapp-artifacts")

    def register_backend(
        self, provider: CloudStorageProvider, backend: CloudStorageBackend
    ) -> None:
        """
        Register a storage backend.

        Args:
            provider: Provider type
            backend: Backend instance
        """
        self.backends[provider.value] = backend

        if not self.active_provider:
            self.active_provider = provider.value

    def set_active_provider(self, provider: CloudStorageProvider) -> None:
        """
        Set the active storage provider.

        Args:
            provider: Provider to activate
        """
        if provider.value in self.backends:
            self.active_provider = provider.value
        else:
            raise ValueError(f"Provider {provider.value} not registered")

    def _get_backend(self) -> CloudStorageBackend:
        """Get the active storage backend."""
        if not self.active_provider or self.active_provider not in self.backends:
            raise RuntimeError("No storage backend available")
        return self.backends[self.active_provider]

    def upload_artifact(
        self,
        artifact_id: str,
        data: bytes,
        artifact_type: str = "generated_code",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Upload a code artifact to cloud storage.

        Args:
            artifact_id: Unique artifact identifier
            data: Artifact content
            artifact_type: Type of artifact (firmware, sdk, ui, etc.)
            metadata: Additional metadata

        Returns:
            Upload result with artifact info
        """
        backend = self._get_backend()

        key = f"{artifact_type}/{artifact_id}"

        # Determine content type
        content_types = {
            "firmware": "application/octet-stream",
            "sdk": "application/zip",
            "ui": "application/zip",
            "generated_code": "text/plain",
            "config": "application/yaml",
        }
        content_type = content_types.get(artifact_type, "application/octet-stream")

        # Add standard metadata
        full_metadata = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "uploaded_at": datetime.utcnow().isoformat(),
            "provider": self.active_provider or "",
        }
        if metadata:
            full_metadata.update(metadata)

        success = backend.upload(key, data, content_type, full_metadata)

        return {
            "success": success,
            "key": key,
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "size": len(data),
            "provider": self.active_provider,
        }

    def download_artifact(self, artifact_id: str, artifact_type: str = "generated_code") -> Optional[bytes]:
        """
        Download an artifact from cloud storage.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            Artifact content or None if not found
        """
        backend = self._get_backend()
        key = f"{artifact_type}/{artifact_id}"
        return backend.download(key)

    def delete_artifact(self, artifact_id: str, artifact_type: str = "generated_code") -> bool:
        """
        Delete an artifact from cloud storage.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            True if deleted successfully
        """
        backend = self._get_backend()
        key = f"{artifact_type}/{artifact_id}"
        return backend.delete(key)

    def list_artifacts(
        self, artifact_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List artifacts in cloud storage.

        Args:
            artifact_type: Optional type filter
            limit: Maximum number of results

        Returns:
            List of artifact information
        """
        backend = self._get_backend()

        prefix = f"{artifact_type}/" if artifact_type else ""
        objects = backend.list_objects(prefix)

        return [obj.to_dict() for obj in objects[:limit]]

    def get_artifact_info(self, artifact_id: str, artifact_type: str = "generated_code") -> Optional[Dict[str, Any]]:
        """
        Get artifact metadata.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            Artifact metadata or None
        """
        backend = self._get_backend()
        key = f"{artifact_type}/{artifact_id}"
        obj = backend.get_object_info(key)
        return obj.to_dict() if obj else None

    def artifact_exists(self, artifact_id: str, artifact_type: str = "generated_code") -> bool:
        """
        Check if an artifact exists.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            True if artifact exists
        """
        backend = self._get_backend()
        key = f"{artifact_type}/{artifact_id}"
        return backend.exists(key)

    def sync_artifacts(
        self,
        local_path: str,
        artifact_type: str = "generated_code",
        direction: str = "upload",
    ) -> Dict[str, Any]:
        """
        Sync artifacts between local storage and cloud.

        Args:
            local_path: Local directory path
            artifact_type: Type of artifacts to sync
            direction: 'upload' or 'download'

        Returns:
            Sync result summary
        """
        local_dir = Path(local_path)
        results = {"synced": [], "failed": [], "skipped": []}

        if direction == "upload":
            if not local_dir.exists():
                return {"error": "Local path does not exist", **results}

            for file_path in local_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        artifact_id = str(file_path.relative_to(local_dir))
                        with open(file_path, "rb") as f:
                            data = f.read()

                        result = self.upload_artifact(artifact_id, data, artifact_type)
                        if result["success"]:
                            results["synced"].append(artifact_id)
                        else:
                            results["failed"].append(artifact_id)
                    except Exception as e:
                        results["failed"].append(str(file_path))

        elif direction == "download":
            local_dir.mkdir(parents=True, exist_ok=True)
            artifacts = self.list_artifacts(artifact_type)

            for artifact in artifacts:
                try:
                    artifact_id = artifact["key"].split("/", 1)[-1] if "/" in artifact["key"] else artifact["key"]
                    data = self.download_artifact(artifact_id, artifact_type)

                    if data:
                        output_path = local_dir / artifact_id
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(data)
                        results["synced"].append(artifact_id)
                    else:
                        results["failed"].append(artifact_id)
                except Exception:
                    results["failed"].append(artifact.get("key", "unknown"))

        return {
            "direction": direction,
            "artifact_type": artifact_type,
            **results,
            "total_synced": len(results["synced"]),
            "total_failed": len(results["failed"]),
        }

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get cloud storage service status.

        Returns:
            Service status dictionary
        """
        return {
            "active_provider": self.active_provider,
            "bucket_name": self.bucket_name,
            "registered_backends": list(self.backends.keys()),
            "available": self.active_provider is not None,
        }
