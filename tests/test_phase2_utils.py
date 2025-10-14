"""
Tests for Phase 2 utility modules.
"""

import asyncio
import time
import pytest
from accelerapp.utils import (
    CacheManager,
    cache_result,
    run_async,
    gather_with_concurrency,
    PerformanceProfiler,
    profile,
)


class TestCacheManager:
    """Test cache manager."""

    def test_cache_set_and_get(self):
        """Test setting and getting values."""
        cache = CacheManager(default_ttl=60)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = CacheManager(default_ttl=1)

        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_cache_deletion(self):
        """Test cache deletion."""
        cache = CacheManager()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.delete("key1")
        assert cache.get("key1") is None

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = CacheManager()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction."""
        cache = CacheManager(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CacheManager(max_size=100, default_ttl=3600)

        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 100
        assert stats["default_ttl"] == 3600

        cache.set("key1", "value1")
        stats = cache.get_stats()
        assert stats["size"] == 1


class TestCacheDecorator:
    """Test cache decorator."""

    def test_cache_decorator(self):
        """Test caching function results."""
        call_count = [0]

        @cache_result(ttl=60)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count[0] == 1  # Function called only once


class TestAsyncUtils:
    """Test async utility functions."""

    @pytest.mark.asyncio
    async def test_run_async(self):
        """Test running sync function in async context."""
        
        def sync_function(x, y):
            return x + y

        result = await run_async(sync_function, 5, 10)
        assert result == 15

    @pytest.mark.asyncio
    async def test_gather_with_concurrency(self):
        """Test gathering tasks with concurrency limit."""
        
        async def task(x):
            await asyncio.sleep(0.1)
            return x * 2

        tasks = [task(i) for i in range(10)]
        results = await gather_with_concurrency(3, *tasks)

        assert len(results) == 10
        assert results[0] == 0
        assert results[9] == 18


class TestPerformanceProfiler:
    """Test performance profiler."""

    def test_record_metric(self):
        """Test recording performance metrics."""
        profiler = PerformanceProfiler()

        profiler.record("test_op", 1.5)
        profiler.record("test_op", 2.0)

        metrics = profiler.get_metrics("test_op")
        assert metrics["count"] == 2
        assert metrics["min_time"] == 1.5
        assert metrics["max_time"] == 2.0
        assert metrics["avg_time"] == 1.75

    def test_measure_context_manager(self):
        """Test measuring with context manager."""
        profiler = PerformanceProfiler()

        with profiler.measure("test_operation"):
            time.sleep(0.1)

        metrics = profiler.get_metrics("test_operation")
        assert metrics["count"] == 1
        assert metrics["total_time"] >= 0.1

    def test_profile_decorator(self):
        """Test profile decorator."""
        
        @profile("decorated_function")
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        assert result == "done"

        # Check that metric was recorded
        from accelerapp.utils.performance import get_profiler
        metrics = get_profiler().get_metrics("decorated_function")
        assert metrics["count"] == 1

    def test_reset_metrics(self):
        """Test resetting metrics."""
        profiler = PerformanceProfiler()

        profiler.record("test_op", 1.0)
        profiler.reset("test_op")

        metrics = profiler.get_metrics("test_op")
        assert metrics == {}

    def test_get_summary(self):
        """Test getting summary of all metrics."""
        profiler = PerformanceProfiler()

        profiler.record("op1", 1.0)
        profiler.record("op2", 2.0)

        summary = profiler.get_summary()
        assert summary["total_operations"] == 2
        assert "metrics" in summary
