"""
AI Model Version Management System.
Handles model lifecycle, versioning, and rollback capabilities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ModelVersion:
    """Represents a specific version of an AI model."""
    
    name: str
    version: str
    created_at: str
    status: str  # active, deprecated, archived
    performance_metrics: Dict[str, float]
    metadata: Dict[str, Any]
    rollback_supported: bool = True


class AIModelVersionManager:
    """
    Manages AI model versions with rollback capabilities.
    Tracks model lifecycle, performance, and deployment status.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize model version manager.
        
        Args:
            storage_path: Path to store model version metadata
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "ai_models"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "versions.json"
        self.versions: Dict[str, List[ModelVersion]] = {}
        self.active_versions: Dict[str, str] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load model version metadata from storage."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.versions = {
                        name: [ModelVersion(**v) for v in versions]
                        for name, versions in data.get("versions", {}).items()
                    }
                    self.active_versions = data.get("active_versions", {})
            except Exception:
                self.versions = {}
                self.active_versions = {}
    
    def _save_metadata(self) -> None:
        """Save model version metadata to storage."""
        data = {
            "versions": {
                name: [asdict(v) for v in versions]
                for name, versions in self.versions.items()
            },
            "active_versions": self.active_versions
        }
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def register_version(
        self,
        name: str,
        version: str,
        performance_metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            name: Model name
            version: Version identifier
            performance_metrics: Performance metrics for this version
            metadata: Additional metadata
            
        Returns:
            Created ModelVersion instance
        """
        model_version = ModelVersion(
            name=name,
            version=version,
            created_at=datetime.utcnow().isoformat(),
            status="active",
            performance_metrics=performance_metrics or {},
            metadata=metadata or {},
            rollback_supported=True
        )
        
        if name not in self.versions:
            self.versions[name] = []
        
        self.versions[name].append(model_version)
        
        # Set as active if it's the first version
        if name not in self.active_versions:
            self.active_versions[name] = version
        
        self._save_metadata()
        return model_version
    
    def set_active_version(self, name: str, version: str) -> bool:
        """
        Set a specific version as active.
        
        Args:
            name: Model name
            version: Version to activate
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.versions:
            return False
        
        version_exists = any(v.version == version for v in self.versions[name])
        if not version_exists:
            return False
        
        self.active_versions[name] = version
        self._save_metadata()
        return True
    
    def get_active_version(self, name: str) -> Optional[ModelVersion]:
        """
        Get the active version of a model.
        
        Args:
            name: Model name
            
        Returns:
            Active ModelVersion or None
        """
        if name not in self.active_versions:
            return None
        
        active_version = self.active_versions[name]
        versions = self.versions.get(name, [])
        
        for version in versions:
            if version.version == active_version:
                return version
        
        return None
    
    def rollback(self, name: str, target_version: Optional[str] = None) -> bool:
        """
        Rollback to a previous version.
        
        Args:
            name: Model name
            target_version: Target version (if None, rollback to previous)
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.versions or len(self.versions[name]) < 2:
            return False
        
        if target_version:
            return self.set_active_version(name, target_version)
        
        # Find previous version
        versions = sorted(
            self.versions[name],
            key=lambda v: v.created_at,
            reverse=True
        )
        
        current_active = self.active_versions.get(name)
        for i, version in enumerate(versions):
            if version.version == current_active and i + 1 < len(versions):
                return self.set_active_version(name, versions[i + 1].version)
        
        return False
    
    def list_versions(self, name: str) -> List[ModelVersion]:
        """
        List all versions of a model.
        
        Args:
            name: Model name
            
        Returns:
            List of ModelVersion instances
        """
        return self.versions.get(name, [])
    
    def update_performance_metrics(
        self,
        name: str,
        version: str,
        metrics: Dict[str, float]
    ) -> bool:
        """
        Update performance metrics for a version.
        
        Args:
            name: Model name
            version: Version identifier
            metrics: Performance metrics to update
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.versions:
            return False
        
        for model_version in self.versions[name]:
            if model_version.version == version:
                model_version.performance_metrics.update(metrics)
                self._save_metadata()
                return True
        
        return False
    
    def deprecate_version(self, name: str, version: str) -> bool:
        """
        Mark a version as deprecated.
        
        Args:
            name: Model name
            version: Version to deprecate
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.versions:
            return False
        
        for model_version in self.versions[name]:
            if model_version.version == version:
                model_version.status = "deprecated"
                self._save_metadata()
                return True
        
        return False
    
    def get_version_stats(self) -> Dict[str, Any]:
        """
        Get statistics about managed model versions.
        
        Returns:
            Dictionary with version statistics
        """
        total_models = len(self.versions)
        total_versions = sum(len(versions) for versions in self.versions.values())
        
        status_counts = {"active": 0, "deprecated": 0, "archived": 0}
        for versions in self.versions.values():
            for version in versions:
                status_counts[version.status] = status_counts.get(version.status, 0) + 1
        
        return {
            "total_models": total_models,
            "total_versions": total_versions,
            "active_models": len(self.active_versions),
            "status_distribution": status_counts,
            "storage_path": str(self.storage_path)
        }
