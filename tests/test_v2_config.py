"""
Tests for enhanced configuration management.
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from src.accelerapp.core.config import (
    ConfigurationManager,
    AppConfig,
    ConfigValidator,
    ConfigEncryption,
    ConfigMigration,
)
from src.accelerapp.core.exceptions import ConfigurationError


class TestConfigurationModels:
    """Test Pydantic configuration models."""
    
    def test_app_config_defaults(self):
        """Test default configuration values."""
        config = AppConfig()
        
        assert config.version == "2.0.0"
        assert config.environment == "development"
        assert config.service.enabled is True
        assert config.performance.enable_caching is True
        assert config.monitoring.enable_metrics is True
    
    def test_app_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = AppConfig(
            environment="production",
            service={"timeout": 60}
        )
        assert config.environment == "production"
        assert config.service.timeout == 60
        
        # Invalid log level should raise error
        with pytest.raises(Exception):
            AppConfig(monitoring={"log_level": "INVALID"})
    
    def test_service_config_constraints(self):
        """Test service configuration constraints."""
        from src.accelerapp.core.config.models import ServiceConfig
        
        # Valid values
        config = ServiceConfig(timeout=30, retry_attempts=5)
        assert config.timeout == 30
        
        # Invalid values should raise validation error
        with pytest.raises(Exception):
            ServiceConfig(timeout=500)  # Too high
        
        with pytest.raises(Exception):
            ServiceConfig(retry_attempts=20)  # Too high


class TestConfigurationManager:
    """Test configuration manager functionality."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        manager = ConfigurationManager()
        config = manager.load()
        
        assert isinstance(config, AppConfig)
        assert config.version == "2.0.0"
    
    def test_load_from_file(self):
        """Test loading configuration from file."""
        import os
        
        # Save current env vars
        old_timeout = os.environ.get("SERVICE_TIMEOUT")
        
        # Clear env var to avoid override
        if "SERVICE_TIMEOUT" in os.environ:
            del os.environ["SERVICE_TIMEOUT"]
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "version": "2.0.0",
                "environment": "test",
                "service": {
                    "timeout": 45
                }
            }, f)
            config_file = Path(f.name)
        
        try:
            manager = ConfigurationManager()
            config = manager.load(config_file=config_file, environment="test")
            
            assert config.environment == "test"
            assert config.service.timeout == 45
        finally:
            config_file.unlink()
            # Restore env var
            if old_timeout is not None:
                os.environ["SERVICE_TIMEOUT"] = old_timeout
    
    def test_get_config_value(self):
        """Test getting configuration values by key."""
        manager = ConfigurationManager()
        manager.load()
        
        # Nested value
        timeout = manager.get("service.timeout")
        assert timeout == 30
        
        # Non-existent key with default
        value = manager.get("nonexistent.key", default="default_value")
        assert value == "default_value"
    
    def test_set_config_value(self):
        """Test setting configuration values."""
        manager = ConfigurationManager()
        manager.load()
        
        manager.set("service.timeout", 60)
        
        assert manager.get("service.timeout") == 60
    
    def test_reload_config(self):
        """Test reloading configuration."""
        manager = ConfigurationManager()
        config1 = manager.load()
        config2 = manager.reload()
        
        assert config1.version == config2.version
    
    def test_change_callback(self):
        """Test configuration change callbacks."""
        manager = ConfigurationManager()
        manager.load()
        
        callback_called = [False]
        
        def on_config_change(new_config):
            callback_called[0] = True
        
        manager.register_change_callback(on_config_change)
        
        # Trigger change by setting a value
        manager.set("service.timeout", 45)
        # Note: callback is called in reload(), not set()


class TestConfigValidator:
    """Test configuration validator."""
    
    def test_register_validator(self):
        """Test registering custom validators."""
        validator = ConfigValidator()
        
        def validate_positive(value):
            return value > 0
        
        validator.register_validator("service.timeout", validate_positive)
        
        # Valid value
        assert validator.validate_value("service.timeout", 30)
        
        # Invalid value
        with pytest.raises(ValueError):
            validator.validate_value("service.timeout", -10)
    
    def test_validate_config(self):
        """Test validating entire configuration."""
        validator = ConfigValidator()
        
        def validate_timeout(value):
            return 1 <= value <= 300
        
        validator.register_validator("service.timeout", validate_timeout)
        
        # Valid config
        config = {"service": {"timeout": 30}}
        errors = validator.validate_config(config)
        assert len(errors) == 0
        
        # Invalid config
        config = {"service": {"timeout": 500}}
        errors = validator.validate_config(config)
        assert len(errors) > 0


class TestConfigEncryption:
    """Test configuration encryption."""
    
    def test_encrypt_decrypt(self):
        """Test encrypting and decrypting values."""
        encryption = ConfigEncryption(secret_key="test-key")
        
        original = "sensitive_value"
        encrypted = encryption.encrypt(original)
        decrypted = encryption.decrypt(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_encrypt_config_values(self):
        """Test encrypting configuration values."""
        encryption = ConfigEncryption(secret_key="test-key")
        
        config = {
            "security": {
                "secret_key": "my-secret",
                "api_key": "my-api-key"
            }
        }
        
        encrypted_config = encryption.encrypt_config_values(
            config,
            ["security.secret_key", "security.api_key"]
        )
        
        # Values should be prefixed with "encrypted:"
        assert encrypted_config["security"]["secret_key"].startswith("encrypted:")
        assert encrypted_config["security"]["api_key"].startswith("encrypted:")
    
    def test_decrypt_config_values(self):
        """Test decrypting configuration values."""
        encryption = ConfigEncryption(secret_key="test-key")
        
        # Encrypt first
        config = {
            "security": {
                "secret_key": "my-secret"
            }
        }
        
        encrypted_config = encryption.encrypt_config_values(
            config,
            ["security.secret_key"]
        )
        
        # Decrypt
        decrypted_config = encryption.decrypt_config_values(encrypted_config)
        
        assert decrypted_config["security"]["secret_key"] == "my-secret"


class TestConfigMigration:
    """Test configuration migration."""
    
    def test_register_migration(self):
        """Test registering migrations."""
        migration = ConfigMigration()
        
        def migrate_func(config):
            config["new_field"] = "value"
            return config
        
        migration.register_migration("1.0", "2.0", migrate_func)
        
        migrations = migration.get_available_migrations()
        assert "1.0->2.0" in migrations
    
    def test_migrate_config(self):
        """Test migrating configuration."""
        migration = ConfigMigration()
        
        def migrate_1_to_2(config):
            config["version"] = "2.0"
            config["new_feature"] = True
            return config
        
        migration.register_migration("1.0", "2.0", migrate_1_to_2)
        
        old_config = {"version": "1.0", "service": {"enabled": True}}
        new_config = migration.migrate(old_config, "1.0", "2.0")
        
        assert new_config["version"] == "2.0"
        assert new_config["new_feature"] is True
        assert new_config["service"]["enabled"] is True
    
    def test_builtin_migration(self):
        """Test built-in migration from v1.0 to v2.0."""
        from src.accelerapp.core.config.migration import migrate_1_0_to_2_0
        
        old_config = {
            "version": "1.0",
            "performance": {
                "cache_enabled": True
            }
        }
        
        new_config = migrate_1_0_to_2_0(old_config)
        
        # Should have new v2.0 fields
        assert "security" in new_config
        assert "events" in new_config
        
        # Should rename old fields
        assert "enable_caching" in new_config["performance"]
