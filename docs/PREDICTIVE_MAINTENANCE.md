# Predictive Maintenance and Self-Healing Agents

## Overview

This module provides comprehensive predictive maintenance and self-healing capabilities for hardware deployments. It includes ML-based anomaly detection, automatic firmware patching, device self-diagnosis, and monitoring dashboards.

## Features

### 1. Anomaly Detection (ML-Based)
- Statistical anomaly detection using online learning
- Adaptive baseline thresholds
- Early hardware failure prediction
- Confidence scoring for anomalies

### 2. Predictive Maintenance Agent
- Real-time device health monitoring
- Failure risk prediction
- Maintenance scheduling automation
- Comprehensive health reporting

### 3. Self-Healing Agent
- Automatic device self-diagnosis
- Health status reporting
- Automatic recovery from common issues
- Configuration repair capabilities

### 4. Firmware Patch Agent
- Analytics-based patch analysis
- Automatic firmware updates
- Rollback support
- Patch validation

### 5. Device Health Monitoring
- Real-time metric tracking
- Alert generation
- Historical trend analysis
- Health score calculation

### 6. Monitoring Dashboard
- Visual monitoring interface
- Alert management
- Notification system
- Analytics widgets

## Installation

The predictive maintenance module is included with Accelerapp. No additional installation is required.

```bash
pip install accelerapp
```

## Quick Start

### Basic Device Monitoring

```python
from accelerapp.agents import PredictiveMaintenanceAgent
from accelerapp.monitoring import get_health_monitor

# Initialize monitoring
agent = PredictiveMaintenanceAgent()
health_monitor = get_health_monitor()

# Record device metrics
health_monitor.record_metric(
    device_id="device001",
    metric_type="cpu_usage",
    value=75.0,
    unit="%"
)

health_monitor.record_metric(
    device_id="device001",
    metric_type="temperature",
    value=65.0,
    unit="°C"
)

# Monitor device and detect anomalies
result = agent.generate({
    "task_type": "monitor",
    "device_id": "device001",
    "metrics": {
        "cpu_usage": 75.0,
        "memory_usage": 60.0,
        "temperature": 65.0
    }
})

print(f"Health Score: {result['health_score']}")
print(f"Anomalies Detected: {result['anomalies_detected']}")
```

## Detailed Usage Examples

### 1. Anomaly Detection

```python
from accelerapp.ai import AnomalyDetector

# Initialize detector
detector = AnomalyDetector()

# Build baseline with normal values
for value in range(100):
    detector.update_baseline("device001", "cpu_usage", 45.0 + value % 10)

# Detect anomalies in new measurements
anomaly = detector.detect_anomaly(
    device_id="device001",
    metric_name="cpu_usage",
    value=95.0  # Anomalous value
)

if anomaly:
    print(f"Anomaly detected!")
    print(f"Severity: {anomaly.severity}")
    print(f"Confidence: {anomaly.confidence}")
    print(f"Expected range: {anomaly.expected_range}")

# Predict failure risk
prediction = detector.predict_failure("device001", lookback_hours=24)
print(f"Risk Level: {prediction['risk_level']}")
print(f"Failure Probability: {prediction['failure_probability']:.2%}")
print(f"Recommendations: {prediction['recommendations']}")
```

### 2. Predictive Maintenance

```python
from accelerapp.agents import PredictiveMaintenanceAgent

agent = PredictiveMaintenanceAgent()

# Predict potential failures
prediction_result = agent.generate({
    "task_type": "predict",
    "device_id": "device001",
    "lookback_hours": 24
})

print(f"Failure Risk: {prediction_result['prediction']['risk_level']}")
print(f"Recommendations:")
for rec in prediction_result['prediction']['recommendations']:
    print(f"  - {rec}")

# Analyze device health
health_result = agent.generate({
    "task_type": "analyze",
    "device_id": "device001",
    "time_window": 24
})

print(f"Health Score: {health_result['health_score']}/100")
print(f"Health Status: {health_result['health_status']}")

# Schedule maintenance based on predictions
schedule_result = agent.generate({
    "task_type": "schedule",
    "device_id": "device001"
})

print(f"Maintenance Priority: {schedule_result['schedule']['priority']}")
print(f"Maintenance Window: {schedule_result['schedule']['maintenance_window']}")
print("Actions to take:")
for action in schedule_result['schedule']['actions']:
    print(f"  - {action}")

# Generate comprehensive report
report_result = agent.generate({
    "task_type": "report",
    "device_id": "device001",
    "time_window": 168  # 1 week
})

print(f"Total Devices: {report_result['summary']['total_devices']}")
print(f"Critical Devices: {report_result['summary']['critical_devices']}")
print(f"Average Health Score: {report_result['summary']['avg_health_score']:.1f}")
```

