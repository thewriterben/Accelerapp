"""
Core architecture module for Accelerapp v2.0.
Provides fundamental interfaces, dependency injection, configuration management,
exception handling, and event-driven architecture.
"""

# Legacy Phase 1 imports (backward compatible)
from .interfaces import IService, IAgent, IPlugin, IRepository, BaseService
from .dependency_injection import ServiceContainer as LegacyServiceContainer

# Phase 2 enhanced imports (v2.0)
# Configuration Management
try:
    from .config import ConfigurationManager
    from .config import AppConfig, ServiceConfig, PerformanceConfig, MonitoringConfig
except ImportError:
    # Fallback to legacy config if new one doesn't exist
    from .config import ConfigurationManager

# Exception Handling - prefer new, fallback to old
try:
    from .exceptions import (
        ErrorCode,
        AccelerappException,
        ConfigurationError,
        ServiceError,
        ValidationError,
        ResourceError,
        PluginError,
        CircuitBreakerError,
        RetryExhaustedError,
        CacheError,
        MonitoringError,
    )
except ImportError:
    from .exceptions import (
        AccelerappException,
        ConfigurationError,
        ServiceError,
        ValidationError,
        ResourceError,
    )

# Enhanced DI Container (v2.0)
try:
    from .container import ServiceContainer as EnhancedServiceContainer
    from .container import ServiceLifecycle, LifecycleManager, ServiceHealthMonitor
    # Prefer enhanced container, but keep legacy available
    ServiceContainer = EnhancedServiceContainer
except ImportError:
    ServiceContainer = LegacyServiceContainer

# Event-Driven Architecture (v2.0)
try:
    from .events import EventBus, Event, EventStore, Saga, SagaOrchestrator
except ImportError:
    # Events not available in legacy version
    pass

# Import AccelerappCore from the legacy core.py for backward compatibility
import sys
from pathlib import Path

# Get parent directory and import from core.py
parent_dir = Path(__file__).parent.parent
core_module_path = parent_dir / "core.py"
if core_module_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("accelerapp_core_legacy", core_module_path)
    if spec and spec.loader:
        core_legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core_legacy)
        AccelerappCore = core_legacy.AccelerappCore
    else:
        AccelerappCore = None
else:
    AccelerappCore = None

# Backward compatible exports
__all__ = [
    # Interfaces
    "IService",
    "IAgent",
    "IPlugin",
    "IRepository",
    "BaseService",
    # Exceptions
    "AccelerappException",
    "ConfigurationError",
    "ServiceError",
    "ValidationError",
    "ResourceError",
    # Configuration
    "ConfigurationManager",
    # Dependency Injection
    "ServiceContainer",
]

# Add v2.0 exports if available
try:
    __all__.extend([
        # Enhanced Configuration
        "AppConfig",
        "ServiceConfig",
        "PerformanceConfig",
        "MonitoringConfig",
        # Enhanced Exceptions
        "ErrorCode",
        "PluginError",
        "CircuitBreakerError",
        "RetryExhaustedError",
        "CacheError",
        "MonitoringError",
        # Enhanced DI
        "ServiceLifecycle",
        "LifecycleManager",
        "ServiceHealthMonitor",
        # Events
        "EventBus",
        "Event",
        "EventStore",
        "Saga",
        "SagaOrchestrator",
    ])
except NameError:
    pass

if AccelerappCore:
    __all__.append("AccelerappCore")
