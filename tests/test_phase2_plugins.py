"""
Tests for Phase 2 plugin system.
"""

import pytest
from accelerapp.plugins import BasePlugin, PluginMetadata, PluginRegistry
from accelerapp.plugins.base import GeneratorPlugin, AnalyzerPlugin


class MockPlugin(BasePlugin):
    """Mock plugin for testing."""

    def __init__(self):
        metadata = PluginMetadata(
            name="MockPlugin",
            version="1.0.0",
            author="Test Author",
            description="Mock plugin for testing",
            capabilities=["test", "mock"],
        )
        super().__init__(metadata)

    async def initialize(self):
        await super().initialize()

    async def shutdown(self):
        await super().shutdown()


class MockGeneratorPlugin(GeneratorPlugin):
    """Mock generator plugin for testing."""

    def __init__(self):
        metadata = PluginMetadata(
            name="MockGenerator",
            version="1.0.0",
            author="Test Author",
            description="Mock generator plugin",
            capabilities=["code_generation"],
        )
        super().__init__(metadata)

    async def initialize(self):
        await super().initialize()

    async def shutdown(self):
        await super().shutdown()

    def generate(self, spec, context=None):
        return {"status": "success", "code": "generated_code"}

    def validate_spec(self, spec):
        return "input" in spec


class TestBasePlugin:
    """Test base plugin functionality."""

    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self):
        """Test plugin initialization and shutdown."""
        plugin = MockPlugin()

        assert not plugin.is_initialized

        await plugin.initialize()
        assert plugin.is_initialized

        await plugin.shutdown()
        assert not plugin.is_initialized

    def test_plugin_metadata(self):
        """Test plugin metadata access."""
        plugin = MockPlugin()

        assert plugin.get_name() == "MockPlugin"
        assert plugin.get_version() == "1.0.0"

        capabilities = plugin.get_capabilities()
        assert capabilities["name"] == "MockPlugin"
        assert "test" in capabilities["capabilities"]

    def test_plugin_info(self):
        """Test getting plugin information."""
        plugin = MockPlugin()

        info = plugin.get_info()

        assert info["name"] == "MockPlugin"
        assert info["version"] == "1.0.0"
        assert info["author"] == "Test Author"
        assert info["description"] == "Mock plugin for testing"
        assert info["initialized"] is False


class TestGeneratorPlugin:
    """Test generator plugin functionality."""

    @pytest.mark.asyncio
    async def test_generator_plugin(self):
        """Test generator plugin."""
        plugin = MockGeneratorPlugin()
        await plugin.initialize()

        spec = {"input": "test"}
        result = plugin.generate(spec)

        assert result["status"] == "success"
        assert "code" in result

    def test_validate_spec(self):
        """Test spec validation."""
        plugin = MockGeneratorPlugin()

        assert plugin.validate_spec({"input": "test"}) is True
        assert plugin.validate_spec({}) is False


class TestPluginRegistry:
    """Test plugin registry."""

    def test_register_plugin(self):
        """Test registering plugin."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)

        assert plugin.get_name() in registry.list_plugins()

    def test_get_plugin(self):
        """Test getting plugin."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)
        retrieved = registry.get("MockPlugin")

        assert retrieved is plugin

    def test_unregister_plugin(self):
        """Test unregistering plugin."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)
        assert registry.unregister("MockPlugin") is True
        assert registry.get("MockPlugin") is None

    def test_list_plugins(self):
        """Test listing plugins."""
        registry = PluginRegistry()

        plugin1 = MockPlugin()
        registry.register(plugin1)

        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert "MockPlugin" in plugins

    def test_get_plugin_info(self):
        """Test getting plugin information."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)
        info = registry.get_plugin_info("MockPlugin")

        assert info is not None
        assert info["name"] == "MockPlugin"

    def test_get_all_info(self):
        """Test getting all plugin information."""
        registry = PluginRegistry()

        plugin1 = MockPlugin()
        registry.register(plugin1)

        all_info = registry.get_all_info()
        assert len(all_info) == 1
        assert all_info[0]["name"] == "MockPlugin"

    @pytest.mark.asyncio
    async def test_initialize_all(self):
        """Test initializing all plugins."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)
        await registry.initialize_all()

        assert plugin.is_initialized

    @pytest.mark.asyncio
    async def test_shutdown_all(self):
        """Test shutting down all plugins."""
        registry = PluginRegistry()
        plugin = MockPlugin()

        registry.register(plugin)
        await registry.initialize_all()
        await registry.shutdown_all()

        assert not plugin.is_initialized

    def test_find_plugins_by_capability(self):
        """Test finding plugins by capability."""
        registry = PluginRegistry()

        plugin1 = MockPlugin()
        plugin2 = MockGeneratorPlugin()

        registry.register(plugin1)
        registry.register(plugin2)

        found = registry.find_plugins_by_capability("test")
        assert len(found) == 1
        assert found[0].get_name() == "MockPlugin"

        found = registry.find_plugins_by_capability("code_generation")
        assert len(found) == 1
        assert found[0].get_name() == "MockGenerator"
