"""
Pydantic configuration models for Accelerapp v2.0.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
import os


class ServiceConfig(BaseModel):
    """Service layer configuration."""
    
    enabled: bool = True
    timeout: int = Field(default=30, ge=1, le=300)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    retry_backoff: float = Field(default=1.0, ge=0.1, le=10.0)
    max_concurrent_requests: int = Field(default=10, ge=1, le=1000)
    
    class Config:
        validate_assignment = True


class PerformanceConfig(BaseModel):
    """Performance optimization configuration."""
    
    enable_caching: bool = True
    cache_ttl: int = Field(default=3600, ge=0)
    cache_max_size: int = Field(default=1000, ge=1)
    enable_async: bool = True
    max_workers: int = Field(default=4, ge=1, le=128)
    object_pooling: bool = False
    memory_limit_mb: Optional[int] = Field(default=None, ge=100)
    
    class Config:
        validate_assignment = True


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""
    
    enable_metrics: bool = True
    enable_health_checks: bool = True
    enable_tracing: bool = False
    metrics_port: int = Field(default=8080, ge=1024, le=65535)
    log_level: str = Field(default="INFO")
    structured_logging: bool = True
    log_format: str = "json"
    metrics_export_interval: int = Field(default=60, ge=1)
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        validate_assignment = True


class PluginConfig(BaseModel):
    """Plugin system configuration."""
    
    enabled: bool = True
    plugin_dirs: List[str] = Field(default_factory=lambda: ["plugins"])
    auto_discover: bool = True
    hot_reload: bool = False
    sandboxing: bool = True
    max_plugins: int = Field(default=100, ge=1)
    plugin_timeout: int = Field(default=30, ge=1)
    
    class Config:
        validate_assignment = True


class SecurityConfig(BaseModel):
    """Security configuration."""
    
    enable_encryption: bool = True
    enable_rbac: bool = False
    enable_audit_logging: bool = True
    secret_key: Optional[str] = Field(default=None)
    token_expiry: int = Field(default=3600, ge=300)
    max_login_attempts: int = Field(default=5, ge=1)
    
    class Config:
        validate_assignment = True


class EventConfig(BaseModel):
    """Event system configuration."""
    
    enabled: bool = True
    event_store: str = "memory"
    max_queue_size: int = Field(default=10000, ge=100)
    batch_size: int = Field(default=100, ge=1, le=1000)
    processing_interval: float = Field(default=1.0, ge=0.1)
    enable_event_sourcing: bool = False
    
    class Config:
        validate_assignment = True


class AppConfig(BaseModel):
    """Main application configuration."""
    
    version: str = "2.0.0"
    environment: str = Field(default="development")
    debug: bool = False
    
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    events: EventConfig = Field(default_factory=EventConfig)
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "test"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    class Config:
        validate_assignment = True
        extra = "allow"  # Allow extra fields for extensibility
