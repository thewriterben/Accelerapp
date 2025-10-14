"""
Health check system for Accelerapp.
Provides health status monitoring and reporting.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class HealthStatus(Enum):
    """Health check status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check."""

    def __init__(
        self,
        name: str,
        check_func: Callable[[], bool],
        critical: bool = True,
        description: str = "",
    ):
        """
        Initialize health check.

        Args:
            name: Check name
            check_func: Function that returns True if healthy
            critical: Whether this is a critical check
            description: Check description
        """
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.description = description

    def run(self) -> Dict[str, Any]:
        """
        Run the health check.

        Returns:
            Health check result
        """
        try:
            is_healthy = self.check_func()
            return {
                "name": self.name,
                "status": HealthStatus.HEALTHY.value if is_healthy else HealthStatus.UNHEALTHY.value,
                "critical": self.critical,
                "description": self.description,
            }
        except Exception as e:
            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY.value,
                "critical": self.critical,
                "description": self.description,
                "error": str(e),
            }


class HealthChecker:
    """Manages and executes health checks."""

    def __init__(self):
        """Initialize health checker."""
        self._checks: List[HealthCheck] = []

    def register(
        self,
        name: str,
        check_func: Callable[[], bool],
        critical: bool = True,
        description: str = "",
    ) -> None:
        """
        Register a health check.

        Args:
            name: Check name
            check_func: Function that returns True if healthy
            critical: Whether this is a critical check
            description: Check description
        """
        check = HealthCheck(name, check_func, critical, description)
        self._checks.append(check)

    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Health check results
        """
        results = [check.run() for check in self._checks]

        # Determine overall status
        has_critical_failure = any(
            r["status"] == HealthStatus.UNHEALTHY.value and r["critical"] for r in results
        )
        has_non_critical_failure = any(
            r["status"] == HealthStatus.UNHEALTHY.value and not r["critical"] for r in results
        )

        if has_critical_failure:
            overall_status = HealthStatus.UNHEALTHY
        elif has_non_critical_failure:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            "status": overall_status.value,
            "checks": results,
            "total_checks": len(results),
            "failed_checks": sum(1 for r in results if r["status"] != HealthStatus.HEALTHY.value),
        }

    def check_specific(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Run a specific health check.

        Args:
            name: Check name

        Returns:
            Health check result or None if not found
        """
        for check in self._checks:
            if check.name == name:
                return check.run()
        return None

    def get_registered_checks(self) -> List[str]:
        """
        Get list of registered check names.

        Returns:
            List of check names
        """
        return [check.name for check in self._checks]


# Global health checker instance
_global_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """
    Get the global health checker.

    Returns:
        Global health checker instance
    """
    return _global_health_checker
