"""
Exception handlers and global exception management.
"""

from typing import Any, Callable, Dict, List, Optional, Type
import logging
import traceback

from .hierarchy import AccelerappException

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """
    Handles exceptions with custom logic.
    
    Features:
    - Exception type-specific handlers
    - Fallback handlers
    - Exception logging
    - Context preservation
    """
    
    def __init__(self):
        """Initialize exception handler."""
        self._handlers: Dict[Type[Exception], Callable] = {}
        self._fallback_handler: Optional[Callable] = None
    
    def register(self, exception_type: Type[Exception], handler: Callable) -> None:
        """
        Register a handler for a specific exception type.
        
        Args:
            exception_type: Exception class to handle
            handler: Handler function
        """
        self._handlers[exception_type] = handler
        logger.debug(f"Registered handler for {exception_type.__name__}")
    
    def set_fallback(self, handler: Callable) -> None:
        """
        Set a fallback handler for unregistered exception types.
        
        Args:
            handler: Fallback handler function
        """
        self._fallback_handler = handler
    
    def handle(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Handle an exception.
        
        Args:
            exception: Exception to handle
            context: Optional context information
            
        Returns:
            Handler result
        """
        exception_type = type(exception)
        
        # Find matching handler
        handler = self._handlers.get(exception_type)
        
        if not handler:
            # Try parent classes
            for exc_type, exc_handler in self._handlers.items():
                if isinstance(exception, exc_type):
                    handler = exc_handler
                    break
        
        if handler:
            try:
                return handler(exception, context or {})
            except Exception as e:
                logger.error(f"Exception handler failed: {e}")
        
        # Use fallback handler if available
        if self._fallback_handler:
            try:
                return self._fallback_handler(exception, context or {})
            except Exception as e:
                logger.error(f"Fallback handler failed: {e}")
        
        # Default: log and re-raise
        logger.error(
            f"Unhandled exception: {exception}",
            exc_info=True,
            extra={"context": context}
        )
        raise


class GlobalExceptionHandler:
    """
    Global exception handler singleton.
    
    Features:
    - Centralized exception management
    - Exception aggregation
    - Error reporting
    """
    
    _instance: Optional["GlobalExceptionHandler"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize global exception handler."""
        if self._initialized:
            return
        
        self._handler = ExceptionHandler()
        self._exception_log: List[Dict[str, Any]] = []
        self._max_log_size = 1000
        self._initialized = True
    
    def register_handler(self, exception_type: Type[Exception], handler: Callable) -> None:
        """Register an exception handler."""
        self._handler.register(exception_type, handler)
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Handle an exception globally.
        
        Args:
            exception: Exception to handle
            context: Optional context
            
        Returns:
            Handler result
        """
        # Log exception
        self._log_exception(exception, context)
        
        # Handle exception
        return self._handler.handle(exception, context)
    
    def _log_exception(self, exception: Exception, context: Optional[Dict[str, Any]]) -> None:
        """Log exception to internal log."""
        entry = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }
        
        # Add to exception log
        self._exception_log.append(entry)
        
        # Limit log size
        if len(self._exception_log) > self._max_log_size:
            self._exception_log = self._exception_log[-self._max_log_size:]
    
    def get_recent_exceptions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent exceptions.
        
        Args:
            count: Number of recent exceptions to return
            
        Returns:
            List of exception entries
        """
        return self._exception_log[-count:]
    
    def clear_log(self) -> None:
        """Clear exception log."""
        self._exception_log.clear()


# Global instance
_global_handler = GlobalExceptionHandler()


def get_global_handler() -> GlobalExceptionHandler:
    """Get the global exception handler instance."""
    return _global_handler
