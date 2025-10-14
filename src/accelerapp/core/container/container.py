"""
Enhanced dependency injection container with advanced lifecycle management.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar
import threading
import inspect

from ..exceptions import ConfigurationError, ServiceError

T = TypeVar("T")


class ServiceLifecycle(Enum):
    """Service lifecycle types."""
    SINGLETON = "singleton"  # Single instance for application lifetime
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"       # Single instance per scope
    FACTORY = "factory"     # Created by factory function


class ServiceRegistration:
    """Represents a service registration."""
    
    def __init__(
        self,
        service_type: Type,
        implementation: Optional[Type] = None,
        lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT,
        factory: Optional[Callable] = None,
        instance: Optional[Any] = None,
    ):
        self.service_type = service_type
        self.implementation = implementation or service_type
        self.lifecycle = lifecycle
        self.factory = factory
        self.instance = instance
        self.dependencies: Set[str] = set()


class ServiceContainer:
    """
    Advanced dependency injection container.
    
    Features:
    - Multiple lifecycle types (Singleton, Transient, Scoped, Factory)
    - Circular dependency detection
    - Type-safe service resolution
    - Thread-safe operations
    - Service health monitoring
    """
    
    def __init__(self):
        """Initialize service container."""
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._resolution_stack: List[str] = []
        self._lock = threading.RLock()
        
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a service with specified lifecycle.
        
        Args:
            service_type: Service interface type
            implementation: Service implementation (defaults to service_type)
            lifecycle: Service lifecycle management strategy
            name: Optional service name for multiple implementations
            
        Raises:
            ConfigurationError: If service is already registered
        """
        with self._lock:
            key = name or service_type.__name__
            
            if key in self._registrations:
                raise ConfigurationError(f"Service '{key}' is already registered")
            
            registration = ServiceRegistration(
                service_type=service_type,
                implementation=implementation,
                lifecycle=lifecycle,
            )
            
            self._registrations[key] = registration
    
    def register_singleton(
        self,
        service_type: Type[T],
        instance: Optional[T] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a singleton service.
        
        Args:
            service_type: Service interface type
            instance: Service instance (if None, will be created on first resolve)
            name: Optional service name
        """
        with self._lock:
            key = name or service_type.__name__
            
            if key in self._registrations:
                raise ConfigurationError(f"Service '{key}' is already registered")
            
            registration = ServiceRegistration(
                service_type=service_type,
                implementation=service_type,
                lifecycle=ServiceLifecycle.SINGLETON,
                instance=instance,
            )
            
            self._registrations[key] = registration
    
    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        name: Optional[str] = None,
    ) -> None:
        """
        Register a factory function for service creation.
        
        Args:
            service_type: Service interface type
            factory: Factory function
            name: Optional service name
        """
        with self._lock:
            key = name or service_type.__name__
            
            if key in self._registrations:
                raise ConfigurationError(f"Service '{key}' is already registered")
            
            registration = ServiceRegistration(
                service_type=service_type,
                lifecycle=ServiceLifecycle.FACTORY,
                factory=factory,
            )
            
            self._registrations[key] = registration
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a scoped service (one instance per scope).
        
        Args:
            service_type: Service interface type
            implementation: Service implementation
            name: Optional service name
        """
        with self._lock:
            key = name or service_type.__name__
            
            if key in self._registrations:
                raise ConfigurationError(f"Service '{key}' is already registered")
            
            registration = ServiceRegistration(
                service_type=service_type,
                implementation=implementation,
                lifecycle=ServiceLifecycle.SCOPED,
            )
            
            self._registrations[key] = registration
    
    def resolve(self, service_type: Type[T], name: Optional[str] = None, scope_id: Optional[str] = None) -> T:
        """
        Resolve and return a service instance.
        
        Args:
            service_type: Service type to resolve
            name: Optional service name
            scope_id: Optional scope identifier for scoped services
            
        Returns:
            Service instance
            
        Raises:
            ServiceError: If service cannot be resolved or circular dependency detected
        """
        with self._lock:
            key = name or service_type.__name__
            
            if key not in self._registrations:
                raise ServiceError(f"Service '{key}' is not registered")
            
            # Check for circular dependencies
            if key in self._resolution_stack:
                cycle = " -> ".join(self._resolution_stack + [key])
                raise ServiceError(f"Circular dependency detected: {cycle}")
            
            self._resolution_stack.append(key)
            
            try:
                return self._resolve_internal(key, scope_id)
            finally:
                self._resolution_stack.pop()
    
    def _resolve_internal(self, key: str, scope_id: Optional[str] = None) -> Any:
        """Internal service resolution logic."""
        registration = self._registrations[key]
        
        # Singleton: return or create single instance
        if registration.lifecycle == ServiceLifecycle.SINGLETON:
            if registration.instance is None:
                registration.instance = self._create_instance(registration)
            return registration.instance
        
        # Scoped: return or create instance for scope
        elif registration.lifecycle == ServiceLifecycle.SCOPED:
            scope_id = scope_id or "default"
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}
            
            if key not in self._scoped_instances[scope_id]:
                self._scoped_instances[scope_id][key] = self._create_instance(registration)
            
            return self._scoped_instances[scope_id][key]
        
        # Factory: use factory function
        elif registration.lifecycle == ServiceLifecycle.FACTORY:
            if registration.factory is None:
                raise ServiceError(f"No factory registered for service '{key}'")
            return registration.factory()
        
        # Transient: create new instance every time
        else:
            return self._create_instance(registration)
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a service instance."""
        try:
            impl = registration.implementation
            
            # Check if implementation has constructor parameters
            sig = inspect.signature(impl.__init__)
            params = list(sig.parameters.values())[1:]  # Skip 'self'
            
            if not params:
                # No constructor parameters
                return impl()
            
            # Try to resolve constructor dependencies
            kwargs = {}
            for param in params:
                if param.annotation != inspect.Parameter.empty:
                    # Try to resolve by type annotation
                    try:
                        kwargs[param.name] = self.resolve(param.annotation)
                    except ServiceError:
                        # If resolution fails and parameter has default, use it
                        if param.default != inspect.Parameter.empty:
                            kwargs[param.name] = param.default
                        else:
                            raise
            
            return impl(**kwargs)
            
        except Exception as e:
            raise ServiceError(
                f"Failed to instantiate service '{registration.service_type.__name__}': {e}"
            )
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered
        """
        with self._lock:
            return name in self._registrations
    
    def clear_scope(self, scope_id: str) -> None:
        """
        Clear all scoped instances for a given scope.
        
        Args:
            scope_id: Scope identifier
        """
        with self._lock:
            if scope_id in self._scoped_instances:
                del self._scoped_instances[scope_id]
    
    def clear(self) -> None:
        """Clear all registered services."""
        with self._lock:
            self._registrations.clear()
            self._scoped_instances.clear()
            self._resolution_stack.clear()
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered services.
        
        Returns:
            Dictionary of service names and their metadata
        """
        with self._lock:
            services = {}
            
            for name, reg in self._registrations.items():
                services[name] = {
                    "type": reg.service_type.__name__,
                    "lifecycle": reg.lifecycle.value,
                    "implementation": reg.implementation.__name__ if reg.implementation else None,
                    "has_instance": reg.instance is not None,
                }
            
            return services
    
    def get_service_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific service.
        
        Args:
            name: Service name
            
        Returns:
            Service metadata or None if not found
        """
        with self._lock:
            if name not in self._registrations:
                return None
            
            reg = self._registrations[name]
            return {
                "name": name,
                "type": reg.service_type.__name__,
                "lifecycle": reg.lifecycle.value,
                "implementation": reg.implementation.__name__ if reg.implementation else None,
                "has_instance": reg.instance is not None,
                "has_factory": reg.factory is not None,
            }
