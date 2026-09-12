"""
Observability instrumentation for Accelerapp.
Provides OpenTelemetry integration for traces, metrics, and logs.
"""

from .metrics_exporter import PrometheusMetricsExporter, setup_metrics_export
from .tracing import get_tracer, setup_tracing, trace_operation

__all__ = [
    "setup_tracing",
    "get_tracer",
    "trace_operation",
    "setup_metrics_export",
    "PrometheusMetricsExporter",
]
