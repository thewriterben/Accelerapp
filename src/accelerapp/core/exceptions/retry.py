"""
Retry mechanisms with exponential backoff.
"""

import time
import asyncio
from typing import Any, Callable, Optional, Tuple, Type
from functools import wraps
import logging

from .hierarchy import RetryExhaustedError

logger = logging.getLogger(__name__)


class RetryPolicy:
    """
    Defines retry behavior.
    
    Features:
    - Configurable retry attempts
    - Exponential backoff
    - Jitter for distributed systems
    - Exception filtering
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        """
        Initialize retry policy.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add jitter to delays
            retry_on: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on = retry_on or (Exception,)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if should retry
        """
        if attempt >= self.max_attempts:
            return False
        
        return isinstance(exception, self.retry_on)
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry.
        
        Args:
            attempt: Current attempt number
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random())
        
        return delay


def retry_with_backoff(
    policy: Optional[RetryPolicy] = None,
    max_attempts: int = 3,
    base_delay: float = 1.0,
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        policy: Retry policy (if None, creates default policy)
        max_attempts: Maximum retry attempts (used if policy is None)
        base_delay: Base delay in seconds (used if policy is None)
        
    Returns:
        Decorated function with retry logic
    """
    if policy is None:
        policy = RetryPolicy(max_attempts=max_attempts, base_delay=base_delay)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            
            while attempt < policy.max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    
                    if not policy.should_retry(e, attempt):
                        raise
                    
                    if attempt < policy.max_attempts:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt}/{policy.max_attempts} failed for "
                            f"{func.__name__}: {e}. Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
            
            # All retries exhausted
            raise RetryExhaustedError(
                f"Failed after {policy.max_attempts} attempts",
                {"last_exception": str(last_exception)}
            )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            
            while attempt < policy.max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    
                    if not policy.should_retry(e, attempt):
                        raise
                    
                    if attempt < policy.max_attempts:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt}/{policy.max_attempts} failed for "
                            f"{func.__name__}: {e}. Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
            
            # All retries exhausted
            raise RetryExhaustedError(
                f"Failed after {policy.max_attempts} attempts",
                {"last_exception": str(last_exception)}
            )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
