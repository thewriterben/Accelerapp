"""
Circuit breaker pattern implementation for fault tolerance.
"""

import time
import threading
from enum import Enum
from typing import Callable, Optional
from functools import wraps
import logging

from .hierarchy import CircuitBreakerError

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    Features:
    - Automatic state transitions
    - Failure threshold configuration
    - Recovery timeout
    - Success threshold for half-open state
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            success_threshold: Successes needed to close from half-open
            expected_exception: Exception type that triggers circuit
        """
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold
        self._expected_exception = expected_exception
        
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = CircuitState.CLOSED
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._state
    
    def call(self, func: Callable, *args, **kwargs):
        """
        Call function through circuit breaker.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerError(
                        "Circuit breaker is OPEN",
                        {
                            "failure_count": self._failure_count,
                            "last_failure": self._last_failure_time,
                        }
                    )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self._expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("Circuit breaker closed after successful recovery")
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("Circuit breaker reopened after failure in HALF_OPEN state")
            elif self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker opened after {self._failure_count} failures"
                )
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return True
        
        return time.time() - self._last_failure_time >= self._recovery_timeout
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            logger.info("Circuit breaker manually reset")
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
            }


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 2,
    expected_exception: type = Exception,
):
    """
    Decorator for circuit breaker pattern.
    
    Args:
        failure_threshold: Failures before opening circuit
        recovery_timeout: Seconds before attempting recovery
        success_threshold: Successes needed to close circuit
        expected_exception: Exception type that triggers circuit
        
    Returns:
        Decorated function with circuit breaker
    """
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        expected_exception=expected_exception,
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        # Attach breaker for external access
        wrapper.circuit_breaker = breaker
        return wrapper
    
    return decorator
