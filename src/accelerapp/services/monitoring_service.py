"""
Monitoring and observability service for Accelerapp.
Provides centralized monitoring capabilities.
"""

from typing import Any, Dict, List

from ..core.interfaces import BaseService
from ..monitoring import get_logger, get_metrics, get_health_checker


class MonitoringService(BaseService):
    """Service for monitoring and observability."""

    def __init__(self):
        """Initialize monitoring service."""
        super().__init__("MonitoringService")
        self.logger = get_logger(__name__)
        self.metrics = get_metrics()
        self.health_checker = get_health_checker()

    async def initialize(self) -> None:
        """Initialize the monitoring service."""
        await super().initialize()
        
        # Register default health checks
        self.health_checker.register(
            "monitoring_service",
            lambda: self.is_initialized,
            critical=True,
            description="Monitoring service availability",
        )
        
        self.logger.info("Monitoring service initialized")

    async def shutdown(self) -> None:
        """Shutdown the monitoring service."""
        await super().shutdown()
        self.logger.info("Monitoring service shutdown")

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dictionary of all metrics
        """
        return self.metrics.get_all_metrics()

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status.

        Returns:
            Health check results
        """
        return self.health_checker.check_all()

    def register_health_check(
        self,
        name: str,
        check_func: callable,
        critical: bool = True,
        description: str = "",
    ) -> None:
        """
        Register a custom health check.

        Args:
            name: Check name
            check_func: Function that returns True if healthy
            critical: Whether this is a critical check
            description: Check description
        """
        self.health_checker.register(name, check_func, critical, description)
        self.logger.info(f"Registered health check: {name}")

    def record_metric(self, metric_type: str, name: str, value: Any) -> None:
        """
        Record a metric value.

        Args:
            metric_type: Type of metric (counter, gauge, histogram)
            name: Metric name
            value: Metric value
        """
        if metric_type == "counter":
            self.metrics.counter(name).inc(value)
        elif metric_type == "gauge":
            self.metrics.gauge(name).set(value)
        elif metric_type == "histogram":
            self.metrics.histogram(name).observe(value)

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        health = super().get_health()
        health.update({
            "registered_checks": len(self.health_checker.get_registered_checks()),
        })
        return health
