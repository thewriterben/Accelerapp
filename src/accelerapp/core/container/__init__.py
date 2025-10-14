"""
Advanced Dependency Injection Container for Accelerapp v2.0.
Provides enhanced service management with lifecycle control, health monitoring, and AOP support.
"""

from .container import ServiceContainer, ServiceLifecycle
from .lifecycle import LifecycleManager, LifecycleState, ILifecycleAware
from .health import ServiceHealthMonitor, HealthStatus, HealthCheckResult
from .proxies import ServiceProxy, create_proxy, logging_proxy, performance_proxy, monitored_proxy

__all__ = [
    "ServiceContainer",
    "ServiceLifecycle",
    "LifecycleManager",
    "LifecycleState",
    "ILifecycleAware",
    "ServiceHealthMonitor",
    "HealthStatus",
    "HealthCheckResult",
    "ServiceProxy",
    "create_proxy",
    "logging_proxy",
    "performance_proxy",
    "monitored_proxy",
]
