"""
Tests for Phase 2 core architecture components.
"""

import pytest
from accelerapp.core import (
    ServiceContainer,
    ConfigurationManager,
    AccelerappException,
    ConfigurationError,
    ServiceError,
    BaseService,
)


class TestServiceContainer:
    """Test dependency injection container."""

    def test_register_and_resolve(self):
        """Test service registration and resolution."""
        container = ServiceContainer()

        class TestService:
            def __init__(self):
                self.name = "test"

        container.register(TestService)
        service = container.resolve(TestService)

        assert service is not None
        assert service.name == "test"

    def test_register_singleton(self):
        """Test singleton registration."""
        container = ServiceContainer()

        class TestService:
            def __init__(self):
                self.value = 42

        instance = TestService()
        container.register_singleton(TestService, instance)

        service1 = container.resolve(TestService)
        service2 = container.resolve(TestService)

        assert service1 is service2
        assert service1.value == 42

    def test_register_factory(self):
        """Test factory registration."""
        container = ServiceContainer()
        call_count = [0]

        def factory():
            call_count[0] += 1
            return {"count": call_count[0]}

        class TestService:
            pass

        container.register_factory(TestService, factory)

        result1 = container.resolve(TestService)
        result2 = container.resolve(TestService)

        assert result1["count"] == 1
        assert result2["count"] == 2

    def test_has_service(self):
        """Test checking if service exists."""
        container = ServiceContainer()

        class TestService:
            pass

        assert not container.has("TestService")

        container.register(TestService)
        assert container.has("TestService")

    def test_service_not_found(self):
        """Test resolving non-existent service."""
        container = ServiceContainer()

        with pytest.raises(ServiceError):
            container.resolve(str, name="NonExistent")


class TestConfigurationManager:
    """Test configuration manager."""

    def test_default_configuration(self):
        """Test loading default configuration."""
        config_mgr = ConfigurationManager()
        config = config_mgr.load()

        assert config is not None
        assert config.service.enabled is True
        assert config.performance.enable_caching is True
        assert config.monitoring.enable_metrics is True

    def test_get_configuration(self):
        """Test getting configuration values."""
        config_mgr = ConfigurationManager()
        config_mgr.load()

        assert config_mgr.get("service.enabled") is True
        assert config_mgr.get("performance.cache_ttl") == 3600
        assert config_mgr.get("nonexistent.key", "default") == "default"

    def test_configuration_properties(self):
        """Test configuration property accessors."""
        config_mgr = ConfigurationManager()
        config_mgr.load()

        assert config_mgr.service is not None
        assert config_mgr.performance is not None
        assert config_mgr.monitoring is not None
        assert config_mgr.plugins is not None


class TestBaseService:
    """Test base service implementation."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and shutdown."""
        
        class TestService(BaseService):
            async def initialize(self):
                await super().initialize()
            
            async def shutdown(self):
                await super().shutdown()

        service = TestService("TestService")

        assert not service.is_initialized
        
        await service.initialize()
        assert service.is_initialized

        health = service.get_health()
        assert health["status"] == "healthy"
        assert health["initialized"] is True

        await service.shutdown()
        assert not service.is_initialized


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_base_exception(self):
        """Test base exception."""
        ex = AccelerappException("Test error", {"detail": "test"})

        assert str(ex) == "Test error - Details: {'detail': 'test'}"
        assert ex.message == "Test error"
        assert ex.details["detail"] == "test"

    def test_configuration_error(self):
        """Test configuration error."""
        ex = ConfigurationError("Config error")

        assert isinstance(ex, AccelerappException)
        assert "Config error" in str(ex)

    def test_service_error(self):
        """Test service error."""
        ex = ServiceError("Service failed")

        assert isinstance(ex, AccelerappException)
        assert "Service failed" in str(ex)
