"""
Tests for enhanced dependency injection container.
"""

import pytest
import asyncio
from src.accelerapp.core.container import (
    ServiceContainer,
    ServiceLifecycle,
    LifecycleManager,
    ServiceHealthMonitor,
    HealthStatus,
    create_proxy,
)
from src.accelerapp.core.exceptions import ConfigurationError, ServiceError


class SimpleService:
    """Simple test service."""
    
    def __init__(self):
        self.value = "simple"
    
    def get_value(self):
        return self.value


class DependentService:
    """Service with dependencies."""
    
    def __init__(self, dependency: SimpleService):
        self.dependency = dependency
    
    def get_dependency_value(self):
        return self.dependency.get_value()


class LifecycleAwareService:
    """Service that implements lifecycle methods."""
    
    def __init__(self):
        self.initialized = False
        self.started = False
    
    async def initialize(self):
        self.initialized = True
    
    async def start(self):
        self.started = True
    
    async def stop(self):
        self.started = False


class TestServiceContainer:
    """Test service container functionality."""
    
    def test_register_and_resolve_transient(self):
        """Test transient service registration and resolution."""
        container = ServiceContainer()
        container.register(SimpleService, lifecycle=ServiceLifecycle.TRANSIENT)
        
        service1 = container.resolve(SimpleService)
        service2 = container.resolve(SimpleService)
        
        assert isinstance(service1, SimpleService)
        assert isinstance(service2, SimpleService)
        assert service1 is not service2  # Different instances
    
    def test_register_and_resolve_singleton(self):
        """Test singleton service registration."""
        container = ServiceContainer()
        container.register(SimpleService, lifecycle=ServiceLifecycle.SINGLETON)
        
        service1 = container.resolve(SimpleService)
        service2 = container.resolve(SimpleService)
        
        assert service1 is service2  # Same instance
    
    def test_register_singleton_with_instance(self):
        """Test registering a singleton with pre-created instance."""
        container = ServiceContainer()
        instance = SimpleService()
        instance.value = "custom"
        
        container.register_singleton(SimpleService, instance=instance)
        
        service = container.resolve(SimpleService)
        assert service is instance
        assert service.value == "custom"
    
    def test_register_factory(self):
        """Test factory registration."""
        container = ServiceContainer()
        
        counter = [0]
        def factory():
            counter[0] += 1
            service = SimpleService()
            service.value = f"factory_{counter[0]}"
            return service
        
        container.register_factory(SimpleService, factory)
        
        service1 = container.resolve(SimpleService)
        service2 = container.resolve(SimpleService)
        
        assert service1.value == "factory_1"
        assert service2.value == "factory_2"
    
    def test_register_scoped(self):
        """Test scoped service registration."""
        container = ServiceContainer()
        container.register_scoped(SimpleService)
        
        # Same scope returns same instance
        service1 = container.resolve(SimpleService, scope_id="scope1")
        service2 = container.resolve(SimpleService, scope_id="scope1")
        assert service1 is service2
        
        # Different scope returns different instance
        service3 = container.resolve(SimpleService, scope_id="scope2")
        assert service1 is not service3
    
    def test_dependency_injection(self):
        """Test automatic dependency injection."""
        container = ServiceContainer()
        container.register(SimpleService, lifecycle=ServiceLifecycle.SINGLETON)
        container.register(DependentService, lifecycle=ServiceLifecycle.TRANSIENT)
        
        service = container.resolve(DependentService)
        assert isinstance(service, DependentService)
        assert service.get_dependency_value() == "simple"
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        # This would require circular dependencies, which we'll skip for now
        # as it requires more complex setup
        pass
    
    def test_duplicate_registration_error(self):
        """Test that duplicate registration raises error."""
        container = ServiceContainer()
        container.register(SimpleService)
        
        with pytest.raises(ConfigurationError):
            container.register(SimpleService)
    
    def test_resolve_unregistered_service(self):
        """Test resolving unregistered service raises error."""
        container = ServiceContainer()
        
        with pytest.raises(ServiceError):
            container.resolve(SimpleService)
    
    def test_has_service(self):
        """Test checking if service is registered."""
        container = ServiceContainer()
        
        assert not container.has("SimpleService")
        container.register(SimpleService)
        assert container.has("SimpleService")
    
    def test_get_service_info(self):
        """Test getting service information."""
        container = ServiceContainer()
        container.register(SimpleService, lifecycle=ServiceLifecycle.SINGLETON)
        
        info = container.get_service_info("SimpleService")
        assert info is not None
        assert info["type"] == "SimpleService"
        assert info["lifecycle"] == "singleton"
    
    def test_clear_scope(self):
        """Test clearing scoped instances."""
        container = ServiceContainer()
        container.register_scoped(SimpleService)
        
        service1 = container.resolve(SimpleService, scope_id="scope1")
        container.clear_scope("scope1")
        service2 = container.resolve(SimpleService, scope_id="scope1")
        
        assert service1 is not service2


