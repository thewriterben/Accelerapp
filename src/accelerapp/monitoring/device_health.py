"""
Device Health Monitoring System.
Provides comprehensive health tracking for hardware devices.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict


@dataclass
class HealthMetric:
    """Represents a health metric measurement."""
    
    timestamp: str
    device_id: str
    metric_type: str  # cpu, memory, temperature, disk, network, etc.
    value: float
    unit: str
    status: str  # normal, warning, critical
    metadata: Dict[str, Any]


class DeviceHealthMonitor:
    """
    Monitors and tracks device health metrics.
    Provides real-time health status and historical trends.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize device health monitor.
        
        Args:
            storage_path: Path to store health data
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "device_health"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Store health metrics
        self.metrics: Dict[str, List[HealthMetric]] = defaultdict(list)
        
        # Store device status
        self.device_status: Dict[str, Dict[str, Any]] = {}
        
        # Alert thresholds
        self.thresholds = {
            "cpu_usage": {"warning": 75, "critical": 90},
            "memory_usage": {"warning": 80, "critical": 90},
            "temperature": {"warning": 75, "critical": 85},
            "disk_usage": {"warning": 85, "critical": 95},
        }
        
        self._load_metrics()
    
    def _load_metrics(self) -> None:
        """Load health metrics from storage."""
        metrics_file = self.storage_path / "health_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    for device_id, measurements in data.items():
                        self.metrics[device_id] = [
                            HealthMetric(**m) for m in measurements
                        ]
            except Exception:
                self.metrics = defaultdict(list)
    
    def _save_metrics(self) -> None:
        """Save health metrics to storage."""
        metrics_file = self.storage_path / "health_metrics.json"
        data = {
            device_id: [asdict(m) for m in measurements[-1000:]]  # Keep last 1000 per device
            for device_id, measurements in self.metrics.items()
        }
        with open(metrics_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_metric(
        self,
        device_id: str,
        metric_type: str,
        value: float,
        unit: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a health metric for a device.
        
        Args:
            device_id: Device identifier
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
        
        Returns:
            Recording result with status
        """
        # Determine status based on thresholds
        status = "normal"
        threshold = self.thresholds.get(metric_type)
        
        if threshold:
            if value >= threshold["critical"]:
                status = "critical"
            elif value >= threshold["warning"]:
                status = "warning"
        
        # Create metric
        metric = HealthMetric(
            timestamp=datetime.now().isoformat(),
            device_id=device_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            status=status,
            metadata=metadata or {}
        )
        
        # Store metric
        self.metrics[device_id].append(metric)
        
        # Update device status
        if device_id not in self.device_status:
            self.device_status[device_id] = {
                "last_update": metric.timestamp,
                "metrics": {},
                "overall_status": "healthy"
            }
        
        self.device_status[device_id]["metrics"][metric_type] = {
            "value": value,
            "unit": unit,
            "status": status,
            "timestamp": metric.timestamp
        }
        self.device_status[device_id]["last_update"] = metric.timestamp
        
        # Update overall status
        self._update_overall_status(device_id)
        
        # Save periodically
        if len(self.metrics[device_id]) % 100 == 0:
            self._save_metrics()
        
        return {
            "status": "success",
            "device_id": device_id,
            "metric_type": metric_type,
            "metric_status": status,
            "timestamp": metric.timestamp
        }
    
    def _update_overall_status(self, device_id: str) -> None:
        """Update overall device status based on all metrics."""
        device_metrics = self.device_status[device_id]["metrics"]
        
        # Check for critical status
        if any(m["status"] == "critical" for m in device_metrics.values()):
            self.device_status[device_id]["overall_status"] = "critical"
        elif any(m["status"] == "warning" for m in device_metrics.values()):
            self.device_status[device_id]["overall_status"] = "warning"
        else:
            self.device_status[device_id]["overall_status"] = "healthy"
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get current health status for a device.
        
        Args:
            device_id: Device identifier
        
        Returns:
            Device health status
        """
        if device_id not in self.device_status:
            return {
                "status": "unknown",
                "message": "No health data available for device",
                "device_id": device_id
            }
        
        status = self.device_status[device_id]
        
        return {
            "status": "success",
            "device_id": device_id,
            "overall_status": status["overall_status"],
            "last_update": status["last_update"],
            "metrics": status["metrics"],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metric_history(
        self,
        device_id: str,
        metric_type: Optional[str] = None,
        time_window: Optional[int] = None
    ) -> List[HealthMetric]:
        """
        Get historical metrics for a device.
        
        Args:
            device_id: Device identifier
            metric_type: Filter by metric type
            time_window: Only return metrics from last N hours
        
        Returns:
            List of health metrics
        """
        metrics = self.metrics.get(device_id, [])
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        if time_window:
            cutoff = datetime.now() - timedelta(hours=time_window)
            metrics = [
                m for m in metrics
                if datetime.fromisoformat(m.timestamp) > cutoff
            ]
        
        return metrics
    
    def get_all_devices_status(self) -> Dict[str, Any]:
        """
        Get health status for all monitored devices.
        
        Returns:
            Status for all devices
        """
        devices = []
        
        for device_id, status in self.device_status.items():
            devices.append({
                "device_id": device_id,
                "overall_status": status["overall_status"],
                "last_update": status["last_update"],
                "metric_count": len(status["metrics"])
            })
        
        # Count devices by status
        status_counts = {
            "healthy": sum(1 for d in devices if d["overall_status"] == "healthy"),
            "warning": sum(1 for d in devices if d["overall_status"] == "warning"),
            "critical": sum(1 for d in devices if d["overall_status"] == "critical")
        }
        
        return {
            "status": "success",
            "total_devices": len(devices),
            "status_summary": status_counts,
            "devices": devices,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_alerts(
        self,
        device_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active alerts for devices.
        
        Args:
            device_id: Filter by device ID
            severity: Filter by severity (warning, critical)
        
        Returns:
            List of active alerts
        """
        alerts = []
        
        # Determine which devices to check
        devices_to_check = [device_id] if device_id else list(self.device_status.keys())
        
        for dev_id in devices_to_check:
            if dev_id not in self.device_status:
                continue
            
            metrics = self.device_status[dev_id]["metrics"]
            
            for metric_type, metric_data in metrics.items():
                if metric_data["status"] in ["warning", "critical"]:
                    if severity and metric_data["status"] != severity:
                        continue
                    
                    alerts.append({
                        "device_id": dev_id,
                        "metric_type": metric_type,
                        "severity": metric_data["status"],
                        "value": metric_data["value"],
                        "unit": metric_data["unit"],
                        "timestamp": metric_data["timestamp"],
                        "message": f"{metric_type} is {metric_data['status']}: {metric_data['value']}{metric_data['unit']}"
                    })
        
        # Sort by severity (critical first) and timestamp
        severity_order = {"critical": 0, "warning": 1}
        alerts.sort(key=lambda x: (severity_order.get(x["severity"], 2), x["timestamp"]))
        
        return alerts
    
    def set_threshold(
        self,
        metric_type: str,
        warning: float,
        critical: float
    ) -> Dict[str, Any]:
        """
        Set custom thresholds for a metric type.
        
        Args:
            metric_type: Type of metric
            warning: Warning threshold
            critical: Critical threshold
        
        Returns:
            Result of threshold update
        """
        self.thresholds[metric_type] = {
            "warning": warning,
            "critical": critical
        }
        
        return {
            "status": "success",
            "metric_type": metric_type,
            "thresholds": self.thresholds[metric_type]
        }
    
    def clear_old_metrics(self, days: int = 30) -> int:
        """
        Clear metrics older than specified days.
        
        Args:
            days: Keep metrics from last N days
        
        Returns:
            Number of metrics cleared
        """
        cutoff = datetime.now() - timedelta(days=days)
        cleared_count = 0
        
        for device_id in self.metrics.keys():
            before_count = len(self.metrics[device_id])
            self.metrics[device_id] = [
                m for m in self.metrics[device_id]
                if datetime.fromisoformat(m.timestamp) > cutoff
            ]
            cleared_count += before_count - len(self.metrics[device_id])
        
        self._save_metrics()
        return cleared_count
    
    def export_health_report(
        self,
        device_id: Optional[str] = None,
        time_window: int = 24
    ) -> Dict[str, Any]:
        """
        Export comprehensive health report.
        
        Args:
            device_id: Specific device or None for all
            time_window: Hours to include in report
        
        Returns:
            Health report
        """
        if device_id:
            devices = [device_id]
        else:
            devices = list(self.device_status.keys())
        
        device_reports = []
        
        for dev_id in devices:
            metrics = self.get_metric_history(dev_id, time_window=time_window)
            status = self.get_device_status(dev_id)
            
            # Calculate metric statistics
            metric_stats = defaultdict(lambda: {"min": float("inf"), "max": float("-inf"), "avg": 0, "count": 0})
            
            for metric in metrics:
                stat = metric_stats[metric.metric_type]
                stat["min"] = min(stat["min"], metric.value)
                stat["max"] = max(stat["max"], metric.value)
                stat["avg"] += metric.value
                stat["count"] += 1
            
            # Calculate averages
            for stat in metric_stats.values():
                if stat["count"] > 0:
                    stat["avg"] = stat["avg"] / stat["count"]
            
            device_reports.append({
                "device_id": dev_id,
                "overall_status": status.get("overall_status", "unknown"),
                "total_metrics": len(metrics),
                "metric_statistics": dict(metric_stats),
                "current_metrics": status.get("metrics", {})
            })
        
        return {
            "status": "success",
            "report_type": "health_overview",
            "time_window_hours": time_window,
            "devices_included": len(device_reports),
            "device_reports": device_reports,
            "timestamp": datetime.now().isoformat()
        }


# Global device health monitor instance
_global_health_monitor = DeviceHealthMonitor()


def get_health_monitor() -> DeviceHealthMonitor:
    """
    Get the global device health monitor.
    
    Returns:
        Global health monitor instance
    """
    return _global_health_monitor
