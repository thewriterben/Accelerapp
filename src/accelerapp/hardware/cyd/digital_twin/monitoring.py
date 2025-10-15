"""
Real-time monitoring for CYD digital twins.

Provides monitoring, alerting, and analytics for CYD devices.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """System alert."""
    level: AlertLevel
    message: str
    device_id: str
    timestamp: datetime
    data: Dict[str, Any]
    acknowledged: bool = False


@dataclass
class Metric:
    """Performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    device_id: str


class CYDMonitor:
    """
    Real-time monitoring for CYD digital twins.
    
    Provides:
    - Real-time state monitoring
    - Performance metrics collection
    - Alerting and notifications
    - Historical data analysis
    - Health check automation
    """

    def __init__(self):
        """Initialize CYD monitor."""
        self._devices: Dict[str, Any] = {}
        self._alerts: List[Alert] = []
        self._metrics: List[Metric] = []
        self._alert_handlers: List[Callable[[Alert], None]] = []
        self._thresholds = self._default_thresholds()

    def _default_thresholds(self) -> Dict[str, Any]:
        """Get default monitoring thresholds."""
        return {
            "temperature_warning": 60.0,
            "temperature_critical": 80.0,
            "power_warning": 300.0,
            "power_critical": 500.0,
            "memory_warning": 50000,
            "memory_critical": 10000,
            "uptime_info": 3600,  # 1 hour
            "uptime_milestone": 86400,  # 24 hours
        }

    def register_device(self, device_id: str, device_data: Dict[str, Any]) -> None:
        """
        Register device for monitoring.
        
        Args:
            device_id: Unique device identifier
            device_data: Device information
        """
        self._devices[device_id] = {
            "id": device_id,
            "registered_at": datetime.now(),
            "last_update": None,
            "data": device_data,
        }

    def unregister_device(self, device_id: str) -> None:
        """
        Unregister device from monitoring.
        
        Args:
            device_id: Device identifier
        """
        if device_id in self._devices:
            del self._devices[device_id]

    def update_device_state(self, device_id: str, state: Dict[str, Any]) -> None:
        """
        Update device state and check for alerts.
        
        Args:
            device_id: Device identifier
            state: Current device state
        """
        if device_id not in self._devices:
            self.register_device(device_id, {})
        
        self._devices[device_id]["last_update"] = datetime.now()
        self._devices[device_id]["data"].update(state)
        
        # Check for alert conditions
        self._check_temperature(device_id, state)
        self._check_power(device_id, state)
        self._check_memory(device_id, state)
        self._check_connectivity(device_id, state)
        
        # Record metrics
        self._record_metrics(device_id, state)

    def _check_temperature(self, device_id: str, state: Dict[str, Any]) -> None:
        """Check temperature thresholds."""
        temp = state.get("temperature_c")
        if temp is None:
            return
        
        if temp >= self._thresholds["temperature_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                f"Critical temperature: {temp}°C",
                device_id,
                {"temperature": temp}
            )
        elif temp >= self._thresholds["temperature_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                f"High temperature: {temp}°C",
                device_id,
                {"temperature": temp}
            )

    def _check_power(self, device_id: str, state: Dict[str, Any]) -> None:
        """Check power consumption thresholds."""
        power = state.get("power_consumption_mw")
        if power is None:
            return
        
        if power >= self._thresholds["power_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                f"Critical power consumption: {power}mW",
                device_id,
                {"power": power}
            )
        elif power >= self._thresholds["power_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                f"High power consumption: {power}mW",
                device_id,
                {"power": power}
            )

    def _check_memory(self, device_id: str, state: Dict[str, Any]) -> None:
        """Check memory thresholds."""
        free_mem = state.get("free_heap_bytes")
        if free_mem is None:
            return
        
        if free_mem <= self._thresholds["memory_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                f"Critical low memory: {free_mem} bytes",
                device_id,
                {"free_memory": free_mem}
            )
        elif free_mem <= self._thresholds["memory_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                f"Low memory: {free_mem} bytes",
                device_id,
                {"free_memory": free_mem}
            )

    def _check_connectivity(self, device_id: str, state: Dict[str, Any]) -> None:
        """Check device connectivity."""
        last_update = self._devices[device_id].get("last_update")
        if not last_update:
            return
        
        elapsed = (datetime.now() - last_update).total_seconds()
        if elapsed > 300:  # 5 minutes
            self._create_alert(
                AlertLevel.WARNING,
                f"Device not responding for {elapsed:.0f} seconds",
                device_id,
                {"elapsed_seconds": elapsed}
            )

    def _record_metrics(self, device_id: str, state: Dict[str, Any]) -> None:
        """Record performance metrics."""
        now = datetime.now()
        
        if "temperature_c" in state:
            self._metrics.append(Metric(
                name="temperature",
                value=state["temperature_c"],
                unit="celsius",
                timestamp=now,
                device_id=device_id,
            ))
        
        if "power_consumption_mw" in state:
            self._metrics.append(Metric(
                name="power_consumption",
                value=state["power_consumption_mw"],
                unit="milliwatts",
                timestamp=now,
                device_id=device_id,
            ))
        
        if "cpu_frequency_mhz" in state:
            self._metrics.append(Metric(
                name="cpu_frequency",
                value=state["cpu_frequency_mhz"],
                unit="megahertz",
                timestamp=now,
                device_id=device_id,
            ))
        
        # Limit metric history
        max_metrics = 10000
        if len(self._metrics) > max_metrics:
            self._metrics = self._metrics[-max_metrics:]

    def _create_alert(
        self,
        level: AlertLevel,
        message: str,
        device_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Create and dispatch alert."""
        alert = Alert(
            level=level,
            message=message,
            device_id=device_id,
            timestamp=datetime.now(),
            data=data,
        )
        
        self._alerts.append(alert)
        
        # Call alert handlers
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")

    def register_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """
        Register alert handler callback.
        
        Args:
            handler: Alert handler function
        """
        self._alert_handlers.append(handler)

    def get_alerts(
        self,
        device_id: Optional[str] = None,
        level: Optional[AlertLevel] = None,
        since: Optional[datetime] = None,
        acknowledged: Optional[bool] = None
    ) -> List[Alert]:
        """
        Get alerts with optional filtering.
        
        Args:
            device_id: Filter by device
            level: Filter by alert level
            since: Filter by timestamp
            acknowledged: Filter by acknowledgment status
            
        Returns:
            List of alerts
        """
        alerts = self._alerts
        
        if device_id:
            alerts = [a for a in alerts if a.device_id == device_id]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if since:
            alerts = [a for a in alerts if a.timestamp >= since]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        return alerts

    def acknowledge_alert(self, alert: Alert) -> None:
        """
        Acknowledge an alert.
        
        Args:
            alert: Alert to acknowledge
        """
        alert.acknowledged = True

    def get_metrics(
        self,
        device_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics with optional filtering.
        
        Args:
            device_id: Filter by device
            metric_name: Filter by metric name
            since: Filter by timestamp
            limit: Maximum number of results
            
        Returns:
            List of metrics
        """
        metrics = self._metrics
        
        if device_id:
            metrics = [m for m in metrics if m.device_id == device_id]
        
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        return metrics[-limit:]

    def get_device_summary(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device monitoring summary.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Summary dictionary or None
        """
        if device_id not in self._devices:
            return None
        
        device = self._devices[device_id]
        
        # Count alerts
        alerts_24h = len(self.get_alerts(
            device_id=device_id,
            since=datetime.now() - timedelta(hours=24)
        ))
        
        unack_alerts = len(self.get_alerts(
            device_id=device_id,
            acknowledged=False
        ))
        
        return {
            "device_id": device_id,
            "registered_at": device["registered_at"].isoformat(),
            "last_update": device["last_update"].isoformat() if device["last_update"] else None,
            "alerts_24h": alerts_24h,
            "unacknowledged_alerts": unack_alerts,
            "current_state": device["data"],
        }

    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get overall system monitoring summary.
        
        Returns:
            System summary dictionary
        """
        total_devices = len(self._devices)
        active_devices = sum(
            1 for d in self._devices.values()
            if d["last_update"] and (datetime.now() - d["last_update"]).total_seconds() < 300
        )
        
        alerts_24h = len(self.get_alerts(since=datetime.now() - timedelta(hours=24)))
        critical_alerts = len(self.get_alerts(level=AlertLevel.CRITICAL, acknowledged=False))
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "inactive_devices": total_devices - active_devices,
            "alerts_24h": alerts_24h,
            "critical_alerts": critical_alerts,
            "total_metrics": len(self._metrics),
        }

    def set_threshold(self, name: str, value: float) -> None:
        """
        Set monitoring threshold.
        
        Args:
            name: Threshold name
            value: Threshold value
        """
        if name in self._thresholds:
            self._thresholds[name] = value

    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get current monitoring thresholds.
        
        Returns:
            Thresholds dictionary
        """
        return self._thresholds.copy()