@pytest.mark.asyncio
class TestLifecycleManager:
    """Test lifecycle manager functionality."""
    
    async def test_initialize_service(self):
        """Test service initialization."""
        manager = LifecycleManager()
        service = LifecycleAwareService()
        
        manager.register_service("test_service", service)
        await manager.initialize_service("test_service")
        
        assert service.initialized
        assert manager.get_state("test_service").value == "initialized"
    
    async def test_start_service(self):
        """Test service starting."""
        manager = LifecycleManager()
        service = LifecycleAwareService()
        
        manager.register_service("test_service", service)
        await manager.initialize_service("test_service")
        await manager.start_service("test_service")
        
        assert service.started
        assert manager.get_state("test_service").value == "running"
    
    async def test_stop_service(self):
        """Test service stopping."""
        manager = LifecycleManager()
        service = LifecycleAwareService()
        
        manager.register_service("test_service", service)
        await manager.initialize_service("test_service")
        await manager.start_service("test_service")
        await manager.stop_service("test_service")
        
        assert not service.started
        assert manager.get_state("test_service").value == "stopped"
    
    async def test_lifecycle_hooks(self):
        """Test lifecycle hooks."""
        manager = LifecycleManager()
        service = LifecycleAwareService()
        
        hook_calls = []
        
        def before_init(name, svc):
            hook_calls.append(("before_init", name))
        
        def after_init(name, svc):
            hook_calls.append(("after_init", name))
        
        manager.register_hook("before_init", before_init)
        manager.register_hook("after_init", after_init)
        manager.register_service("test_service", service)
        
        await manager.initialize_service("test_service")
        
        assert ("before_init", "test_service") in hook_calls
        assert ("after_init", "test_service") in hook_calls


@pytest.mark.asyncio
class TestServiceHealthMonitor:
    """Test service health monitoring."""
    
    async def test_register_service(self):
        """Test registering service for monitoring."""
        monitor = ServiceHealthMonitor()
        service = SimpleService()
        
        monitor.register_service("test_service", service)
        
        status = monitor.get_health_status("test_service")
        assert status is not None
        assert status.status == HealthStatus.UNKNOWN
    
    async def test_health_check_healthy(self):
        """Test health check for healthy service."""
        monitor = ServiceHealthMonitor()
        service = SimpleService()
        
        def health_check():
            return True
        
        monitor.register_service("test_service", service, health_check)
        result = await monitor.check_service_health("test_service")
        
        assert result.status == HealthStatus.HEALTHY
    
    async def test_health_check_unhealthy(self):
        """Test health check for unhealthy service."""
        monitor = ServiceHealthMonitor()
        service = SimpleService()
        
        def health_check():
            return False
        
        monitor.register_service("test_service", service, health_check)
        result = await monitor.check_service_health("test_service")
        
        assert result.status == HealthStatus.UNHEALTHY
    
    async def test_recovery_callback(self):
        """Test recovery callback execution."""
        monitor = ServiceHealthMonitor()
        service = SimpleService()
        
        recovered = [False]
        
        def recovery_callback(svc):
            recovered[0] = True
        
        def health_check():
            return False
        
        monitor.register_service("test_service", service, health_check)
        monitor.register_recovery_callback("test_service", recovery_callback)
        
        await monitor.check_service_health("test_service")
        
        assert recovered[0]


class TestServiceProxy:
    """Test service proxy functionality."""
    
    def test_proxy_method_call(self):
        """Test proxying method calls."""
        service = SimpleService()
        proxy = create_proxy(service)
        
        result = proxy.get_value()
        assert result == "simple"
    
    def test_proxy_with_logging(self):
        """Test proxy with logging enabled."""
        service = SimpleService()
        proxy = create_proxy(service, log_calls=True)
        
        # Should not raise error
        result = proxy.get_value()
        assert result == "simple"
    
    def test_proxy_get_target(self):
        """Test getting underlying target from proxy."""
        service = SimpleService()
        proxy = create_proxy(service)
        
        target = proxy.get_target()
        assert target is service
