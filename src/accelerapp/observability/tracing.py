"""
OpenTelemetry tracing instrumentation for Accelerapp.
"""

import os
from functools import wraps
from typing import Optional, Callable, Any
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None
    TracerProvider = None


def setup_tracing(
    service_name: str = "accelerapp",
    service_version: str = "1.0.0",
    otlp_endpoint: Optional[str] = None,
    jaeger_endpoint: Optional[str] = None,
    environment: str = "production"
) -> None:
    """
    Setup OpenTelemetry tracing for the application.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        otlp_endpoint: OTLP collector endpoint (e.g., 'http://otel-collector:4317')
        jaeger_endpoint: Jaeger agent endpoint (e.g., 'http://jaeger-collector:14268/api/traces')
        environment: Deployment environment (production, staging, development)
    """
    if not OTEL_AVAILABLE:
        print("Warning: OpenTelemetry not installed. Tracing disabled.")
        return
    
    # Use environment variables if endpoints not provided
    if otlp_endpoint is None:
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    
    if jaeger_endpoint is None:
        jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://jaeger-collector:14268/api/traces")
    
    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": environment,
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter if endpoint provided
    if otlp_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            print(f"OpenTelemetry tracing enabled: {otlp_endpoint}")
        except Exception as e:
            print(f"Warning: Failed to setup OTLP exporter: {e}")
    
    # Add Jaeger exporter as fallback
    if jaeger_endpoint:
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_endpoint.split("://")[1].split(":")[0],
                agent_port=14268,
            )
            provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
            print(f"Jaeger tracing enabled: {jaeger_endpoint}")
        except Exception as e:
            print(f"Warning: Failed to setup Jaeger exporter: {e}")
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)


def get_tracer(name: str = __name__) -> Any:
    """
    Get a tracer instance for creating spans.
    
    Args:
        name: Name of the tracer (typically __name__)
        
    Returns:
        Tracer instance
    """
    if not OTEL_AVAILABLE or trace is None:
        # Return a no-op tracer if OpenTelemetry not available
        return NoOpTracer()
    
    return trace.get_tracer(name)


class NoOpTracer:
    """No-op tracer when OpenTelemetry is not available."""
    
    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        """No-op context manager for spans."""
        yield NoOpSpan()


class NoOpSpan:
    """No-op span when OpenTelemetry is not available."""
    
    def set_attribute(self, key: str, value: Any) -> None:
        pass
    
    def set_status(self, status: Any) -> None:
        pass
    
    def record_exception(self, exception: Exception) -> None:
        pass
    
    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        pass


def trace_operation(operation_name: Optional[str] = None):
    """
    Decorator to automatically trace a function/method.
    
    Args:
        operation_name: Name of the operation (uses function name if not provided)
        
    Example:
        @trace_operation("code_generation")
        def generate_code(spec):
            # Your code here
            return result
    """
    def decorator(func: Callable) -> Callable:
        name = operation_name or func.__name__
        tracer = get_tracer(func.__module__)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                # Add function info as attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Add arguments as attributes (be careful with sensitive data)
                if args:
                    span.set_attribute("args.count", len(args))
                if kwargs:
                    span.set_attribute("kwargs.count", len(kwargs))
                    # Add specific kwargs as attributes (customize as needed)
                    for key in ["user_id", "request_id", "correlation_id"]:
                        if key in kwargs:
                            span.set_attribute(key, str(kwargs[key]))
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Mark span as successful
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Record exception
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                    raise
        
        return wrapper
    
    return decorator


@contextmanager
def trace_block(operation_name: str, attributes: Optional[dict] = None):
    """
    Context manager for tracing a block of code.
    
    Args:
        operation_name: Name of the operation
        attributes: Optional attributes to add to the span
        
    Example:
        with trace_block("database_query", {"query": "SELECT * FROM users"}):
            # Your code here
            result = execute_query()
    """
    tracer = get_tracer()
    
    with tracer.start_as_current_span(operation_name) as span:
        # Add custom attributes
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        try:
            yield span
            
            # Mark as successful
            if OTEL_AVAILABLE:
                span.set_status(Status(StatusCode.OK))
                
        except Exception as e:
            # Record exception
            if OTEL_AVAILABLE:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise
