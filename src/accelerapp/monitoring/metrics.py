"""
Metrics collection for Accelerapp.
Provides Prometheus-compatible metrics collection with thread safety.
"""

import threading
import time
from typing import Any, Dict, Optional


class Counter:
    """Thread-safe counter metric."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize counter.

        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self._value = 0
        self._lock = threading.Lock()

    def inc(self, amount: int = 1) -> None:
        """Increment counter."""
        with self._lock:
            self._value += amount

    def get(self) -> int:
        """Get counter value."""
        with self._lock:
            return self._value

    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0


class Gauge:
    """Thread-safe gauge metric."""

    def __init__(self, name: str, description: str = ""):
        """
        Initialize gauge.

        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        """Set gauge value."""
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        """Increment gauge."""
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        """Decrement gauge."""
        with self._lock:
            self._value -= amount

    def get(self) -> float:
        """Get gauge value."""
        with self._lock:
            return self._value


class Histogram:
    """Thread-safe histogram metric with efficient storage."""

    def __init__(self, name: str, description: str = "", max_observations: int = 10000):
        """
        Initialize histogram.

        Args:
            name: Metric name
            description: Metric description
            max_observations: Maximum number of observations to store
        """
        self.name = name
        self.description = description
        self._max_observations = max_observations
        self._observations = []
        self._sum = 0.0
        self._count = 0
        self._min = float("inf")
        self._max = float("-inf")
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        """Record an observation."""
        with self._lock:
            # Keep track of summary stats
            self._sum += value
            self._count += 1
            self._min = min(self._min, value)
            self._max = max(self._max, value)

            # Store observation with limit to prevent memory issues
            if len(self._observations) < self._max_observations:
                self._observations.append(value)
            else:
                # Rotate old observations out (FIFO)
                self._observations.pop(0)
                self._observations.append(value)

    def get(self) -> Dict[str, Any]:
        """Get histogram statistics."""
        with self._lock:
            if self._count == 0:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0,
                }

            return {
                "count": self._count,
                "sum": self._sum,
                "min": self._min if self._min != float("inf") else 0.0,
                "max": self._max if self._max != float("-inf") else 0.0,
                "avg": self._sum / self._count,
            }

    def reset(self) -> None:
        """Reset histogram."""
        with self._lock:
            self._observations.clear()
            self._sum = 0.0
            self._count = 0
            self._min = float("inf")
            self._max = float("-inf")


class MetricsCollector:
    """Thread-safe metrics collector."""

    def __init__(self):
        """Initialize metrics collector."""
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._start_time = time.time()
        self._lock = threading.RLock()

    def counter(self, name: str, description: str = "") -> Counter:
        """
        Get or create a counter metric.

        Args:
            name: Counter name
            description: Counter description

        Returns:
            Counter instance
        """
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, description)
            return self._counters[name]

    def gauge(self, name: str, description: str = "") -> Gauge:
        """
        Get or create a gauge metric.

        Args:
            name: Gauge name
            description: Gauge description

        Returns:
            Gauge instance
        """
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, description)
            return self._gauges[name]

    def histogram(self, name: str, description: str = "") -> Histogram:
        """
        Get or create a histogram metric.

        Args:
            name: Histogram name
            description: Histogram description

        Returns:
            Histogram instance
        """
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, description)
            return self._histograms[name]

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dictionary of all metrics
        """
        with self._lock:
            metrics = {
                "uptime_seconds": time.time() - self._start_time,
                "counters": {name: counter.get() for name, counter in self._counters.items()},
                "gauges": {name: gauge.get() for name, gauge in self._gauges.items()},
                "histograms": {name: hist.get() for name, hist in self._histograms.items()},
            }
        return metrics

    def reset_all(self) -> None:
        """Reset all metrics."""
        with self._lock:
            for counter in self._counters.values():
                counter.reset()
            for histogram in self._histograms.values():
                histogram.reset()
            # Note: Gauges are not reset as they represent current state


# Global metrics collector instance
_global_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """
    Get the global metrics collector.

    Returns:
        Global metrics collector instance
    """
    return _global_metrics
