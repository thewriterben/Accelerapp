"""
Performance profiling utilities for Accelerapp.
Provides tools for measuring and optimizing performance.
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional


class PerformanceProfiler:
    """Performance profiler for tracking execution metrics."""

    def __init__(self):
        """Initialize performance profiler."""
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def record(self, name: str, duration: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a performance metric.

        Args:
            name: Metric name
            duration: Execution duration in seconds
            metadata: Additional metadata
        """
        if name not in self._metrics:
            self._metrics[name] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "avg_time": 0.0,
                "metadata": metadata or {},
            }

        metric = self._metrics[name]
        metric["count"] += 1
        metric["total_time"] += duration
        metric["min_time"] = min(metric["min_time"], duration)
        metric["max_time"] = max(metric["max_time"], duration)
        metric["avg_time"] = metric["total_time"] / metric["count"]

    def get_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.

        Args:
            name: Specific metric name (returns all if None)

        Returns:
            Dictionary of metrics
        """
        if name:
            return self._metrics.get(name, {})
        return self._metrics.copy()

    def reset(self, name: Optional[str] = None) -> None:
        """
        Reset metrics.

        Args:
            name: Specific metric to reset (resets all if None)
        """
        if name:
            if name in self._metrics:
                del self._metrics[name]
        else:
            self._metrics.clear()

    @contextmanager
    def measure(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for measuring execution time.

        Args:
            name: Metric name
            metadata: Additional metadata

        Yields:
            None
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.record(name, duration, metadata)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.

        Returns:
            Summary dictionary
        """
        return {
            "total_operations": sum(m["count"] for m in self._metrics.values()),
            "metrics": self._metrics,
        }


# Global profiler instance
_global_profiler = PerformanceProfiler()


def profile(name: Optional[str] = None):
    """
    Decorator to profile function execution.

    Args:
        name: Metric name (uses function name if not provided)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        metric_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with _global_profiler.measure(metric_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_profiler() -> PerformanceProfiler:
    """
    Get the global profiler instance.

    Returns:
        Global performance profiler
    """
    return _global_profiler


@contextmanager
def measure_memory():
    """
    Context manager for measuring memory usage.

    Yields:
        Dictionary with memory statistics
    """
    try:
        import psutil

        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        stats = {"initial_mb": mem_before}

        yield stats

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        stats["final_mb"] = mem_after
        stats["delta_mb"] = mem_after - mem_before

    except ImportError:
        # psutil not available, provide dummy stats
        stats = {"error": "psutil not installed"}
        yield stats
