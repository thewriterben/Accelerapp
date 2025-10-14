"""
Tests for observability components.
"""

import pytest
from accelerapp.observability import (
    setup_tracing,
    get_tracer,
    trace_operation,
    setup_metrics_export,
    PrometheusMetricsExporter,
)
from accelerapp.monitoring import get_metrics


class TestTracing:
    """Tests for tracing functionality."""
    
    def test_get_tracer(self):
        """Test getting a tracer instance."""
        tracer = get_tracer("test")
        assert tracer is not None
    
    def test_trace_operation_decorator(self):
        """Test trace_operation decorator."""
        @trace_operation("test_operation")
        def sample_function(x, y):
            return x + y
        
        result = sample_function(2, 3)
        assert result == 5
    
    def test_trace_operation_with_exception(self):
        """Test trace_operation with exception."""
        @trace_operation("failing_operation")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
    
    def test_trace_operation_with_kwargs(self):
        """Test trace_operation with keyword arguments."""
        @trace_operation()
        def function_with_kwargs(user_id=None, correlation_id=None):
            return {"user_id": user_id, "correlation_id": correlation_id}
        
        result = function_with_kwargs(user_id=123, correlation_id="req-456")
        assert result["user_id"] == 123
        assert result["correlation_id"] == "req-456"


class TestMetricsExporter:
    """Tests for Prometheus metrics exporter."""
    
    def test_metrics_exporter_initialization(self):
        """Test metrics exporter initialization."""
        exporter = PrometheusMetricsExporter()
        assert exporter is not None
        assert exporter.metrics_collector is not None
    
    def test_generate_prometheus_metrics(self):
        """Test Prometheus metrics generation."""
        metrics = get_metrics()
        
        # Create some test metrics
        counter = metrics.counter("test_counter")
        counter.inc()
        counter.inc()
        
        gauge = metrics.gauge("test_gauge")
        gauge.set(42)
        
        histogram = metrics.histogram("test_histogram")
        histogram.observe(0.5)
        histogram.observe(1.0)
        
        # Generate Prometheus format
        exporter = PrometheusMetricsExporter(metrics)
        output = exporter.generate_prometheus_metrics()
        
        assert "accelerapp_uptime_seconds" in output
        assert "accelerapp_test_counter" in output
        assert "accelerapp_test_gauge 42" in output
        assert "accelerapp_test_histogram" in output
        assert "# TYPE accelerapp_test_counter counter" in output
        assert "# TYPE accelerapp_test_gauge gauge" in output
        assert "# TYPE accelerapp_test_histogram histogram" in output
    
    def test_export_to_file(self, tmp_path):
        """Test exporting metrics to file."""
        metrics = get_metrics()
        counter = metrics.counter("file_counter")
        counter.inc()
        
        exporter = PrometheusMetricsExporter(metrics)
        
        # Export to temporary file
        filepath = tmp_path / "metrics.txt"
        exporter.export_to_file(str(filepath))
        
        # Read and verify
        content = filepath.read_text()
        assert "accelerapp_file_counter" in content
        assert "# TYPE accelerapp_file_counter counter" in content
    
    def test_prometheus_format_structure(self):
        """Test that Prometheus format follows specification."""
        metrics = get_metrics()
        counter = metrics.counter("requests_total")
        counter.inc(5)
        
        exporter = PrometheusMetricsExporter(metrics)
        output = exporter.generate_prometheus_metrics()
        
        lines = output.split('\n')
        
        # Check for HELP and TYPE comments
        help_lines = [l for l in lines if l.startswith("# HELP")]
        type_lines = [l for l in lines if l.startswith("# TYPE")]
        
        assert len(help_lines) > 0
        assert len(type_lines) > 0
        
        # Check for actual metric values
        metric_lines = [l for l in lines if l and not l.startswith("#")]
        assert len(metric_lines) > 0


class TestIntegration:
    """Integration tests for observability components."""
    
    def test_end_to_end_tracing_and_metrics(self):
        """Test complete tracing and metrics flow."""
        # Setup
        metrics = get_metrics()
        
        @trace_operation("integration_test")
        def instrumented_function():
            counter = metrics.counter("integration_counter")
            counter.inc()
            return "success"
        
        # Execute
        result = instrumented_function()
        
        # Verify
        assert result == "success"
        
        # Check metrics
        all_metrics = metrics.get_all_metrics()
        assert "integration_counter" in all_metrics["counters"]
        assert all_metrics["counters"]["integration_counter"] == 1
    
    def test_metrics_exporter_with_real_metrics(self):
        """Test exporter with realistic metrics."""
        metrics = get_metrics()
        
        # Simulate application metrics
        request_counter = metrics.counter("app_requests_total")
        request_counter.inc(100)
        
        error_counter = metrics.counter("app_errors_total")
        error_counter.inc(5)
        
        active_connections = metrics.gauge("app_active_connections")
        active_connections.set(25)
        
        response_time = metrics.histogram("app_response_time_seconds")
        for i in range(10):
            response_time.observe(0.1 * i)
        
        # Export
        exporter = PrometheusMetricsExporter(metrics)
        output = exporter.generate_prometheus_metrics()
        
        # Verify all metrics present
        assert "accelerapp_app_requests_total 100" in output
        assert "accelerapp_app_errors_total 5" in output
        assert "accelerapp_app_active_connections 25" in output
        assert "accelerapp_app_response_time_seconds" in output
