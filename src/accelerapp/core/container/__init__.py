"""
Advanced Dependency Injection Container for Accelerapp v2.0.
Provides enhanced service management with lifecycle control, health monitoring, and AOP support.
"""

from .container import ServiceContainer, ServiceLifecycle
from .health import HealthCheckResult, HealthStatus, ServiceHealthMonitor
from .lifecycle import ILifecycleAware, LifecycleManager, LifecycleState
from .proxies import ServiceProxy, create_proxy, logging_proxy, monitored_proxy, performance_proxy

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
