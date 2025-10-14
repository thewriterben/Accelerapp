"""
Advanced exception handling system for Accelerapp v2.0.
Provides enhanced error handling with retry, circuit breaker, and recovery mechanisms.
"""

from .hierarchy import (
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
    EventError,
)
from .handlers import ExceptionHandler, GlobalExceptionHandler, get_global_handler
from .retry import RetryPolicy, retry_with_backoff
from .circuit_breaker import CircuitBreaker, CircuitState, circuit_breaker
from .recovery import RecoveryStrategy, RecoveryManager, RestartStrategy, FallbackStrategy, RetryStrategy

__all__ = [
    # Error codes
    "ErrorCode",
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
    "get_global_handler",
    # Retry
    "RetryPolicy",
    "retry_with_backoff",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "circuit_breaker",
    # Recovery
    "RecoveryStrategy",
    "RecoveryManager",
    "RestartStrategy",
    "FallbackStrategy",
    "RetryStrategy",
]
