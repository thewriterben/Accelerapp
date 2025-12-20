"""
Caching utilities for Accelerapp.
Provides multi-level caching with TTL support and performance optimizations.
"""

import threading
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple


class CacheManager:
    """Multi-level cache manager with TTL support and performance tracking."""

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
        self._lock = threading.RLock()

        # Performance tracking
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                # Expired, remove from cache
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                self._misses += 1
                return None

            # Update access time
            self._access_times[key] = time.time()
            self._hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        with self._lock:
            # Check if we need to evict old entries
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl

            self._cache[key] = {"value": value, "expires_at": expires_at}
            self._access_times[key] = time.time()

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or compute and store it.

        Args:
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time-to-live in seconds

        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        # Compute and cache the value
        value = factory()
        self.set(key, value, ttl)
        return value

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of found key-value pairs
        """
        results = {}
        current_time = time.time()
        with self._lock:
            for key in keys:
                if key not in self._cache:
                    self._misses += 1
                    continue

                entry = self._cache[key]
                if current_time > entry["expires_at"]:
                    # Expired, remove from cache
                    del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
                    self._misses += 1
                    continue

                # Update access time
                self._access_times[key] = current_time
                self._hits += 1
                results[key] = entry["value"]
        return results

    def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """
        Set multiple values in cache.

        Args:
            items: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
        """
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl_seconds
        with self._lock:
            for key, value in items.items():
                # Check if we need to evict old entries
                if len(self._cache) >= self.max_size and key not in self._cache:
                    self._evict_lru()

                self._cache[key] = {"value": value, "expires_at": expires_at}
                self._access_times[key] = time.time()

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        with self._lock:
            existed = key in self._cache
            if existed:
                del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
            return existed

    def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        deleted = 0
        with self._lock:
            for key in keys:
                if self.delete(key):
                    deleted += 1
        return deleted

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        removed = 0
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                removed += 1
        return removed

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
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._hits = 0
            self._misses = 0

    def contains(self, key: str) -> bool:
        """
        Check if key exists in cache (and is not expired).

        Args:
            key: Cache key

        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            if key not in self._cache:
                return False
            entry = self._cache[key]
            return time.time() <= entry["expires_at"]

    def keys(self) -> List[str]:
        """
        Get all valid (non-expired) keys.

        Returns:
            List of valid cache keys
        """
        current_time = time.time()
        with self._lock:
            return [
                key for key, entry in self._cache.items()
                if current_time <= entry["expires_at"]
            ]


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
