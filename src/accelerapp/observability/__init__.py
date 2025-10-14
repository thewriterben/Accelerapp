"""
Observability instrumentation for Accelerapp.
Provides OpenTelemetry integration for traces, metrics, and logs.
"""

from .tracing import setup_tracing, get_tracer, trace_operation
from .metrics_exporter import setup_metrics_export, PrometheusMetricsExporter

__all__ = [
    "setup_tracing",
    "get_tracer",
    "trace_operation",
    "setup_metrics_export",
    "PrometheusMetricsExporter",
]
