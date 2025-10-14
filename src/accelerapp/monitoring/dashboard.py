"""
Monitoring Dashboard for Predictive Maintenance.
Provides visualization and alerting capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class MonitoringDashboard:
    """
    Dashboard for monitoring device health and maintenance status.
    Provides data aggregation and alerting capabilities.
    """
    
    def __init__(self):
        """Initialize monitoring dashboard."""
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_channels: Dict[str, Dict[str, Any]] = {}
    
    def add_alert_rule(
        self,
        name: str,
        condition: str,
        severity: str,
        notification_channels: List[str]
    ) -> Dict[str, Any]:
        """
        Add an alert rule.
        
        Args:
            name: Rule name
            condition: Alert condition
            severity: Alert severity
            notification_channels: Channels to notify
        
        Returns:
            Created alert rule
        """
        rule = {
            "id": f"rule-{len(self.alert_rules) + 1}",
            "name": name,
            "condition": condition,
            "severity": severity,
            "notification_channels": notification_channels,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        self.alert_rules.append(rule)
        
        return {
            "status": "success",
            "rule": rule
        }
    
    def trigger_alert(
        self,
        device_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger an alert.
        
        Args:
            device_id: Device identifier
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
            metadata: Additional metadata
        
        Returns:
            Created alert
        """
        alert = {
            "id": f"alert-{len(self.alerts) + 1}",
            "device_id": device_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "status": "active",
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Send notifications based on matching rules
        self._send_notifications(alert)
        
        return {
            "status": "success",
            "alert": alert
        }
    
    def _send_notifications(self, alert: Dict[str, Any]) -> None:
        """Send notifications for an alert."""
        # Find matching rules
        matching_rules = [
            rule for rule in self.alert_rules
            if rule["enabled"] and rule["severity"] == alert["severity"]
        ]
        
        # Simulate sending notifications
        for rule in matching_rules:
            for channel_id in rule["notification_channels"]:
                if channel_id in self.notification_channels:
                    # In a real implementation, this would send actual notifications
                    pass
    
    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert identifier
        
        Returns:
            Updated alert
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                return {
                    "status": "success",
                    "alert": alert
                }
        
        return {
            "status": "error",
            "message": f"Alert {alert_id} not found"
        }
    
    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert identifier
        
        Returns:
            Updated alert
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                return {
                    "status": "success",
                    "alert": alert
                }
        
        return {
            "status": "error",
            "message": f"Alert {alert_id} not found"
        }
    
    def get_active_alerts(
        self,
        device_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active alerts.
        
        Args:
            device_id: Filter by device ID
            severity: Filter by severity
        
        Returns:
            List of active alerts
        """
        alerts = [a for a in self.alerts if a["status"] == "active"]
        
        if device_id:
            alerts = [a for a in alerts if a["device_id"] == device_id]
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        
        return alerts
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get dashboard summary with key metrics.
        
        Returns:
            Dashboard summary
        """
        active_alerts = [a for a in self.alerts if a["status"] == "active"]
        
        # Count by severity
        severity_counts = {
            "critical": sum(1 for a in active_alerts if a["severity"] == "critical"),
            "high": sum(1 for a in active_alerts if a["severity"] == "high"),
            "medium": sum(1 for a in active_alerts if a["severity"] == "medium"),
            "low": sum(1 for a in active_alerts if a["severity"] == "low")
        }
        
        # Count by type
        type_counts = defaultdict(int)
        for alert in active_alerts:
            type_counts[alert["alert_type"]] += 1
        
        # Get recent alerts
        recent_alerts = sorted(
            active_alerts,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:10]
        
        return {
            "status": "success",
            "summary": {
                "total_alerts": len(active_alerts),
                "unacknowledged": sum(1 for a in active_alerts if not a["acknowledged"]),
                "severity_counts": severity_counts,
                "type_counts": dict(type_counts),
                "total_rules": len(self.alert_rules),
                "active_rules": sum(1 for r in self.alert_rules if r["enabled"])
            },
            "recent_alerts": recent_alerts,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_alert_history(
        self,
        time_window: int = 24,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get alert history.
        
        Args:
            time_window: Hours to look back
            device_id: Filter by device ID
        
        Returns:
            Alert history
        """
        cutoff = datetime.now() - timedelta(hours=time_window)
        
        alerts = [
            a for a in self.alerts
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        
        if device_id:
            alerts = [a for a in alerts if a["device_id"] == device_id]
        
        # Calculate statistics
        total_alerts = len(alerts)
        resolved_alerts = sum(1 for a in alerts if a["status"] == "resolved")
        avg_resolution_time = 0
        
        if resolved_alerts > 0:
            resolution_times = []
            for alert in alerts:
                if alert["status"] == "resolved" and "resolved_at" in alert:
                    created = datetime.fromisoformat(alert["timestamp"])
                    resolved = datetime.fromisoformat(alert["resolved_at"])
                    resolution_times.append((resolved - created).total_seconds() / 60)
            
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return {
            "status": "success",
            "time_window_hours": time_window,
            "statistics": {
                "total_alerts": total_alerts,
                "resolved_alerts": resolved_alerts,
                "active_alerts": total_alerts - resolved_alerts,
                "avg_resolution_time_minutes": round(avg_resolution_time, 2)
            },
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    
    def register_notification_channel(
        self,
        channel_id: str,
        channel_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a notification channel.
        
        Args:
            channel_id: Channel identifier
            channel_type: Type (email, slack, webhook, etc.)
            config: Channel configuration
        
        Returns:
            Registration result
        """
        self.notification_channels[channel_id] = {
            "channel_id": channel_id,
            "channel_type": channel_type,
            "config": config,
            "registered_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        return {
            "status": "success",
            "channel": self.notification_channels[channel_id]
        }
    
    def get_widget_data(self, widget_type: str) -> Dict[str, Any]:
        """
        Get data for dashboard widgets.
        
        Args:
            widget_type: Type of widget
        
        Returns:
            Widget data
        """
        if widget_type == "alert_trend":
            return self._get_alert_trend_data()
        elif widget_type == "severity_distribution":
            return self._get_severity_distribution()
        elif widget_type == "top_devices":
            return self._get_top_alert_devices()
        elif widget_type == "resolution_metrics":
            return self._get_resolution_metrics()
        else:
            return {"status": "error", "message": f"Unknown widget type: {widget_type}"}
    
    def _get_alert_trend_data(self) -> Dict[str, Any]:
        """Get alert trend data for the last 7 days."""
        days = 7
        trend_data = []
        
        for i in range(days):
            day_start = datetime.now() - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_alerts = [
                a for a in self.alerts
                if day_start <= datetime.fromisoformat(a["timestamp"]) < day_end
            ]
            
            trend_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": len(day_alerts),
                "critical": sum(1 for a in day_alerts if a["severity"] == "critical"),
                "high": sum(1 for a in day_alerts if a["severity"] == "high")
            })
        
        trend_data.reverse()
        
        return {
            "status": "success",
            "widget_type": "alert_trend",
            "data": trend_data
        }
    
    def _get_severity_distribution(self) -> Dict[str, Any]:
        """Get severity distribution of active alerts."""
        active_alerts = [a for a in self.alerts if a["status"] == "active"]
        
        distribution = {
            "critical": sum(1 for a in active_alerts if a["severity"] == "critical"),
            "high": sum(1 for a in active_alerts if a["severity"] == "high"),
            "medium": sum(1 for a in active_alerts if a["severity"] == "medium"),
            "low": sum(1 for a in active_alerts if a["severity"] == "low")
        }
        
        return {
            "status": "success",
            "widget_type": "severity_distribution",
            "data": distribution
        }
    
    def _get_top_alert_devices(self, limit: int = 10) -> Dict[str, Any]:
        """Get devices with most active alerts."""
        active_alerts = [a for a in self.alerts if a["status"] == "active"]
        
        device_counts = defaultdict(int)
        for alert in active_alerts:
            device_counts[alert["device_id"]] += 1
        
        top_devices = sorted(
            device_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return {
            "status": "success",
            "widget_type": "top_devices",
            "data": [{"device_id": dev, "alert_count": count} for dev, count in top_devices]
        }
    
    def _get_resolution_metrics(self) -> Dict[str, Any]:
        """Get alert resolution metrics."""
        resolved_alerts = [a for a in self.alerts if a["status"] == "resolved"]
        
        if not resolved_alerts:
            return {
                "status": "success",
                "widget_type": "resolution_metrics",
                "data": {
                    "total_resolved": 0,
                    "avg_resolution_time": 0,
                    "fastest_resolution": 0,
                    "slowest_resolution": 0
                }
            }
        
        resolution_times = []
        for alert in resolved_alerts:
            if "resolved_at" in alert:
                created = datetime.fromisoformat(alert["timestamp"])
                resolved = datetime.fromisoformat(alert["resolved_at"])
                resolution_times.append((resolved - created).total_seconds() / 60)
        
        return {
            "status": "success",
            "widget_type": "resolution_metrics",
            "data": {
                "total_resolved": len(resolved_alerts),
                "avg_resolution_time": round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0,
                "fastest_resolution": round(min(resolution_times), 2) if resolution_times else 0,
                "slowest_resolution": round(max(resolution_times), 2) if resolution_times else 0
            }
        }


# Global dashboard instance
_global_dashboard = MonitoringDashboard()


def get_dashboard() -> MonitoringDashboard:
    """
    Get the global monitoring dashboard.
    
    Returns:
        Global dashboard instance
    """
    return _global_dashboard
