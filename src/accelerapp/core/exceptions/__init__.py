"""
Advanced exception handling system for Accelerapp v2.0.
Provides enhanced error handling with retry, circuit breaker, and recovery mechanisms.
"""

from .hierarchy import (
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
    EventError,
)
from .handlers import ExceptionHandler, GlobalExceptionHandler
from .retry import RetryPolicy, retry_with_backoff
from .circuit_breaker import CircuitBreaker, CircuitState
from .recovery import RecoveryStrategy, RecoveryManager

__all__ = [
    # Exceptions
    "AccelerappException",
    "ConfigurationError",
    "ServiceError",
    "ValidationError",
    "ResourceError",
    "PluginError",
    "CircuitBreakerError",
    "RetryExhaustedError",
    "CacheError",
    "MonitoringError",
    "EventError",
    # Handlers
    "ExceptionHandler",
    "GlobalExceptionHandler",
    # Retry
    "RetryPolicy",
    "retry_with_backoff",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    # Recovery
    "RecoveryStrategy",
    "RecoveryManager",
]
