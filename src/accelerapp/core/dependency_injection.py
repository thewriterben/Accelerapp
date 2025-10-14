"""
Dependency injection container for Accelerapp.
Provides service registration, resolution, and lifecycle management.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

from .exceptions import ConfigurationError, ServiceError

T = TypeVar("T")


class ServiceContainer:
    """Dependency injection container for managing services."""

    def __init__(self):
        """Initialize service container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register(
        self, service_type: Type[T], implementation: Optional[Type[T]] = None, name: Optional[str] = None
    ) -> None:
        """
        Register a service type with its implementation.

        Args:
            service_type: Service interface type
            implementation: Service implementation (defaults to service_type)
            name: Optional service name for multiple implementations
        """
        impl = implementation or service_type
        key = name or service_type.__name__

        if key in self._services:
            raise ConfigurationError(f"Service '{key}' is already registered")

        self._services[key] = impl

    def register_singleton(
        self, service_type: Type[T], instance: T, name: Optional[str] = None
    ) -> None:
        """
        Register a singleton service instance.

        Args:
            service_type: Service interface type
            instance: Service instance
            name: Optional service name
        """
        key = name or service_type.__name__
        if key in self._singletons:
            raise ConfigurationError(f"Singleton '{key}' is already registered")

        self._singletons[key] = instance

    def register_factory(
        self, service_type: Type[T], factory: Callable[[], T], name: Optional[str] = None
    ) -> None:
        """
        Register a factory function for creating service instances.

        Args:
            service_type: Service interface type
            factory: Factory function
            name: Optional service name
        """
        key = name or service_type.__name__
        if key in self._factories:
            raise ConfigurationError(f"Factory '{key}' is already registered")

        self._factories[key] = factory

    def resolve(self, service_type: Type[T], name: Optional[str] = None) -> T:
        """
        Resolve and return a service instance.

        Args:
            service_type: Service type to resolve
            name: Optional service name

        Returns:
            Service instance

        Raises:
            ServiceError: If service cannot be resolved
        """
        key = name or service_type.__name__

        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]

        # Check factories
        if key in self._factories:
            return self._factories[key]()

        # Check registered services
        if key in self._services:
            impl = self._services[key]
            try:
                return impl()
            except Exception as e:
                raise ServiceError(f"Failed to instantiate service '{key}': {e}")

        raise ServiceError(f"Service '{key}' is not registered")

    def get(self, name: str) -> Any:
        """
        Get a service by name.

        Args:
            name: Service name

        Returns:
            Service instance
        """
        if name in self._singletons:
            return self._singletons[name]

        if name in self._factories:
            return self._factories[name]()

        if name in self._services:
            impl = self._services[name]
            try:
                return impl()
            except Exception as e:
                raise ServiceError(f"Failed to instantiate service '{name}': {e}")

        raise ServiceError(f"Service '{name}' not found")

    def has(self, name: str) -> bool:
        """
        Check if a service is registered.

        Args:
            name: Service name

        Returns:
            True if service is registered
        """
        return name in self._services or name in self._singletons or name in self._factories

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

    def get_all_services(self) -> Dict[str, str]:
        """
        Get information about all registered services.

        Returns:
            Dictionary of service names and types
        """
        services = {}

        for name in self._services:
            services[name] = "registered"

        for name in self._factories:
            services[name] = "factory"

        for name in self._singletons:
            services[name] = "singleton"

        return services
