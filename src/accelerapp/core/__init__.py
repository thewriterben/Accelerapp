"""
Core architecture module for Accelerapp v2.0.
Provides fundamental interfaces, dependency injection, configuration management,
exception handling, and event-driven architecture.
"""

from .dependency_injection import ServiceContainer as LegacyServiceContainer

# Legacy Phase 1 imports (backward compatible)
from .interfaces import BaseService, IAgent, IPlugin, IRepository, IService

# Phase 2 enhanced imports (v2.0)
# Configuration Management
#
# The names in these try/except blocks are imported for re-export and are listed
# in `__all__` at the bottom, which is where pyflakes looks to decide that an
# import is used. They used to carry `# noqa: F401` because `__all__` was built
# up inside a `try:` and pyflakes only honours a plain module-level one -- see
# the note on `__all__` below for why that guard turned out to be dead code.
# With a plain list, the markers are unnecessary, and an unnecessary `noqa` is
# worse than none: it suppresses the next real F401 to land on that line.
try:
    from .config import (
        AppConfig,
        ConfigurationManager,
        MonitoringConfig,
        PerformanceConfig,
        ServiceConfig,
    )
except ImportError:
    # Fallback to legacy config if new one doesn't exist
    from .config import ConfigurationManager

# Exception Handling - prefer new, fallback to old
try:
    from .exceptions import (
        AccelerappException,
        CacheError,
        CircuitBreakerError,
        ConfigurationError,
        ErrorCode,
        MonitoringError,
        PluginError,
        ResourceError,
        RetryExhaustedError,
        ServiceError,
        ValidationError,
    )
except ImportError:
    from .exceptions import (
        AccelerappException,
        ConfigurationError,
        ResourceError,
        ServiceError,
        ValidationError,
    )

# Enhanced DI Container (v2.0)
try:
    from .container import LifecycleManager
    from .container import ServiceContainer as EnhancedServiceContainer
    from .container import ServiceHealthMonitor, ServiceLifecycle

    # Prefer enhanced container, but keep legacy available
    ServiceContainer = EnhancedServiceContainer
except ImportError:
    ServiceContainer = LegacyServiceContainer

# Event-Driven Architecture (v2.0)
try:
    from .events import (
        Event,
        EventBus,
        EventStore,
        Saga,
        SagaOrchestrator,
    )
except ImportError:
    # Events not available in legacy version
    pass

# Import AccelerappCore from the legacy core.py for backward compatibility.
#
# `import sys` stood here under a `# noqa: F401`. Nothing in this module uses
# `sys`, and it is not re-exported -- the marker was silencing a genuinely dead
# import rather than protecting a re-export, which is the one case where a noqa
# hides the thing it looks like it is documenting. Deleted.
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

# Backward compatible exports.
#
# One plain top-level list, deliberately. The v2.0 names used to be added by a
# second block:
#
#     try:
#         __all__.extend(["AppConfig", ..., "ServiceLifecycle", ...])
#     except NameError:
#         pass
#
# which read as "export these only if the enhanced modules imported". It never
# did that. The list holds *string literals*, so the extend can no more raise
# NameError than `["a"]` can -- the guard was unreachable and `__all__` was
# extended unconditionally on every path. Folding the two lists together changes
# nothing at runtime and stops pyflakes reporting the re-exported names as
# unused, because it honours a plain module-level `__all__` and not one built up
# inside a `try`.
#
# What this does NOT fix, and did not break: if `.config` or `.container` really
# is absent, these names are in `__all__` and unbound, so `import *` raises
# AttributeError. That was equally true before, for the reason above. It is a
# separate question -- whether the ImportError fallbacks are load-bearing at all
# -- and answering it means knowing whether any deployment ships without them.
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
    # Enhanced Configuration (v2.0)
    "AppConfig",
    "ServiceConfig",
    "PerformanceConfig",
    "MonitoringConfig",
    # Enhanced Exceptions (v2.0)
    "ErrorCode",
    "PluginError",
    "CircuitBreakerError",
    "RetryExhaustedError",
    "CacheError",
    "MonitoringError",
    # Enhanced DI (v2.0)
    "ServiceLifecycle",
    "LifecycleManager",
    "ServiceHealthMonitor",
    # Events (v2.0)
    "EventBus",
    "Event",
    "EventStore",
    "Saga",
    "SagaOrchestrator",
]

if AccelerappCore:
    __all__.append("AccelerappCore")
