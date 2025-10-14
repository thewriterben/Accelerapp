"""
Base plugin classes for Accelerapp.
Provides abstract base classes for plugin development.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    name: str
    version: str
    author: str
    description: str
    capabilities: List[str]
    dependencies: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.dependencies is None:
            self.dependencies = []


class BasePlugin(ABC):
    """Abstract base class for plugins."""

    def __init__(self, metadata: PluginMetadata):
        """
        Initialize plugin.

        Args:
            metadata: Plugin metadata
        """
        self.metadata = metadata
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the plugin."""
        self._initialized = True

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the plugin gracefully."""
        self._initialized = False

    def get_name(self) -> str:
        """Get plugin name."""
        return self.metadata.name

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "capabilities": self.metadata.capabilities,
            "dependencies": self.metadata.dependencies,
        }

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.

        Returns:
            Plugin information dictionary
        """
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "description": self.metadata.description,
            "capabilities": self.metadata.capabilities,
            "dependencies": self.metadata.dependencies,
            "initialized": self._initialized,
        }


class GeneratorPlugin(BasePlugin):
    """Base class for code generator plugins."""

    @abstractmethod
    def generate(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code or output.

        Args:
            spec: Generation specification
            context: Optional context

        Returns:
            Generation result
        """
        pass

    @abstractmethod
    def validate_spec(self, spec: Dict[str, Any]) -> bool:
        """
        Validate generation specification.

        Args:
            spec: Specification to validate

        Returns:
            True if valid
        """
        pass


class AnalyzerPlugin(BasePlugin):
    """Base class for code analyzer plugins."""

    @abstractmethod
    def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code.

        Args:
            code: Source code
            language: Programming language

        Returns:
            Analysis results
        """
        pass


class TransformerPlugin(BasePlugin):
    """Base class for code transformer plugins."""

    @abstractmethod
    def transform(self, code: str, options: Dict[str, Any]) -> str:
        """
        Transform code.

        Args:
            code: Source code
            options: Transformation options

        Returns:
            Transformed code
        """
        pass
