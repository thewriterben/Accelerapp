"""
Abstract base classes and protocols for Accelerapp architecture.
Defines contracts for services, agents, plugins, and repositories.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class IService(Protocol):
    """Protocol for service layer components."""

    async def initialize(self) -> None:
        """Initialize the service."""
        ...

    async def shutdown(self) -> None:
        """Shutdown the service gracefully."""
        ...

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        ...


@runtime_checkable
class IAgent(Protocol):
    """Protocol for AI agent components."""

    def can_handle(self, task: str) -> bool:
        """Check if agent can handle a task."""
        ...

    def generate(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate output based on specification."""
        ...

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        ...


@runtime_checkable
class IPlugin(Protocol):
    """Protocol for plugin components."""

    def get_name(self) -> str:
        """Get plugin name."""
        ...

    def get_version(self) -> str:
        """Get plugin version."""
        ...

    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities."""
        ...

    async def initialize(self) -> None:
        """Initialize the plugin."""
        ...

    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        ...


@runtime_checkable
class IRepository(Protocol):
    """Protocol for data repository components."""

    async def get(self, key: str) -> Optional[Any]:
        """Get item by key."""
        ...

    async def set(self, key: str, value: Any) -> None:
        """Set item by key."""
        ...

    async def delete(self, key: str) -> None:
        """Delete item by key."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...


class BaseService(ABC):
    """Base class for service implementations."""

    def __init__(self, name: str):
        """
        Initialize base service.

        Args:
            name: Service name
        """
        self.name = name
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        self._initialized = True

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service gracefully."""
        self._initialized = False

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        return {
            "service": self.name,
            "status": "healthy" if self._initialized else "stopped",
            "initialized": self._initialized,
        }

    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self._initialized