### 3. Self-Healing

```python
from accelerapp.agents import SelfHealingAgent

agent = SelfHealingAgent()

# Diagnose device issues
diagnosis_result = agent.generate({
    "task_type": "diagnose",
    "device_id": "device001",
    "symptoms": ["slow performance", "high memory usage"],
    "metrics": {
        "cpu_usage": 85.0,
        "memory_usage": 92.0,
        "temperature": 75.0
    }
})

print(f"Overall Severity: {diagnosis_result['diagnosis']['severity']}")
print("Issues detected:")
for issue in diagnosis_result['diagnosis']['issues']:
    print(f"  - Type: {issue['type']}")
    print(f"    Description: {issue['description']}")
    print(f"    Severity: {issue['severity']}")
    print(f"    Auto-recoverable: {issue['auto_recoverable']}")

print("\nRecommendations:")
for rec in diagnosis_result['diagnosis']['recommendations']:
    print(f"  - {rec}")

# Attempt automatic recovery
recovery_result = agent.generate({
    "task_type": "recover",
    "device_id": "device001",
    "issue_type": "memory"
})

print("\nRecovery actions taken:")
for action in recovery_result['recovery_actions']:
    print(f"  - {action['description']}")

# Repair configuration
repair_result = agent.generate({
    "task_type": "repair_config",
    "device_id": "device001",
    "config_type": "network"
})

print("\nConfiguration repairs:")
for repair in repair_result['repairs']:
    print(f"  - {repair['item']}: {repair['action']} - {repair['status']}")

# Validate system after recovery
validation_result = agent.generate({
    "task_type": "validate",
    "device_id": "device001"
})

print(f"\nValidation Result: {validation_result['validation_result']}")
```

### 4. Firmware Patching

```python
from accelerapp.agents import FirmwarePatchAgent

agent = FirmwarePatchAgent()

# Analyze patch needs based on device analytics
analysis_result = agent.generate({
    "task_type": "analyze",
    "device_id": "device001",
    "current_version": "1.0.0",
    "analytics": {
        "security_score": 65,
        "crash_count": 10,
        "performance_score": 55
    }
})

print(f"Current Version: {analysis_result['current_version']}")
print(f"Critical Issues: {analysis_result['critical_issues']}")
print("\nRecommended Patches:")
for patch in analysis_result['recommended_patches']:
    print(f"  - {patch['patch_id']}: {patch['description']}")
    print(f"    Type: {patch['type']}, Priority: {patch['priority']}")

# Check for available updates
updates_result = agent.generate({
    "task_type": "check_updates",
    "device_id": "device001",
    "device_type": "esp32"
})

print(f"\nUpdates Available: {updates_result['updates_available']}")
for update in updates_result['updates']:
    print(f"  - Version {update['version']}")
    print(f"    Type: {update['type']}, Priority: {update['priority']}")
    print(f"    Size: {update['size_kb']} KB")

# Apply a patch
patch_result = agent.generate({
    "task_type": "apply_patch",
    "device_id": "device001",
    "patch_id": "SEC-20250101-001",
    "patch_type": "security",
    "auto_rollback": True
})

print(f"\nPatch Applied:")
print(f"  Old Version: {patch_result['old_version']}")
print(f"  New Version: {patch_result['new_version']}")
print("  Stages:")
for stage in patch_result['stages']:
    print(f"    - {stage['stage']}: {stage['status']}")

# Validate patch
validation_result = agent.generate({
    "task_type": "validate",
    "device_id": "device001"
})

print(f"\nPatch Validation: {validation_result['validation_result']}")

# Rollback if needed
if validation_result['validation_result'] == 'failed':
    rollback_result = agent.generate({
        "task_type": "rollback",
        "device_id": "device001"
    })
    print(f"Rolled back to version: {rollback_result['to_version']}")
```

### 5. Device Health Monitoring

