"""
Advanced exception handling system for Accelerapp v2.0.
Provides enhanced error handling with retry, circuit breaker, and recovery mechanisms.
"""

from .circuit_breaker import CircuitBreaker, CircuitState, circuit_breaker
from .handlers import ExceptionHandler, GlobalExceptionHandler, get_global_handler
from .hierarchy import (
    AccelerappException,
    CacheError,
    CircuitBreakerError,
    ConfigurationError,
    ErrorCode,
    EventError,
    MonitoringError,
    PluginError,
    ResourceError,
    RetryExhaustedError,
    ServiceError,
    ValidationError,
)
from .recovery import (
    FallbackStrategy,
    RecoveryManager,
    RecoveryStrategy,
    RestartStrategy,
    RetryStrategy,
)
from .retry import RetryPolicy, retry_with_backoff

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
