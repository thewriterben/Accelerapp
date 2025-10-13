"""
API module for Accelerapp.
Provides REST API endpoints for code generation and agent interaction.
"""

from .rate_limiter import RateLimiter, APIKeyManager

# HTTP endpoints are optional
try:
    from .endpoints import CodeGenerationAPI
    __all__ = [
        "CodeGenerationAPI",
        "RateLimiter",
        "APIKeyManager"
    ]
except ImportError:
    __all__ = [
        "RateLimiter",
        "APIKeyManager"
    ]
