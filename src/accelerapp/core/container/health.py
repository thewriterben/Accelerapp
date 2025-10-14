"""
Service health monitoring for Accelerapp v2.0.
Provides health checks and automatic recovery for services.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import asyncio
import time
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check."""
    
    def __init__(
        self,
        status: HealthStatus,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()


class ServiceHealthMonitor:
    """
    Monitors service health and provides recovery mechanisms.
    
    Features:
    - Periodic health checks
    - Configurable health check intervals
    - Automatic recovery attempts
    - Health status history
    """
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize health monitor.
        
        Args:
            check_interval: Interval between health checks in seconds
        """
        self._services: Dict[str, Any] = {}
        self._health_checks: Dict[str, Callable] = {}
        self._health_status: Dict[str, HealthCheckResult] = {}
        self._check_interval = check_interval
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._recovery_callbacks: Dict[str, List[Callable]] = {}
    
    def register_service(
        self,
        name: str,
        service: Any,
        health_check: Optional[Callable] = None,
    ) -> None:
        """
        Register a service for health monitoring.
        
        Args:
            name: Service name
            service: Service instance
            health_check: Optional custom health check function
        """
        self._services[name] = service
        
        if health_check:
            self._health_checks[name] = health_check
        elif hasattr(service, "health_check"):
            self._health_checks[name] = service.health_check
        else:
            # Default health check
            self._health_checks[name] = lambda: self._default_health_check(name)
        
        self._health_status[name] = HealthCheckResult(
            HealthStatus.UNKNOWN,
            "Not yet checked"
        )
        
        logger.info(f"Registered service '{name}' for health monitoring")
    
    def register_recovery_callback(self, name: str, callback: Callable) -> None:
        """
        Register a callback for service recovery.
        
        Args:
            name: Service name
            callback: Recovery callback function
        """
        if name not in self._recovery_callbacks:
            self._recovery_callbacks[name] = []
        self._recovery_callbacks[name].append(callback)
    
    async def check_service_health(self, name: str) -> HealthCheckResult:
        """
        Check the health of a specific service.
        
        Args:
            name: Service name
            
        Returns:
            Health check result
        """
        if name not in self._services:
            return HealthCheckResult(
                HealthStatus.UNKNOWN,
                f"Service '{name}' not registered"
            )
        
        try:
            health_check = self._health_checks[name]
            result = health_check()
            
            # Handle async health checks
            if asyncio.iscoroutine(result):
                result = await result
            
            # Convert boolean results to HealthCheckResult
            if isinstance(result, bool):
                if result:
                    result = HealthCheckResult(HealthStatus.HEALTHY, "Service is healthy")
                else:
                    result = HealthCheckResult(HealthStatus.UNHEALTHY, "Service is unhealthy")
            
            self._health_status[name] = result
            
            # Trigger recovery if unhealthy
            if result.status == HealthStatus.UNHEALTHY:
                await self._attempt_recovery(name)
            
            return result
            
        except Exception as e:
            result = HealthCheckResult(
                HealthStatus.UNHEALTHY,
                f"Health check failed: {e}",
                {"exception": str(e)}
            )
            self._health_status[name] = result
            
            logger.error(f"Health check failed for service '{name}': {e}")
            await self._attempt_recovery(name)
            
            return result
    
    async def check_all_health(self) -> Dict[str, HealthCheckResult]:
        """
        Check health of all registered services.
        
        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}
        for name in self._services:
            results[name] = await self.check_service_health(name)
        return results
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._monitoring:
            logger.warning("Health monitoring is already running")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                await self.check_all_health()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _default_health_check(self, name: str) -> HealthCheckResult:
        """
        Default health check implementation.
        
        Args:
            name: Service name
            
        Returns:
            Health check result
        """
        service = self._services[name]
        
        # Check if service has a basic health method
        if hasattr(service, "is_healthy"):
            is_healthy = service.is_healthy()
            if asyncio.iscoroutine(is_healthy):
                is_healthy = await is_healthy
            
            return HealthCheckResult(
                HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                "Basic health check"
            )
        
        # Default: assume healthy if service exists
        return HealthCheckResult(HealthStatus.HEALTHY, "Service exists")
    
    async def _attempt_recovery(self, name: str) -> None:
        """
        Attempt to recover an unhealthy service.
        
        Args:
            name: Service name
        """
        if name not in self._recovery_callbacks:
            logger.warning(f"No recovery callbacks registered for service '{name}'")
            return
        
        logger.info(f"Attempting recovery for service '{name}'")
        
        for callback in self._recovery_callbacks[name]:
            try:
                result = callback(self._services[name])
                if asyncio.iscoroutine(result):
                    await result
                logger.info(f"Recovery callback executed for service '{name}'")
            except Exception as e:
                logger.error(f"Recovery callback failed for service '{name}': {e}")
    
    def get_health_status(self, name: str) -> Optional[HealthCheckResult]:
        """
        Get the current health status of a service.
        
        Args:
            name: Service name
            
        Returns:
            Health check result or None if not found
        """
        return self._health_status.get(name)
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status of all services.
        
        Returns:
            Dictionary mapping service names to their health status
        """
        return {
            name: {
                "status": result.status.value,
                "message": result.message,
                "details": result.details,
                "timestamp": result.timestamp,
            }
            for name, result in self._health_status.items()
        }
    
    def is_all_healthy(self) -> bool:
        """
        Check if all services are healthy.
        
        Returns:
            True if all services are healthy
        """
        return all(
            result.status == HealthStatus.HEALTHY
            for result in self._health_status.values()
        )
