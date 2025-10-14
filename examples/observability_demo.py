"""
Observability Demo for Accelerapp.
Demonstrates tracing, metrics, and logging integration.
"""

import time
import random
from accelerapp.monitoring import get_metrics, setup_logging, get_logger
from accelerapp.observability import setup_tracing, trace_operation, get_tracer


def demo_metrics():
    """Demonstrate metrics collection."""
    print("\n=== Metrics Demo ===")
    metrics = get_metrics()
    
    # Counter - for counting events
    print("\n1. Counter Metrics:")
    request_counter = metrics.counter("demo_requests_total", "Total demo requests")
    for i in range(10):
        request_counter.inc()
        print(f"   Request {i+1} counted")
    
    # Gauge - for current state
    print("\n2. Gauge Metrics:")
    connections_gauge = metrics.gauge("demo_active_connections", "Active demo connections")
    for i in range(5):
        connections_gauge.set(i * 2)
        print(f"   Active connections: {i * 2}")
        time.sleep(0.1)
    
    # Histogram - for distributions
    print("\n3. Histogram Metrics:")
    latency_histogram = metrics.histogram("demo_request_duration_seconds", "Request duration")
    for i in range(10):
        duration = random.uniform(0.1, 1.0)
        latency_histogram.observe(duration)
        print(f"   Request duration: {duration:.3f}s")
    
    # Get all metrics
    print("\n4. All Metrics:")
    all_metrics = metrics.get_all_metrics()
    print(f"   Uptime: {all_metrics['uptime_seconds']:.2f}s")
    print(f"   Counters: {len(all_metrics['counters'])}")
    print(f"   Gauges: {len(all_metrics['gauges'])}")
    print(f"   Histograms: {len(all_metrics['histograms'])}")


def demo_logging():
    """Demonstrate structured logging."""
    print("\n=== Logging Demo ===")
    
    # Setup structured logging
    setup_logging(level="INFO", structured=True)
    
    # Get logger with correlation ID
    logger = get_logger(__name__, correlation_id="demo-123")
    
    print("\n1. Basic Logging:")
    logger.info("Demo started")
    logger.debug("This is a debug message")
    logger.warning("This is a warning")
    
    print("\n2. Logging with Extra Fields:")
    logger.info(
        "User action performed",
        extra={
            "extra_fields": {
                "user_id": 456,
                "action": "code_generation",
                "platform": "arduino"
            }
        }
    )
    
    print("\n3. Error Logging:")
    try:
        raise ValueError("Demo error")
    except Exception as e:
        logger.error(f"Error occurred: {e}", extra={"extra_fields": {"error_type": type(e).__name__}})
    
    print("\n✓ Logs sent to configured handlers (console/file/logstash)")


@trace_operation("demo_traced_function")
def traced_function(x: int, y: int, user_id: int = None) -> int:
    """Example function with tracing."""
    time.sleep(0.1)  # Simulate work
    return x + y


@trace_operation("demo_code_generation")
def simulated_code_generation(platform: str, correlation_id: str = None):
    """Simulate code generation with tracing."""
    tracer = get_tracer(__name__)
    
    with tracer.start_as_current_span("validate_platform") as span:
        span.set_attribute("platform", platform)
        time.sleep(0.05)  # Simulate validation
        print(f"   ✓ Platform validated: {platform}")
    
    with tracer.start_as_current_span("generate_code") as span:
        span.set_attribute("platform", platform)
        span.set_attribute("lines_of_code", 150)
        time.sleep(0.1)  # Simulate code generation
        print(f"   ✓ Code generated: 150 lines")
    
    with tracer.start_as_current_span("optimize_code") as span:
        span.set_attribute("optimization_level", "O2")
        time.sleep(0.05)  # Simulate optimization
        print(f"   ✓ Code optimized")
    
    return {"platform": platform, "lines": 150, "status": "success"}


