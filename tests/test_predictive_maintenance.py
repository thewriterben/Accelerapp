"""
Tests for predictive maintenance and self-healing agents.
"""

import pytest
from accelerapp.agents import (
    PredictiveMaintenanceAgent,
    SelfHealingAgent,
    FirmwarePatchAgent
)
from accelerapp.ai import AnomalyDetector
from accelerapp.monitoring import DeviceHealthMonitor, MonitoringDashboard


class TestAnomalyDetector:
    """Test anomaly detection functionality."""
    
    def test_anomaly_detector_initialization(self):
        """Test anomaly detector initialization."""
        detector = AnomalyDetector()
        assert detector is not None
        assert detector.window_size > 0
    
    def test_baseline_update(self):
        """Test baseline statistics update."""
        detector = AnomalyDetector()
        
        # Add normal values
        for i in range(10):
            detector.update_baseline("device1", "cpu_usage", 50.0 + i)
        
        # Check baseline was created
        key = "device1:cpu_usage"
        assert key in detector.baselines
        assert "mean" in detector.baselines[key]
        assert "std" in detector.baselines[key]
    
    def test_anomaly_detection(self):
        """Test anomaly detection."""
        detector = AnomalyDetector()
        
        # Create baseline with normal values (with some variance)
        for i in range(50):
            detector.update_baseline("device1", "temperature", 48.0 + i % 5)
        
        # Test normal value (should not trigger)
        anomaly = detector.detect_anomaly("device1", "temperature", 50.0)
        assert anomaly is None
        
        # Test anomalous value (should trigger)
        anomaly = detector.detect_anomaly("device1", "temperature", 100.0)
        assert anomaly is not None
        assert anomaly.severity in ["low", "medium", "high", "critical"]
    
    def test_failure_prediction(self):
        """Test failure prediction."""
        detector = AnomalyDetector()
        
        # Add some anomalies
        for i in range(50):
            detector.update_baseline("device1", "cpu_usage", 50.0)
        
        # Create anomalies
        detector.detect_anomaly("device1", "cpu_usage", 95.0)
        detector.detect_anomaly("device1", "cpu_usage", 98.0)
        
        # Predict failure
        prediction = detector.predict_failure("device1")
        
        assert "risk_level" in prediction
        assert "failure_probability" in prediction
        assert "recommendations" in prediction
        assert isinstance(prediction["recommendations"], list)
    
    def test_health_score_calculation(self):
        """Test health score calculation."""
        detector = AnomalyDetector()
        
        # Test with no history - should be 100
        score = detector.get_device_health_score("device_new")
        assert score == 100.0
        
        # Create baseline (with some variance)
        for i in range(50):
            detector.update_baseline("device1", "cpu_usage", 48.0 + i % 5)
        
        # Create critical anomaly
        anomaly = detector.detect_anomaly("device1", "cpu_usage", 200.0)
        assert anomaly is not None  # Verify anomaly was detected
        
        # Should have lower score after the anomaly
        score = detector.get_device_health_score("device1")
        assert score < 100.0  # Should be reduced


