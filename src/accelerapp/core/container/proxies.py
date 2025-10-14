"""
Service proxy creation for aspect-oriented programming (AOP).
Enables cross-cutting concerns like logging, metrics, and caching.
"""

from typing import Any, Callable, Optional
import functools
import time
import logging

logger = logging.getLogger(__name__)


class ServiceProxy:
    """
    Proxy wrapper for services to add cross-cutting concerns.
    
    Features:
    - Method call interception
    - Logging before/after method calls
    - Performance measurement
    - Exception handling
    """
    
    def __init__(
        self,
        target: Any,
        log_calls: bool = False,
        measure_performance: bool = False,
        on_error: Optional[Callable] = None,
    ):
        """
        Initialize service proxy.
        
        Args:
            target: Target service to proxy
            log_calls: Whether to log method calls
            measure_performance: Whether to measure method performance
            on_error: Optional error handler callback
        """
        self._target = target
        self._log_calls = log_calls
        self._measure_performance = measure_performance
        self._on_error = on_error
    
    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access.
        
        Args:
            name: Attribute name
            
        Returns:
            Proxied attribute or method
        """
        attr = getattr(self._target, name)
        
        # If it's a method, wrap it with proxy logic
        if callable(attr):
            return self._create_proxy_method(name, attr)
        
        return attr
    
    def _create_proxy_method(self, name: str, method: Callable) -> Callable:
        """
        Create a proxy method with cross-cutting concerns.
        
        Args:
            name: Method name
            method: Original method
            
        Returns:
            Proxied method
        """
        @functools.wraps(method)
        def proxy_method(*args, **kwargs):
            # Log method call
            if self._log_calls:
                logger.debug(
                    f"Calling {self._target.__class__.__name__}.{name} "
                    f"with args={args}, kwargs={kwargs}"
                )
            
            # Measure performance
            start_time = time.time() if self._measure_performance else None
            
            try:
                # Execute the actual method
                result = method(*args, **kwargs)
                
                # Log success
                if self._log_calls:
                    logger.debug(f"Method {name} completed successfully")
                
                # Log performance
                if self._measure_performance and start_time:
                    duration = time.time() - start_time
                    logger.debug(
                        f"Method {self._target.__class__.__name__}.{name} "
                        f"took {duration:.4f} seconds"
                    )
                
                return result
                
            except Exception as e:
                # Log error
                logger.error(
                    f"Error in {self._target.__class__.__name__}.{name}: {e}"
                )
                
                # Call error handler if provided
                if self._on_error:
                    try:
                        self._on_error(name, e)
                    except Exception as handler_error:
                        logger.error(f"Error handler failed: {handler_error}")
                
                # Re-raise the original exception
                raise
        
        return proxy_method
    
    def get_target(self) -> Any:
        """
        Get the underlying target service.
        
        Returns:
            Target service
        """
        return self._target


def create_proxy(
    target: Any,
    log_calls: bool = False,
    measure_performance: bool = False,
    on_error: Optional[Callable] = None,
) -> ServiceProxy:
    """
    Create a service proxy with specified options.
    
    Args:
        target: Target service to proxy
        log_calls: Whether to log method calls
        measure_performance: Whether to measure method performance
        on_error: Optional error handler callback
        
    Returns:
        Service proxy
    """
    return ServiceProxy(
        target=target,
        log_calls=log_calls,
        measure_performance=measure_performance,
        on_error=on_error,
    )


def logging_proxy(target: Any) -> ServiceProxy:
    """
    Create a proxy with logging enabled.
    
    Args:
        target: Target service
        
    Returns:
        Service proxy with logging
    """
    return create_proxy(target, log_calls=True)


def performance_proxy(target: Any) -> ServiceProxy:
    """
    Create a proxy with performance measurement enabled.
    
    Args:
        target: Target service
        
    Returns:
        Service proxy with performance measurement
    """
    return create_proxy(target, measure_performance=True)


def monitored_proxy(target: Any, on_error: Optional[Callable] = None) -> ServiceProxy:
    """
    Create a fully monitored proxy (logging + performance + error handling).
    
    Args:
        target: Target service
        on_error: Optional error handler callback
        
    Returns:
        Fully monitored service proxy
    """
    return create_proxy(
        target,
        log_calls=True,
        measure_performance=True,
        on_error=on_error,
    )