def demo_tracing():
    """Demonstrate distributed tracing."""
    print("\n=== Tracing Demo ===")
    
    # Setup tracing (optional - will use no-op tracer if OpenTelemetry not installed)
    print("\n1. Setting up tracing...")
    try:
        setup_tracing(
            service_name="accelerapp-demo",
            service_version="1.0.0",
            environment="development"
        )
        print("   ✓ Tracing configured")
    except Exception as e:
        print(f"   ⚠ Tracing not available: {e}")
    
    # Simple traced function
    print("\n2. Calling traced function:")
    result = traced_function(10, 20, user_id=123)
    print(f"   Result: {result}")
    
    # Complex traced operation
    print("\n3. Simulating code generation with nested spans:")
    result = simulated_code_generation("arduino", correlation_id="req-789")
    print(f"   Result: {result}")
    
    print("\n✓ Traces sent to configured exporters (Jaeger/OTLP)")


def demo_prometheus_export():
    """Demonstrate Prometheus metrics export."""
    print("\n=== Prometheus Export Demo ===")
    
    from accelerapp.observability import PrometheusMetricsExporter
    
    # Get metrics collector
    metrics = get_metrics()
    
    # Add some demo metrics
    counter = metrics.counter("export_demo_requests")
    counter.inc(42)
    
    gauge = metrics.gauge("export_demo_temperature")
    gauge.set(23.5)
    
    # Create exporter
    exporter = PrometheusMetricsExporter(metrics)
    
    # Generate Prometheus format
    print("\n1. Generated Prometheus Metrics:")
    prom_metrics = exporter.generate_prometheus_metrics()
    
    # Show first few lines
    lines = prom_metrics.split('\n')[:20]
    for line in lines:
        print(f"   {line}")
    print("   ...")
    
    # Export to file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        exporter.export_to_file(f.name)
        print(f"\n2. Metrics exported to: {f.name}")
    
    print("\n✓ Prometheus metrics ready for scraping at /metrics endpoint")


def demo_integrated_workflow():
    """Demonstrate integrated observability."""
    print("\n=== Integrated Workflow Demo ===")
    print("Simulating a complete request with metrics, logs, and traces...\n")
    
    # Setup
    metrics = get_metrics()
    logger = get_logger(__name__, correlation_id="req-workflow-001")
    
    # Track request
    request_counter = metrics.counter("workflow_requests_total")
    request_counter.inc()
    
    active_gauge = metrics.gauge("workflow_active_requests")
    active_gauge.inc()
    
    request_duration = metrics.histogram("workflow_request_duration_seconds")
    
    start_time = time.time()
    
    try:
        # Log request start
        logger.info("Workflow started", extra={"extra_fields": {"workflow_id": "wf-001"}})
        
        # Execute with tracing
        result = simulated_code_generation("esp32", correlation_id="req-workflow-001")
        
        # Log success
        logger.info(
            "Workflow completed successfully",
            extra={
                "extra_fields": {
                    "workflow_id": "wf-001",
                    "platform": result["platform"],
                    "lines_generated": result["lines"]
                }
            }
        )
        
        # Record duration
        duration = time.time() - start_time
        request_duration.observe(duration)
        
        print(f"\n✓ Workflow completed in {duration:.3f}s")
        print(f"  - Metrics: request counted, duration recorded")
        print(f"  - Logs: start and completion logged with correlation ID")
        print(f"  - Traces: distributed trace with 3 spans")
        
    except Exception as e:
        # Log error
        logger.error(f"Workflow failed: {e}", extra={"extra_fields": {"workflow_id": "wf-001"}})
        
        # Count error
        error_counter = metrics.counter("workflow_errors_total")
        error_counter.inc()
        
        raise
    finally:
        # Cleanup
        active_gauge.dec()


def main():
    """Run all observability demos."""
    print("=" * 60)
    print("Accelerapp Observability Demo")
    print("=" * 60)
    
    try:
        # Run demos
        demo_metrics()
        demo_logging()
        demo_tracing()
        demo_prometheus_export()
        demo_integrated_workflow()
        
        print("\n" + "=" * 60)
        print("Demo Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Deploy observability stack:")
        print("   cd deployment/observability")
        print("   docker-compose up -d")
        print("\n2. Access dashboards:")
        print("   - Prometheus: http://localhost:9090")
        print("   - Grafana: http://localhost:3000")
        print("   - Kibana: http://localhost:5601")
        print("   - Jaeger: http://localhost:16686")
        print("\n3. View this demo's metrics:")
        print("   - Query 'demo_' metrics in Prometheus")
        print("   - Search 'correlation_id:demo-123' in Kibana")
        print("   - View traces in Jaeger UI")
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
