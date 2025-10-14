"""
Caching utilities for Accelerapp.
Provides multi-level caching with TTL support.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional


class CacheManager:
    """Multi-level cache manager with TTL support."""

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache manager.

        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum cache size
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            # Expired, remove from cache
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
            return None

        # Update access time
        self._access_times[key] = time.time()
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        # Check if we need to evict old entries
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()

        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl

        self._cache[key] = {"value": value, "expires_at": expires_at}
        self._access_times[key] = time.time()

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._access_times:
            return

        # Find least recently used key
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        self.delete(lru_key)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }


def cache_result(ttl: int = 3600, cache_manager: Optional[CacheManager] = None):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        cache_manager: Cache manager instance (creates new if not provided)

    Returns:
        Decorated function
    """
    cache = cache_manager or CacheManager(default_ttl=ttl)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result

        # Attach cache manager to function for testing/inspection
        wrapper.cache = cache
        return wrapper

    return decorator
