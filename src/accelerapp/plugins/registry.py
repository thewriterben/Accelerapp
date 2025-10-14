"""
Plugin registry for Accelerapp.
Manages plugin discovery, registration, and lifecycle.
"""

import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..core.exceptions import PluginError
from ..monitoring import get_logger
from .base import BasePlugin


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        """Initialize plugin registry."""
        self.logger = get_logger(__name__)
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_types: Dict[str, Type[BasePlugin]] = {}

    def register(self, plugin: BasePlugin) -> None:
        """
        Register a plugin instance.

        Args:
            plugin: Plugin instance

        Raises:
            PluginError: If plugin is already registered
        """
        name = plugin.get_name()
        if name in self._plugins:
            raise PluginError(f"Plugin '{name}' is already registered")

        self._plugins[name] = plugin
        self.logger.info(f"Registered plugin: {name} v{plugin.get_version()}")

    def register_type(self, plugin_type: Type[BasePlugin]) -> None:
        """
        Register a plugin type for auto-instantiation.

        Args:
            plugin_type: Plugin class

        Raises:
            PluginError: If plugin type is already registered
        """
        name = plugin_type.__name__
        if name in self._plugin_types:
            raise PluginError(f"Plugin type '{name}' is already registered")

        self._plugin_types[name] = plugin_type
        self.logger.info(f"Registered plugin type: {name}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            name: Plugin name

        Returns:
            True if plugin was unregistered
        """
        if name in self._plugins:
            del self._plugins[name]
            self.logger.info(f"Unregistered plugin: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        """
        List all registered plugins.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information.

        Args:
            name: Plugin name

        Returns:
            Plugin information or None
        """
        plugin = self.get(name)
        if plugin:
            return plugin.get_info()
        return None

    def get_all_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all plugins.

        Returns:
            List of plugin information dictionaries
        """
        return [plugin.get_info() for plugin in self._plugins.values()]

    async def initialize_all(self) -> None:
        """Initialize all registered plugins."""
        for name, plugin in self._plugins.items():
            try:
                await plugin.initialize()
                self.logger.info(f"Initialized plugin: {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize plugin {name}: {e}")
                raise PluginError(f"Failed to initialize plugin {name}: {e}")

    async def shutdown_all(self) -> None:
        """Shutdown all registered plugins."""
        for name, plugin in self._plugins.items():
            try:
                await plugin.shutdown()
                self.logger.info(f"Shutdown plugin: {name}")
            except Exception as e:
                self.logger.error(f"Failed to shutdown plugin {name}: {e}")

    def discover_plugins(self, plugin_dir: Path) -> List[str]:
        """
        Discover plugins in a directory.

        Args:
            plugin_dir: Directory to search for plugins

        Returns:
            List of discovered plugin names
        """
        discovered = []

        if not plugin_dir.exists():
            self.logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return discovered

        # Look for Python files
        for file_path in plugin_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                # Import module
                module_name = file_path.stem
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find BasePlugin subclasses
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BasePlugin) and obj != BasePlugin:
                            self.register_type(obj)
                            discovered.append(name)

            except Exception as e:
                self.logger.error(f"Failed to load plugin from {file_path}: {e}")

        return discovered

    def find_plugins_by_capability(self, capability: str) -> List[BasePlugin]:
        """
        Find plugins with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of matching plugins
        """
        matching = []
        for plugin in self._plugins.values():
            if capability in plugin.metadata.capabilities:
                matching.append(plugin)
        return matching


# Global plugin registry instance
_global_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    """
    Get the global plugin registry.

    Returns:
        Global plugin registry instance
    """
    return _global_registry