```python
from accelerapp.monitoring import get_health_monitor

monitor = get_health_monitor()

# Set custom thresholds
monitor.set_threshold("cpu_usage", warning=70, critical=85)
monitor.set_threshold("temperature", warning=70, critical=80)

# Record multiple metrics
metrics = {
    "cpu_usage": 82.0,
    "memory_usage": 75.0,
    "temperature": 68.0,
    "disk_usage": 65.0
}

for metric_type, value in metrics.items():
    monitor.record_metric(
        device_id="device001",
        metric_type=metric_type,
        value=value,
        unit="%" if metric_type != "temperature" else "°C"
    )

# Get device status
status = monitor.get_device_status("device001")
print(f"Overall Status: {status['overall_status']}")
print(f"Last Update: {status['last_update']}")
print("\nMetrics:")
for metric, data in status['metrics'].items():
    print(f"  {metric}: {data['value']}{data['unit']} - {data['status']}")

# Get alerts
alerts = monitor.get_alerts(severity="critical")
print(f"\nCritical Alerts: {len(alerts)}")
for alert in alerts:
    print(f"  - {alert['device_id']}: {alert['message']}")

# Get all devices status
all_status = monitor.get_all_devices_status()
print(f"\nTotal Devices: {all_status['total_devices']}")
print(f"Status Summary: {all_status['status_summary']}")

# Export health report
report = monitor.export_health_report(time_window=24)
print(f"\nDevices in Report: {report['devices_included']}")
for device_report in report['device_reports']:
    print(f"  {device_report['device_id']}: {device_report['overall_status']}")
```

### 6. Monitoring Dashboard

```python
from accelerapp.monitoring import get_dashboard

dashboard = get_dashboard()

# Add alert rules
dashboard.add_alert_rule(
    name="Critical CPU Alert",
    condition="cpu_usage > 90",
    severity="critical",
    notification_channels=["email", "slack"]
)

dashboard.add_alert_rule(
    name="High Temperature Alert",
    condition="temperature > 80",
    severity="high",
    notification_channels=["email"]
)

# Trigger alerts (usually done automatically by monitoring system)
dashboard.trigger_alert(
    device_id="device001",
    alert_type="cpu_overload",
    severity="critical",
    message="CPU usage exceeded 90% threshold",
    metadata={"value": 95.0, "threshold": 90.0}
)

# Get dashboard summary
summary = dashboard.get_dashboard_summary()
print("Dashboard Summary:")
print(f"  Total Alerts: {summary['summary']['total_alerts']}")
print(f"  Unacknowledged: {summary['summary']['unacknowledged']}")
print(f"  Severity Breakdown: {summary['summary']['severity_counts']}")

# Get active alerts
active_alerts = dashboard.get_active_alerts()
for alert in active_alerts:
    print(f"\nAlert: {alert['alert_type']}")
    print(f"  Device: {alert['device_id']}")
    print(f"  Severity: {alert['severity']}")
    print(f"  Message: {alert['message']}")
    print(f"  Acknowledged: {alert['acknowledged']}")

# Acknowledge an alert
if active_alerts:
    dashboard.acknowledge_alert(active_alerts[0]['id'])

# Get widget data for visualization
trend_data = dashboard.get_widget_data("alert_trend")
severity_dist = dashboard.get_widget_data("severity_distribution")
top_devices = dashboard.get_widget_data("top_devices")

print("\nAlert Trend (Last 7 Days):")
for day_data in trend_data['data']:
    print(f"  {day_data['date']}: {day_data['count']} alerts")

# Register notification channel
dashboard.register_notification_channel(
    channel_id="email-ops",
    channel_type="email",
    config={"recipients": ["ops@example.com"]}
)
```

## Integration Example

### Complete Monitoring Pipeline

