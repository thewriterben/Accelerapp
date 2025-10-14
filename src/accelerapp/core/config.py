"""
Centralized configuration management for Accelerapp.
Provides configuration loading, validation, and access patterns.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from .exceptions import ConfigurationError


class ServiceConfig(BaseModel):
    """Service layer configuration."""

    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    retry_backoff: float = 1.0


class PerformanceConfig(BaseModel):
    """Performance optimization configuration."""

    enable_caching: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    enable_async: bool = True
    max_workers: int = 4


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""

    enable_metrics: bool = True
    enable_health_checks: bool = True
    metrics_port: int = 8080
    log_level: str = "INFO"
    structured_logging: bool = True


class PluginConfig(BaseModel):
    """Plugin system configuration."""

    enabled: bool = True
    plugin_dirs: list = Field(default_factory=lambda: ["plugins"])
    auto_discover: bool = True


class AppConfig(BaseModel):
    """Main application configuration."""

    service: ServiceConfig = Field(default_factory=ServiceConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)


class ConfigurationManager:
    """Manages application configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path("config")
        self._config: Optional[AppConfig] = None
        self._raw_config: Dict[str, Any] = {}

    def load(self, config_file: Optional[Path] = None) -> AppConfig:
        """
        Load configuration from file or defaults.

        Args:
            config_file: Path to configuration file

        Returns:
            Loaded configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            if config_file and config_file.exists():
                with open(config_file, "r") as f:
                    self._raw_config = yaml.safe_load(f) or {}
            else:
                # Load from environment variables
                self._load_from_env()

            self._config = AppConfig(**self._raw_config)
            return self._config

        except PydanticValidationError as e:
            raise ConfigurationError(f"Invalid configuration: {e}", {"errors": str(e)})
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        self._raw_config = {
            "service": {
                "enabled": os.getenv("SERVICE_ENABLED", "true").lower() == "true",
                "timeout": int(os.getenv("SERVICE_TIMEOUT", "30")),
            },
            "performance": {
                "enable_caching": os.getenv("ENABLE_CACHING", "true").lower() == "true",
                "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
                "enable_async": os.getenv("ENABLE_ASYNC", "true").lower() == "true",
            },
            "monitoring": {
                "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "metrics_port": int(os.getenv("METRICS_PORT", "8080")),
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (dot-separated for nested values)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        if not self._config:
            self.load()

        keys = key.split(".")
        value = self._config.dict()

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_config(self) -> AppConfig:
        """
        Get the full configuration object.

        Returns:
            Application configuration
        """
        if not self._config:
            self.load()
        return self._config

    def reload(self) -> None:
        """Reload configuration from files."""
        self._config = None
        self._raw_config = {}
        self.load()

    @property
    def service(self) -> ServiceConfig:
        """Get service configuration."""
        return self.get_config().service

    @property
    def performance(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self.get_config().performance

    @property
    def monitoring(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return self.get_config().monitoring

    @property
    def plugins(self) -> PluginConfig:
        """Get plugin configuration."""
        return self.get_config().plugins
