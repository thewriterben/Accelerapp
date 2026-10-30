"""
API module for Accelerapp.
Provides REST API endpoints for code generation and agent interaction.
"""

from .rate_limiter import APIKeyManager, RateLimiter

# HTTP endpoints are optional
# Optional dependencies: these names are imported for re-export and are listed
# in __all__ below. That __all__ is assigned (or extended) inside the same
# try/except ImportError guard, and pyflakes only honours a plain top-level
# __all__ -- so it reports these as unused. They are not; hence the markers.
try:
    from .endpoints import CodeGenerationAPI  # noqa: F401

    __all__ = ["CodeGenerationAPI", "RateLimiter", "APIKeyManager"]
except ImportError:
    __all__ = ["RateLimiter", "APIKeyManager"]
