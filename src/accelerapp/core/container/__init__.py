"""
Advanced Dependency Injection Container for Accelerapp v2.0.
Provides enhanced service management with lifecycle control, health monitoring, and AOP support.
"""

from .container import ServiceContainer, ServiceLifecycle
from .lifecycle import LifecycleManager
from .health import ServiceHealthMonitor
from .proxies import ServiceProxy, create_proxy

__all__ = [
    "ServiceContainer",
    "ServiceLifecycle",
    "LifecycleManager",
    "ServiceHealthMonitor",
    "ServiceProxy",
    "create_proxy",
]
