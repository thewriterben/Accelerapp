"""
Enhanced configuration manager with hot-reload and environment support.
"""

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import yaml
import json
from pydantic import ValidationError as PydanticValidationError
import threading
import time

from ..exceptions import ConfigurationError
from .models import AppConfig


class ConfigurationContext:
    """Thread-local configuration context for scoped configurations."""
    
    def __init__(self, config: AppConfig):
        self.config = config


class ConfigurationManager:
    """
    Enhanced configuration manager.
    
    Features:
    - Environment-specific configurations
    - Hot-reload without service restart
    - Configuration validation
    - Change notifications
    - Thread-safe operations
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path("config")
        self._config: Optional[AppConfig] = None
        self._raw_config: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._change_callbacks: List[Callable[[AppConfig], None]] = []
        self._watching = False
        self._watch_thread: Optional[threading.Thread] = None
        self._last_modified: float = 0
    
    def load(
        self,
        config_file: Optional[Path] = None,
        environment: Optional[str] = None,
    ) -> AppConfig:
        """
        Load configuration from file or defaults.
        
        Args:
            config_file: Path to configuration file
            environment: Environment name (dev, staging, prod)
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        with self._lock:
            try:
                # Determine environment
                env = environment or os.getenv("ACCELERAPP_ENV", "development")
                
                # Load base configuration
                if config_file and config_file.exists():
                    self._load_from_file(config_file)
                else:
                    # Try to load from default locations
                    self._load_from_defaults(env)
                
                # Override with environment variables
                self._load_from_env()
                
                # Validate and create config object
                self._config = AppConfig(**self._raw_config)
                self._config.environment = env
                
                return self._config
                
            except PydanticValidationError as e:
                raise ConfigurationError(
                    f"Invalid configuration: {e}",
                    {"errors": str(e)}
                )
            except Exception as e:
                raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _load_from_file(self, config_file: Path) -> None:
        """Load configuration from a file."""
        with open(config_file, "r") as f:
            if config_file.suffix in [".yaml", ".yml"]:
                self._raw_config = yaml.safe_load(f) or {}
            elif config_file.suffix == ".json":
                self._raw_config = json.load(f)
            else:
                raise ConfigurationError(
                    f"Unsupported config file format: {config_file.suffix}"
                )
        
        self._last_modified = config_file.stat().st_mtime
    
    def _load_from_defaults(self, environment: str) -> None:
        """Load configuration from default locations."""
        # Try environment-specific config first
        env_config = self.config_dir / f"config.{environment}.yaml"
        if env_config.exists():
            self._load_from_file(env_config)
            return
        
        # Try base config
        base_config = self.config_dir / "config.yaml"
        if base_config.exists():
            self._load_from_file(base_config)
            return
        
        # Use environment variables only
        self._raw_config = {}
    
    def _load_from_env(self) -> None:
        """Load and override configuration from environment variables."""
        env_overrides = {}
        
        # Only add overrides if environment variables are actually set
        if os.getenv("ACCELERAPP_DEBUG"):
            env_overrides["debug"] = os.getenv("ACCELERAPP_DEBUG", "").lower() == "true"
        
        service_overrides = {}
        if os.getenv("SERVICE_ENABLED"):
            service_overrides["enabled"] = os.getenv("SERVICE_ENABLED").lower() == "true"
        if os.getenv("SERVICE_TIMEOUT"):
            service_overrides["timeout"] = int(os.getenv("SERVICE_TIMEOUT"))
        if os.getenv("SERVICE_MAX_CONCURRENT"):
            service_overrides["max_concurrent_requests"] = int(os.getenv("SERVICE_MAX_CONCURRENT"))
        if service_overrides:
            env_overrides["service"] = service_overrides
        
        performance_overrides = {}
        if os.getenv("ENABLE_CACHING"):
            performance_overrides["enable_caching"] = os.getenv("ENABLE_CACHING").lower() == "true"
        if os.getenv("CACHE_TTL"):
            performance_overrides["cache_ttl"] = int(os.getenv("CACHE_TTL"))
        if os.getenv("ENABLE_ASYNC"):
            performance_overrides["enable_async"] = os.getenv("ENABLE_ASYNC").lower() == "true"
        if os.getenv("MAX_WORKERS"):
            performance_overrides["max_workers"] = int(os.getenv("MAX_WORKERS"))
        if performance_overrides:
            env_overrides["performance"] = performance_overrides
        
        monitoring_overrides = {}
        if os.getenv("ENABLE_METRICS"):
            monitoring_overrides["enable_metrics"] = os.getenv("ENABLE_METRICS").lower() == "true"
        if os.getenv("LOG_LEVEL"):
            monitoring_overrides["log_level"] = os.getenv("LOG_LEVEL")
        if os.getenv("METRICS_PORT"):
            monitoring_overrides["metrics_port"] = int(os.getenv("METRICS_PORT"))
        if os.getenv("STRUCTURED_LOGGING"):
            monitoring_overrides["structured_logging"] = os.getenv("STRUCTURED_LOGGING").lower() == "true"
        if monitoring_overrides:
            env_overrides["monitoring"] = monitoring_overrides
        
        plugins_overrides = {}
        if os.getenv("PLUGINS_ENABLED"):
            plugins_overrides["enabled"] = os.getenv("PLUGINS_ENABLED").lower() == "true"
        if os.getenv("PLUGINS_HOT_RELOAD"):
            plugins_overrides["hot_reload"] = os.getenv("PLUGINS_HOT_RELOAD").lower() == "true"
        if plugins_overrides:
            env_overrides["plugins"] = plugins_overrides
        
        security_overrides = {}
        if os.getenv("ENABLE_ENCRYPTION"):
            security_overrides["enable_encryption"] = os.getenv("ENABLE_ENCRYPTION").lower() == "true"
        if os.getenv("SECRET_KEY"):
            security_overrides["secret_key"] = os.getenv("SECRET_KEY")
        if security_overrides:
            env_overrides["security"] = security_overrides
        
        # Deep merge environment overrides
        if env_overrides:
            self._deep_merge(self._raw_config, env_overrides)
    
    def _deep_merge(self, base: Dict, updates: Dict) -> None:
        """Deep merge updates into base dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            elif value is not None:
                base[key] = value
    
    def reload(self) -> AppConfig:
        """
        Reload configuration from sources.
        
        Returns:
            Reloaded configuration
        """
        with self._lock:
            old_config = self._config
            new_config = self.load()
            
            # Notify listeners of configuration change
            if old_config != new_config:
                self._notify_change(new_config)
            
            return new_config
    
    def register_change_callback(self, callback: Callable[[AppConfig], None]) -> None:
        """
        Register a callback for configuration changes.
        
        Args:
            callback: Callback function to execute on config change
        """
        with self._lock:
            self._change_callbacks.append(callback)
    
    def _notify_change(self, new_config: AppConfig) -> None:
        """Notify all registered callbacks of configuration change."""
        for callback in self._change_callbacks:
            try:
                callback(new_config)
            except Exception as e:
                # Log but don't fail on callback errors
                print(f"Configuration change callback failed: {e}")
    
    def start_watching(self, check_interval: int = 5) -> None:
        """
        Start watching configuration files for changes.
        
        Args:
            check_interval: Interval in seconds to check for changes
        """
        if self._watching:
            return
        
        self._watching = True
        self._watch_thread = threading.Thread(
            target=self._watch_loop,
            args=(check_interval,),
            daemon=True
        )
        self._watch_thread.start()
    
    def stop_watching(self) -> None:
        """Stop watching configuration files."""
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=5)
    
    def _watch_loop(self, check_interval: int) -> None:
        """Configuration file watch loop."""
        while self._watching:
            try:
                # Check if config file has been modified
                env = os.getenv("ACCELERAPP_ENV", "development")
                config_file = self.config_dir / f"config.{env}.yaml"
                
                if not config_file.exists():
                    config_file = self.config_dir / "config.yaml"
                
                if config_file.exists():
                    current_modified = config_file.stat().st_mtime
                    if current_modified > self._last_modified:
                        self.reload()
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Error in configuration watch loop: {e}")
                time.sleep(check_interval)
    
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
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value (runtime only, not persisted).
        
        Args:
            key: Configuration key (dot-separated)
            value: Value to set
        """
        with self._lock:
            if not self._config:
                self.load()
            
            keys = key.split(".")
            config_dict = self._config.dict()
            
            # Navigate to the parent
            current = config_dict
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
            # Recreate config with validation
            self._config = AppConfig(**config_dict)
    
    def get_config(self) -> AppConfig:
        """
        Get the full configuration object.
        
        Returns:
            Application configuration
        """
        if not self._config:
            self.load()
        return self._config
    
    @property
    def service(self) -> Any:
        """Get service configuration."""
        return self.get_config().service
    
    @property
    def performance(self) -> Any:
        """Get performance configuration."""
        return self.get_config().performance
    
    @property
    def monitoring(self) -> Any:
        """Get monitoring configuration."""
        return self.get_config().monitoring
    
    @property
    def plugins(self) -> Any:
        """Get plugin configuration."""
        return self.get_config().plugins
    
    @property
    def security(self) -> Any:
        """Get security configuration."""
        return self.get_config().security
    
    @property
    def events(self) -> Any:
        """Get event configuration."""
        return self.get_config().events