```python
from accelerapp.agents import (
    PredictiveMaintenanceAgent,
    SelfHealingAgent,
    FirmwarePatchAgent
)
from accelerapp.monitoring import get_health_monitor, get_dashboard
from accelerapp.ai import AnomalyDetector

# Initialize components
pred_agent = PredictiveMaintenanceAgent()
heal_agent = SelfHealingAgent()
patch_agent = FirmwarePatchAgent()
health_monitor = get_health_monitor()
dashboard = get_dashboard()

# Monitor device
device_id = "device001"
metrics = {
    "cpu_usage": 88.0,
    "memory_usage": 85.0,
    "temperature": 78.0,
    "disk_usage": 70.0
}

# 1. Record metrics
for metric_type, value in metrics.items():
    health_monitor.record_metric(device_id, metric_type, value, "%")

# 2. Check for anomalies
monitor_result = pred_agent.generate({
    "task_type": "monitor",
    "device_id": device_id,
    "metrics": metrics
})

if monitor_result['anomalies_detected'] > 0:
    print(f"⚠️  Anomalies detected: {monitor_result['anomalies_detected']}")
    
    # Trigger dashboard alert
    dashboard.trigger_alert(
        device_id=device_id,
        alert_type="anomaly_detected",
        severity="high",
        message=f"{monitor_result['anomalies_detected']} anomalies detected"
    )

# 3. Predict failures
prediction_result = pred_agent.generate({
    "task_type": "predict",
    "device_id": device_id
})

risk_level = prediction_result['prediction']['risk_level']
print(f"Risk Level: {risk_level}")

if risk_level in ["high", "critical"]:
    # 4. Diagnose issues
    diagnosis = heal_agent.generate({
        "task_type": "diagnose",
        "device_id": device_id,
        "symptoms": ["high resource usage"],
        "metrics": metrics
    })
    
    # 5. Attempt automatic recovery for recoverable issues
    for issue in diagnosis['diagnosis']['issues']:
        if issue['auto_recoverable']:
            recovery = heal_agent.generate({
                "task_type": "recover",
                "device_id": device_id,
                "issue_type": issue['type']
            })
            print(f"Recovery attempted for {issue['type']}")
    
    # 6. Schedule maintenance
    schedule = pred_agent.generate({
        "task_type": "schedule",
        "device_id": device_id
    })
    print(f"Maintenance scheduled: {schedule['schedule']['priority']}")

# 7. Check for firmware updates
if risk_level == "critical":
    updates = patch_agent.generate({
        "task_type": "check_updates",
        "device_id": device_id
    })
    
    if updates['updates_available'] > 0:
        # Apply critical patches
        critical_updates = [u for u in updates['updates'] if u['priority'] == 'critical']
        for update in critical_updates:
            patch_agent.generate({
                "task_type": "apply_patch",
                "device_id": device_id,
                "patch_id": update['type'] + "-001",
                "patch_type": update['type']
            })

# 8. Generate comprehensive report
report = pred_agent.generate({
    "task_type": "report",
    "time_window": 24
})

print(f"\nSystem Report:")
print(f"  Total Devices: {report['summary']['total_devices']}")
print(f"  Critical Devices: {report['summary']['critical_devices']}")
print(f"  Average Health: {report['summary']['avg_health_score']:.1f}/100")
```

## Best Practices

### 1. Baseline Establishment
- Collect at least 50-100 data points before relying on anomaly detection
- Use representative operating conditions for baseline
- Update baselines periodically to adapt to changing conditions

### 2. Threshold Configuration
- Set thresholds based on device specifications and operating environment
- Use warning thresholds to catch issues early
- Review and adjust thresholds based on historical data

### 3. Alert Management
- Implement alert fatigue prevention (rate limiting, aggregation)
- Use appropriate severity levels
- Acknowledge and resolve alerts promptly

### 4. Maintenance Scheduling
- Schedule maintenance during low-usage periods
- Keep maintenance windows realistic
- Document maintenance actions and outcomes

### 5. Firmware Updates
- Test patches in staging environment first
- Enable auto-rollback for critical systems
- Validate patches after application
- Keep audit log of all firmware changes

## API Reference

See individual module documentation:
- [Anomaly Detection API](./api/anomaly_detection.md)
- [Predictive Maintenance Agent API](./api/predictive_maintenance_agent.md)
- [Self-Healing Agent API](./api/self_healing_agent.md)
- [Firmware Patch Agent API](./api/firmware_patch_agent.md)
- [Device Health Monitor API](./api/device_health_monitor.md)
- [Monitoring Dashboard API](./api/monitoring_dashboard.md)

## Troubleshooting

### False Positive Anomalies
- Increase baseline sample size
- Adjust threshold factors (default is 3 standard deviations)
- Review baseline data for outliers

### Recovery Failures
- Check device connectivity
- Verify recovery actions are appropriate for device type
- Review device logs for detailed error information

### Patch Application Issues
- Ensure sufficient storage space
- Verify network connectivity for patch download
- Check device compatibility with patch version

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.
