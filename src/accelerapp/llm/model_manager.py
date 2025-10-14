"""
Model management system for local LLM models.
Handles model downloading, versioning, and lifecycle.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime


class ModelInfo:
    """Information about a local LLM model."""

    def __init__(
        self,
        name: str,
        backend: str,
        size: Optional[int] = None,
        downloaded_at: Optional[str] = None,
        version: Optional[str] = None,
    ):
        """
        Initialize model information.

        Args:
            name: Model identifier
            backend: Backend type (ollama, localai, etc.)
            size: Model size in bytes
            downloaded_at: ISO timestamp of download
            version: Model version string
        """
        self.name = name
        self.backend = backend
        self.size = size
        self.downloaded_at = downloaded_at or datetime.now().isoformat()
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "backend": self.backend,
            "size": self.size,
            "downloaded_at": self.downloaded_at,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Create ModelInfo from dictionary."""
        return cls(**data)


class ModelManager:
    """
    Manages local LLM models across different backends.
    Provides model downloading, caching, and lifecycle management.
    """

    def __init__(self, cache_dir: Optional[Path] = None, metadata_file: Optional[Path] = None):
        """
        Initialize model manager.

        Args:
            cache_dir: Directory for model cache
            metadata_file: Path to metadata JSON file
        """
        self.cache_dir = cache_dir or Path.home() / ".accelerapp" / "models"
        self.metadata_file = metadata_file or (self.cache_dir / "metadata.json")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, ModelInfo] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load model metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.models = {name: ModelInfo.from_dict(info) for name, info in data.items()}
            except Exception:
                # If metadata is corrupted, start fresh
                self.models = {}

    def _save_metadata(self) -> None:
        """Save model metadata to file."""
        try:
            with open(self.metadata_file, "w") as f:
                data = {name: info.to_dict() for name, info in self.models.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save metadata: {e}")

    def register_model(
        self, name: str, backend: str, size: Optional[int] = None, version: Optional[str] = None
    ) -> ModelInfo:
        """
        Register a new model in the manager.

        Args:
            name: Model identifier
            backend: Backend type
            size: Model size in bytes
            version: Model version

        Returns:
            ModelInfo object for the registered model
        """
        model_info = ModelInfo(name=name, backend=backend, size=size, version=version)
        self.models[name] = model_info
        self._save_metadata()
        return model_info

    def get_model_info(self, name: str) -> Optional[ModelInfo]:
        """
        Get information about a model.

        Args:
            name: Model identifier

        Returns:
            ModelInfo if found, None otherwise
        """
        return self.models.get(name)

    def list_models(self, backend: Optional[str] = None) -> List[ModelInfo]:
        """
        List all registered models.

        Args:
            backend: Optional filter by backend type

        Returns:
            List of ModelInfo objects
        """
        models = list(self.models.values())
        if backend:
            models = [m for m in models if m.backend == backend]
        return models

    def remove_model(self, name: str) -> bool:
        """
        Remove a model from the registry.

        Args:
            name: Model identifier

        Returns:
            True if removed, False if not found
        """
        if name in self.models:
            del self.models[name]
            self._save_metadata()
            return True
        return False

    def get_recommended_models(self, task_type: str = "code_generation") -> List[Dict[str, str]]:
        """
        Get recommended models for a specific task.

        Args:
            task_type: Type of task (code_generation, chat, etc.)

        Returns:
            List of recommended model configurations
        """
        recommendations = {
            "code_generation": [
                {
                    "name": "codellama:7b",
                    "backend": "ollama",
                    "description": "Fast code generation model (7B parameters)",
                    "use_case": "General purpose code generation",
                },
                {
                    "name": "codellama:13b",
                    "backend": "ollama",
                    "description": "Balanced performance model (13B parameters)",
                    "use_case": "Higher quality code generation",
                },
                {
                    "name": "codellama:34b",
                    "backend": "ollama",
                    "description": "High quality model (34B parameters)",
                    "use_case": "Complex code generation tasks",
                },
                {
                    "name": "deepseek-coder:6.7b",
                    "backend": "ollama",
                    "description": "Efficient code generation model",
                    "use_case": "Fast code completion",
                },
            ],
            "firmware": [
                {
                    "name": "codellama:7b",
                    "backend": "ollama",
                    "description": "Embedded systems code generation",
                    "use_case": "Firmware and driver generation",
                }
            ],
            "chat": [
                {
                    "name": "llama2:7b",
                    "backend": "ollama",
                    "description": "General purpose chat model",
                    "use_case": "Interactive assistance",
                }
            ],
        }

        return recommendations.get(task_type, recommendations["code_generation"])

    def get_model_stats(self) -> Dict[str, Any]:
        """
        Get statistics about managed models.

        Returns:
            Dictionary with model statistics
        """
        total_models = len(self.models)
        backends = {}
        total_size = 0

        for model in self.models.values():
            backend = model.backend
            backends[backend] = backends.get(backend, 0) + 1
            if model.size:
                total_size += model.size

        return {
            "total_models": total_models,
            "backends": backends,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024**3), 2) if total_size > 0 else 0,
            "cache_dir": str(self.cache_dir),
        }
