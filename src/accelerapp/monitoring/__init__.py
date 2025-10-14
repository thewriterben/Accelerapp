"""
Monitoring and observability module for Accelerapp.
Provides metrics collection, structured logging, and health checks.
"""

from .metrics import MetricsCollector, get_metrics
from .logging import setup_logging, get_logger
from .health import HealthChecker, HealthStatus, get_health_checker
from .device_health import DeviceHealthMonitor, HealthMetric, get_health_monitor
from .dashboard import MonitoringDashboard, get_dashboard

__all__ = [
    "MetricsCollector",
    "get_metrics",
    "setup_logging",
    "get_logger",
    "HealthChecker",
    "HealthStatus",
    "get_health_checker",
    "DeviceHealthMonitor",
    "HealthMetric",
    "get_health_monitor",
    "MonitoringDashboard",
    "get_dashboard",
]
