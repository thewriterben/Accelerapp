"""
Enhanced exception hierarchy with error codes and context.
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(Enum):
    """Standard error codes."""
    # Configuration errors (1000-1099)
    CONFIG_INVALID = 1000
    CONFIG_MISSING = 1001
    CONFIG_PARSE_ERROR = 1002
    
    # Service errors (1100-1199)
    SERVICE_UNAVAILABLE = 1100
    SERVICE_TIMEOUT = 1101
    SERVICE_INITIALIZATION_FAILED = 1102
    
    # Validation errors (1200-1299)
    VALIDATION_FAILED = 1200
    INVALID_INPUT = 1201
    SCHEMA_MISMATCH = 1202
    
    # Resource errors (1300-1399)
    RESOURCE_NOT_FOUND = 1300
    RESOURCE_EXHAUSTED = 1301
    RESOURCE_LOCKED = 1302
    
    # Plugin errors (1400-1499)
    PLUGIN_LOAD_FAILED = 1400
    PLUGIN_INITIALIZATION_FAILED = 1401
    PLUGIN_NOT_FOUND = 1402
    
    # Circuit breaker errors (1500-1599)
    CIRCUIT_OPEN = 1500
    CIRCUIT_HALF_OPEN = 1501
    
    # Retry errors (1600-1699)
    RETRY_EXHAUSTED = 1600
    RETRY_TIMEOUT = 1601
    
    # Cache errors (1700-1799)
    CACHE_MISS = 1700
    CACHE_WRITE_FAILED = 1701
    
    # Monitoring errors (1800-1899)
    MONITORING_UNAVAILABLE = 1800
    METRICS_COLLECTION_FAILED = 1801
    
    # Event errors (1900-1999)
    EVENT_PROCESSING_FAILED = 1900
    EVENT_QUEUE_FULL = 1901


class AccelerappException(Exception):
    """
    Base exception for all Accelerapp errors.
    
    Features:
    - Error codes for categorization
    - Context preservation
    - Structured error details
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[ErrorCode] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize exception.
        
        Args:
            message: Error message
            details: Additional error details
            error_code: Optional error code
            cause: Optional underlying exception
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        self.cause = cause
    
    def __str__(self) -> str:
        """String representation of exception."""
        parts = [self.message]
        
        if self.error_code:
            parts.append(f"[Error Code: {self.error_code.value}]")
        
        if self.details:
            parts.append(f"Details: {self.details}")
        
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        
        return " - ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value if self.error_code else None,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(AccelerappException):
    """Raised when there are configuration issues."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.CONFIG_INVALID,
    ):
        super().__init__(message, details, error_code)


class ServiceError(AccelerappException):
    """Raised when a service operation fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE,
    ):
        super().__init__(message, details, error_code)


class ValidationError(AccelerappException):
    """Raised when validation fails."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.VALIDATION_FAILED,
    ):
        super().__init__(message, details, error_code)


class ResourceError(AccelerappException):
    """Raised when resource operations fail."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
    ):
        super().__init__(message, details, error_code)


class PluginError(AccelerappException):
    """Raised when plugin operations fail."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.PLUGIN_LOAD_FAILED,
    ):
        super().__init__(message, details, error_code)


class CircuitBreakerError(ServiceError):
    """Raised when circuit breaker is open."""
    
    def __init__(self, message: str = "Circuit breaker is open", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, ErrorCode.CIRCUIT_OPEN)


class RetryExhaustedError(ServiceError):
    """Raised when retry attempts are exhausted."""
    
    def __init__(self, message: str = "Retry attempts exhausted", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, ErrorCode.RETRY_EXHAUSTED)


class CacheError(AccelerappException):
    """Raised when cache operations fail."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.CACHE_WRITE_FAILED,
    ):
        super().__init__(message, details, error_code)


class MonitoringError(AccelerappException):
    """Raised when monitoring operations fail."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.MONITORING_UNAVAILABLE,
    ):
        super().__init__(message, details, error_code)


class EventError(AccelerappException):
    """Raised when event operations fail."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: ErrorCode = ErrorCode.EVENT_PROCESSING_FAILED,
    ):
        super().__init__(message, details, error_code)
