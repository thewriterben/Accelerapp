"""
Tests for Phase 2 monitoring and observability.
"""

import logging
import pytest
from accelerapp.monitoring import (
    MetricsCollector,
    get_metrics,
    setup_logging,
    get_logger,
    HealthChecker,
    HealthStatus,
)


class TestMetricsCollector:
    """Test metrics collector."""

    def test_counter(self):
        """Test counter metric."""
        metrics = MetricsCollector()

        counter = metrics.counter("test_counter")
        counter.inc()
        counter.inc(5)

        assert counter.get() == 6

    def test_gauge(self):
        """Test gauge metric."""
        metrics = MetricsCollector()

        gauge = metrics.gauge("test_gauge")
        gauge.set(10.5)
        assert gauge.get() == 10.5

        gauge.inc(2.5)
        assert gauge.get() == 13.0

        gauge.dec(3.0)
        assert gauge.get() == 10.0

    def test_histogram(self):
        """Test histogram metric."""
        metrics = MetricsCollector()

        histogram = metrics.histogram("test_histogram")
        histogram.observe(1.0)
        histogram.observe(2.0)
        histogram.observe(3.0)

        stats = histogram.get()
        assert stats["count"] == 3
        assert stats["sum"] == 6.0
        assert stats["min"] == 1.0
        assert stats["max"] == 3.0
        assert stats["avg"] == 2.0

    def test_get_all_metrics(self):
        """Test getting all metrics."""
        metrics = MetricsCollector()

        metrics.counter("counter1").inc()
        metrics.gauge("gauge1").set(42.0)
        metrics.histogram("hist1").observe(1.0)

        all_metrics = metrics.get_all_metrics()

        assert "counters" in all_metrics
        assert "gauges" in all_metrics
        assert "histograms" in all_metrics
        assert "uptime_seconds" in all_metrics

        assert all_metrics["counters"]["counter1"] == 1
        assert all_metrics["gauges"]["gauge1"] == 42.0

    def test_global_metrics(self):
        """Test global metrics instance."""
        global_metrics = get_metrics()
        assert isinstance(global_metrics, MetricsCollector)


class TestStructuredLogging:
    """Test structured logging."""

    def test_setup_logging(self):
        """Test setting up logging."""
        setup_logging(level="INFO", structured=False)

        logger = logging.getLogger("test")
        assert logger.level <= logging.INFO

    def test_get_logger(self):
        """Test getting logger."""
        logger = get_logger("test_module")

        assert logger is not None
        assert isinstance(logger, logging.Logger) or hasattr(logger, "logger")

    def test_logger_with_correlation_id(self):
        """Test logger with correlation ID."""
        logger = get_logger("test_module", correlation_id="test-123")

        assert logger is not None


class TestHealthChecker:
    """Test health checker."""

    def test_register_health_check(self):
        """Test registering health checks."""
        checker = HealthChecker()

        def healthy_check():
            return True

        checker.register("test_check", healthy_check, critical=True, description="Test check")

        checks = checker.get_registered_checks()
        assert "test_check" in checks

    def test_check_all_healthy(self):
        """Test checking all when all healthy."""
        checker = HealthChecker()

        checker.register("check1", lambda: True, critical=True)
        checker.register("check2", lambda: True, critical=False)

        results = checker.check_all()

        assert results["status"] == HealthStatus.HEALTHY.value
        assert results["total_checks"] == 2
        assert results["failed_checks"] == 0

    def test_check_all_critical_failure(self):
        """Test checking all with critical failure."""
        checker = HealthChecker()

        checker.register("check1", lambda: False, critical=True)
        checker.register("check2", lambda: True, critical=False)

        results = checker.check_all()

        assert results["status"] == HealthStatus.UNHEALTHY.value
        assert results["failed_checks"] == 1

    def test_check_all_degraded(self):
        """Test checking all with non-critical failure."""
        checker = HealthChecker()

        checker.register("check1", lambda: True, critical=True)
        checker.register("check2", lambda: False, critical=False)

        results = checker.check_all()

        assert results["status"] == HealthStatus.DEGRADED.value
        assert results["failed_checks"] == 1

    def test_check_specific(self):
        """Test checking specific health check."""
        checker = HealthChecker()

        checker.register("test_check", lambda: True, critical=True)

        result = checker.check_specific("test_check")

        assert result is not None
        assert result["name"] == "test_check"
        assert result["status"] == HealthStatus.HEALTHY.value

    def test_check_exception_handling(self):
        """Test health check with exception."""
        checker = HealthChecker()

        def failing_check():
            raise Exception("Test error")

        checker.register("failing_check", failing_check, critical=True)

        result = checker.check_specific("failing_check")

        assert result["status"] == HealthStatus.UNHEALTHY.value
        assert "error" in result
