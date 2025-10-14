"""
Predictive Maintenance Agent for hardware monitoring and failure prediction.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from ..ai.anomaly_detection import AnomalyDetector


class PredictiveMaintenanceAgent(BaseAgent):
    """
    Specialized agent for predictive maintenance.
    Uses ML-based anomaly detection to predict hardware failures.
    """

    def __init__(self):
        """Initialize predictive maintenance agent."""
        capabilities = [
            "anomaly_detection",
            "failure_prediction",
            "health_monitoring",
            "maintenance_scheduling",
            "performance_analysis",
        ]
        super().__init__("Predictive Maintenance Agent", capabilities)
        
        self.anomaly_detector = AnomalyDetector()
        self.maintenance_schedules: Dict[str, List[Dict[str, Any]]] = {}

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle a specific task type."""
        return any(cap in task.lower() for cap in self.capabilities)

    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute predictive maintenance tasks.

        Args:
            spec: Task specification
            context: Additional context

        Returns:
            Task results
        """
        task_type = spec.get("task_type", "monitor")
        
        if task_type == "monitor":
            return self._monitor_device(spec)
        elif task_type == "predict":
            return self._predict_failure(spec)
        elif task_type == "analyze":
            return self._analyze_health(spec)
        elif task_type == "schedule":
            return self._schedule_maintenance(spec)
        elif task_type == "report":
            return self._generate_report(spec)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    def _monitor_device(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor device metrics and detect anomalies.

        Args:
            spec: Monitoring specification

        Returns:
            Monitoring results
        """
        device_id = spec.get("device_id")
        metrics = spec.get("metrics", {})
        
        if not device_id:
            return {"status": "error", "message": "device_id is required"}
        
        detected_anomalies = []
        
        # Check each metric for anomalies
        for metric_name, value in metrics.items():
            anomaly = self.anomaly_detector.detect_anomaly(
                device_id=device_id,
                metric_name=metric_name,
                value=value
            )
            
            if anomaly:
                detected_anomalies.append({
                    "metric": metric_name,
                    "value": value,
                    "expected_range": anomaly.expected_range,
                    "severity": anomaly.severity,
                    "confidence": anomaly.confidence
                })
        
        health_score = self.anomaly_detector.get_device_health_score(device_id)
        
        return {
            "status": "success",
            "device_id": device_id,
            "health_score": health_score,
            "anomalies_detected": len(detected_anomalies),
            "anomalies": detected_anomalies,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

    def _predict_failure(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict potential device failure.

        Args:
            spec: Prediction specification

        Returns:
            Failure prediction
        """
        device_id = spec.get("device_id")
        lookback_hours = spec.get("lookback_hours", 24)
        
        if not device_id:
            return {"status": "error", "message": "device_id is required"}
        
        prediction = self.anomaly_detector.predict_failure(
            device_id=device_id,
            lookback_hours=lookback_hours
        )
        
        # Log the prediction
        self.log_action("failure_prediction", {
            "device_id": device_id,
            "risk_level": prediction["risk_level"],
            "failure_probability": prediction["failure_probability"]
        })
        
        return {
            "status": "success",
            "device_id": device_id,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

    def _analyze_health(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall device health.

        Args:
            spec: Analysis specification

        Returns:
            Health analysis
        """
        device_id = spec.get("device_id")
        time_window = spec.get("time_window", 24)
        
        if not device_id:
            return {"status": "error", "message": "device_id is required"}
        
        # Get recent anomalies
        anomalies = self.anomaly_detector.get_anomalies(
            device_id=device_id,
            time_window=time_window
        )
        
        # Calculate health score
        health_score = self.anomaly_detector.get_device_health_score(device_id)
        
        # Get failure prediction
        prediction = self.anomaly_detector.predict_failure(device_id, time_window)
        
        # Categorize anomalies by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity] += 1
        
        # Generate health status
        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 75:
            health_status = "good"
        elif health_score >= 50:
            health_status = "fair"
        elif health_score >= 25:
            health_status = "poor"
        else:
            health_status = "critical"
        
        return {
            "status": "success",
            "device_id": device_id,
            "health_score": health_score,
            "health_status": health_status,
            "anomaly_summary": severity_counts,
            "total_anomalies": len(anomalies),
            "failure_risk": prediction["risk_level"],
            "recommendations": prediction["recommendations"],
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

    def _schedule_maintenance(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule maintenance based on predictions.

        Args:
            spec: Scheduling specification

        Returns:
            Maintenance schedule
        """
        device_id = spec.get("device_id")
        
        if not device_id:
            return {"status": "error", "message": "device_id is required"}
        
        # Get failure prediction
        prediction = self.anomaly_detector.predict_failure(device_id)
        
        # Determine maintenance schedule based on risk
        risk_level = prediction["risk_level"]
        
        if risk_level == "critical":
            priority = "emergency"
            window = "immediate"
            actions = [
                "Immediate device inspection",
                "Prepare replacement components",
                "Notify maintenance team",
                "Consider temporary shutdown"
            ]
        elif risk_level == "high":
            priority = "urgent"
            window = "24 hours"
            actions = [
                "Schedule maintenance within 24 hours",
                "Order replacement parts",
                "Assign maintenance technician",
                "Monitor continuously"
            ]
        elif risk_level == "medium":
            priority = "normal"
            window = "1 week"
            actions = [
                "Schedule routine maintenance",
                "Review component specifications",
                "Plan resource allocation",
                "Continue monitoring"
            ]
        else:
            priority = "low"
            window = "1 month"
            actions = [
                "Add to routine maintenance schedule",
                "Continue normal operation",
                "Periodic monitoring"
            ]
        
        schedule = {
            "device_id": device_id,
            "priority": priority,
            "maintenance_window": window,
            "actions": actions,
            "risk_level": risk_level,
            "scheduled_date": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Store schedule
        if device_id not in self.maintenance_schedules:
            self.maintenance_schedules[device_id] = []
        self.maintenance_schedules[device_id].append(schedule)
        
        self.log_action("maintenance_scheduled", {
            "device_id": device_id,
            "priority": priority
        })
        
        return {
            "status": "success",
            "schedule": schedule,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

    def _generate_report(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive maintenance report.

        Args:
            spec: Report specification

        Returns:
            Maintenance report
        """
        device_id = spec.get("device_id")
        time_window = spec.get("time_window", 168)  # 1 week default
        
        if device_id:
            # Single device report
            devices = [device_id]
        else:
            # All devices report
            # Get unique device IDs from anomalies
            all_anomalies = self.anomaly_detector.get_anomalies(time_window=time_window)
            devices = list(set(a.device_id for a in all_anomalies))
        
        device_reports = []
        
        for dev_id in devices:
            health_analysis = self._analyze_health({
                "device_id": dev_id,
                "time_window": time_window
            })
            
            device_reports.append({
                "device_id": dev_id,
                "health_score": health_analysis.get("health_score", 0),
                "health_status": health_analysis.get("health_status", "unknown"),
                "anomaly_count": health_analysis.get("total_anomalies", 0),
                "risk_level": health_analysis.get("failure_risk", "unknown"),
                "recommendations": health_analysis.get("recommendations", [])
            })
        
        # Sort by health score (worst first)
        device_reports.sort(key=lambda x: x["health_score"])
        
        # Summary statistics
        total_devices = len(device_reports)
        critical_devices = sum(1 for d in device_reports if d["risk_level"] == "critical")
        high_risk_devices = sum(1 for d in device_reports if d["risk_level"] == "high")
        
        return {
            "status": "success",
            "report_type": "maintenance_overview",
            "time_window_hours": time_window,
            "summary": {
                "total_devices": total_devices,
                "critical_devices": critical_devices,
                "high_risk_devices": high_risk_devices,
                "avg_health_score": sum(d["health_score"] for d in device_reports) / total_devices if total_devices > 0 else 100
            },
            "device_reports": device_reports,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.capabilities

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "predictive_maintenance",
            "capabilities": self.capabilities,
            "version": "1.0.0",
            "description": "Monitors hardware health and predicts failures using ML-based anomaly detection"
        }
