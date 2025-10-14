"""
Custom exception hierarchy for Accelerapp.
Provides domain-specific exceptions for better error handling.
"""


class AccelerappException(Exception):
    """Base exception for all Accelerapp errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of exception."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigurationError(AccelerappException):
    """Raised when there are configuration issues."""

    pass


class ServiceError(AccelerappException):
    """Raised when a service operation fails."""

    pass


class ValidationError(AccelerappException):
    """Raised when validation fails."""

    pass


class ResourceError(AccelerappException):
    """Raised when resource operations fail."""

    pass


class PluginError(AccelerappException):
    """Raised when plugin operations fail."""

    pass


class CircuitBreakerError(ServiceError):
    """Raised when circuit breaker is open."""

    pass


class RetryExhaustedError(ServiceError):
    """Raised when retry attempts are exhausted."""

    pass


class CacheError(AccelerappException):
    """Raised when cache operations fail."""

    pass


class MonitoringError(AccelerappException):
    """Raised when monitoring operations fail."""

    pass