class TestPredictiveMaintenanceAgent:
    """Test predictive maintenance agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = PredictiveMaintenanceAgent()
        assert agent.name == "Predictive Maintenance Agent"
        assert len(agent.capabilities) > 0
        assert "anomaly_detection" in agent.capabilities
    
    def test_monitor_device(self):
        """Test device monitoring."""
        agent = PredictiveMaintenanceAgent()
        
        spec = {
            "task_type": "monitor",
            "device_id": "device1",
            "metrics": {
                "cpu_usage": 75.0,
                "memory_usage": 60.0,
                "temperature": 55.0
            }
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert result["device_id"] == "device1"
        assert "health_score" in result
        assert "anomalies_detected" in result
    
    def test_predict_failure(self):
        """Test failure prediction."""
        agent = PredictiveMaintenanceAgent()
        
        spec = {
            "task_type": "predict",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "prediction" in result
        assert "risk_level" in result["prediction"]
    
    def test_analyze_health(self):
        """Test health analysis."""
        agent = PredictiveMaintenanceAgent()
        
        spec = {
            "task_type": "analyze",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "health_score" in result
        assert "health_status" in result
    
    def test_schedule_maintenance(self):
        """Test maintenance scheduling."""
        agent = PredictiveMaintenanceAgent()
        
        spec = {
            "task_type": "schedule",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "schedule" in result
        assert "priority" in result["schedule"]
    
    def test_generate_report(self):
        """Test report generation."""
        agent = PredictiveMaintenanceAgent()
        
        spec = {
            "task_type": "report",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "device_reports" in result


class TestSelfHealingAgent:
    """Test self-healing agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = SelfHealingAgent()
        assert agent.name == "Self-Healing Agent"
        assert len(agent.capabilities) > 0
        assert "self_diagnosis" in agent.capabilities
    
    def test_diagnose_device(self):
        """Test device diagnosis."""
        agent = SelfHealingAgent()
        
        spec = {
            "task_type": "diagnose",
            "device_id": "device1",
            "symptoms": ["slow performance", "high cpu"],
            "metrics": {
                "cpu_usage": 95.0,
                "memory_usage": 85.0
            }
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "diagnosis" in result
        assert "issues" in result["diagnosis"]
        assert len(result["diagnosis"]["issues"]) > 0
    
    def test_report_health(self):
        """Test health reporting."""
        agent = SelfHealingAgent()
        
        # First diagnose
        agent.generate({
            "task_type": "diagnose",
            "device_id": "device1",
            "symptoms": [],
            "metrics": {}
        })
        
        # Then report
        spec = {
            "task_type": "report_health",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "report" in result
        assert "health_status" in result["report"]
    
    def test_attempt_recovery(self):
        """Test recovery attempt."""
        agent = SelfHealingAgent()
        
        spec = {
            "task_type": "recover",
            "device_id": "device1",
            "issue_type": "memory"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "recovery_actions" in result
        assert len(result["recovery_actions"]) > 0
    
    def test_repair_configuration(self):
        """Test configuration repair."""
        agent = SelfHealingAgent()
        
        spec = {
            "task_type": "repair_config",
            "device_id": "device1",
            "config_type": "network"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "repairs" in result
        assert len(result["repairs"]) > 0
    
    def test_validate_system(self):
        """Test system validation."""
        agent = SelfHealingAgent()
        
        spec = {
            "task_type": "validate",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "validation_result" in result


class TestFirmwarePatchAgent:
    """Test firmware patch agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = FirmwarePatchAgent()
        assert agent.name == "Firmware Patch Agent"
        assert len(agent.capabilities) > 0
        assert "automatic_patching" in agent.capabilities
    
    def test_analyze_patch_needs(self):
        """Test patch needs analysis."""
        agent = FirmwarePatchAgent()
        
        spec = {
            "task_type": "analyze",
            "device_id": "device1",
            "current_version": "1.0.0",
            "analytics": {
                "security_score": 65,
                "crash_count": 10
            }
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "critical_issues" in result
        assert "recommended_patches" in result
    
    def test_apply_patch(self):
        """Test patch application."""
        agent = FirmwarePatchAgent()
        
        # Set initial version
        agent.device_versions["device1"] = "1.0.0"
        
        spec = {
            "task_type": "apply_patch",
            "device_id": "device1",
            "patch_id": "SEC-001",
            "patch_type": "security"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "old_version" in result
        assert "new_version" in result
        assert result["new_version"] != result["old_version"]
    
    def test_check_updates(self):
        """Test update checking."""
        agent = FirmwarePatchAgent()
        agent.device_versions["device1"] = "1.0.0"
        
        spec = {
            "task_type": "check_updates",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "updates_available" in result
        assert "updates" in result
    
    def test_rollback_patch(self):
        """Test patch rollback."""
        agent = FirmwarePatchAgent()
        
        # Apply a patch first
        agent.device_versions["device1"] = "1.0.0"
        agent.generate({
            "task_type": "apply_patch",
            "device_id": "device1",
            "patch_id": "TEST-001"
        })
        
        # Now rollback
        spec = {
            "task_type": "rollback",
            "device_id": "device1"
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert "from_version" in result
        assert "to_version" in result


class TestDeviceHealthMonitor:
    """Test device health monitor."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = DeviceHealthMonitor()
        assert monitor is not None
    
    def test_record_metric(self):
        """Test metric recording."""
        monitor = DeviceHealthMonitor()
        
        result = monitor.record_metric(
            device_id="device1",
            metric_type="cpu_usage",
            value=75.0,
            unit="%"
        )
        
        assert result["status"] == "success"
        assert result["device_id"] == "device1"
    
    def test_get_device_status(self):
        """Test getting device status."""
        monitor = DeviceHealthMonitor()
        
        # Record some metrics
        monitor.record_metric("device1", "cpu_usage", 75.0, "%")
        monitor.record_metric("device1", "memory_usage", 60.0, "%")
        
        status = monitor.get_device_status("device1")
        
        assert status["status"] == "success"
        assert status["device_id"] == "device1"
        assert "metrics" in status
    
    def test_get_alerts(self):
        """Test alert retrieval."""
        monitor = DeviceHealthMonitor()
        
        # Record critical metric
        monitor.record_metric("device1", "cpu_usage", 95.0, "%")
        
        alerts = monitor.get_alerts()
        
        assert len(alerts) > 0
        assert alerts[0]["severity"] in ["warning", "critical"]


class TestMonitoringDashboard:
    """Test monitoring dashboard."""
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        dashboard = MonitoringDashboard()
        assert dashboard is not None
    
    def test_add_alert_rule(self):
        """Test adding alert rule."""
        dashboard = MonitoringDashboard()
        
        result = dashboard.add_alert_rule(
            name="High CPU Alert",
            condition="cpu_usage > 90",
            severity="critical",
            notification_channels=["email"]
        )
        
        assert result["status"] == "success"
        assert "rule" in result
    
    def test_trigger_alert(self):
        """Test triggering alert."""
        dashboard = MonitoringDashboard()
        
        result = dashboard.trigger_alert(
            device_id="device1",
            alert_type="cpu_overload",
            severity="critical",
            message="CPU usage exceeded threshold"
        )
        
        assert result["status"] == "success"
        assert "alert" in result
    
    def test_get_dashboard_summary(self):
        """Test dashboard summary."""
        dashboard = MonitoringDashboard()
        
        # Add some alerts
        dashboard.trigger_alert("device1", "test", "critical", "Test alert")
        
        summary = dashboard.get_dashboard_summary()
        
        assert summary["status"] == "success"
        assert "summary" in summary
        assert "total_alerts" in summary["summary"]
    
    def test_get_widget_data(self):
        """Test widget data retrieval."""
        dashboard = MonitoringDashboard()
        
        result = dashboard.get_widget_data("severity_distribution")
        
        assert result["status"] == "success"
        assert "data" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
