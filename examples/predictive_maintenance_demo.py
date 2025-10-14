"""
Predictive Maintenance and Self-Healing Demo.
Demonstrates the capabilities of the predictive maintenance system.
"""

from accelerapp.agents import (
    PredictiveMaintenanceAgent,
    SelfHealingAgent,
    FirmwarePatchAgent
)
from accelerapp.monitoring import get_health_monitor, get_dashboard
from accelerapp.ai import AnomalyDetector
import time


def demo_anomaly_detection():
    """Demonstrate anomaly detection capabilities."""
    print("\n" + "="*60)
    print("ANOMALY DETECTION DEMO")
    print("="*60)
    
    detector = AnomalyDetector()
    
    # Build baseline with normal CPU usage
    print("\n1. Building baseline with normal values...")
    for i in range(50):
        detector.update_baseline("demo_device", "cpu_usage", 45.0 + (i % 10))
    print("   ✓ Baseline established")
    
    # Test with normal value
    print("\n2. Testing with normal value (50%)...")
    anomaly = detector.detect_anomaly("demo_device", "cpu_usage", 50.0)
    if anomaly:
        print(f"   ⚠️  Unexpected anomaly detected")
    else:
        print("   ✓ Normal value detected correctly")
    
    # Test with anomalous value
    print("\n3. Testing with anomalous value (95%)...")
    anomaly = detector.detect_anomaly("demo_device", "cpu_usage", 95.0)
    if anomaly:
        print(f"   🚨 Anomaly detected!")
        print(f"      Severity: {anomaly.severity}")
        print(f"      Confidence: {anomaly.confidence:.2%}")
        print(f"      Expected range: {anomaly.expected_range[0]:.1f}-{anomaly.expected_range[1]:.1f}")
    
    # Predict failure
    print("\n4. Predicting failure risk...")
    prediction = detector.predict_failure("demo_device", lookback_hours=24)
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   Failure Probability: {prediction['failure_probability']:.2%}")
    print(f"   Recommendations:")
    for rec in prediction['recommendations'][:3]:
        print(f"      - {rec}")


def demo_predictive_maintenance():
    """Demonstrate predictive maintenance agent."""
    print("\n" + "="*60)
    print("PREDICTIVE MAINTENANCE DEMO")
    print("="*60)
    
    agent = PredictiveMaintenanceAgent()
    
    # Monitor device
    print("\n1. Monitoring device health...")
    result = agent.generate({
        "task_type": "monitor",
        "device_id": "demo_device",
        "metrics": {
            "cpu_usage": 85.0,
            "memory_usage": 78.0,
            "temperature": 72.0
        }
    })
    
    print(f"   Health Score: {result['health_score']:.1f}/100")
    print(f"   Anomalies Detected: {result['anomalies_detected']}")
    if result['anomalies']:
        print("   Detected Anomalies:")
        for anomaly in result['anomalies']:
            print(f"      - {anomaly['metric']}: {anomaly['severity']}")
    
    # Predict failure
    print("\n2. Predicting potential failures...")
    prediction = agent.generate({
        "task_type": "predict",
        "device_id": "demo_device"
    })
    
    pred_data = prediction['prediction']
    print(f"   Risk Level: {pred_data['risk_level']}")
    print(f"   Failure Probability: {pred_data['failure_probability']:.2%}")
    
    # Schedule maintenance
    print("\n3. Scheduling maintenance...")
    schedule = agent.generate({
        "task_type": "schedule",
        "device_id": "demo_device"
    })
    
    sched_data = schedule['schedule']
    print(f"   Priority: {sched_data['priority']}")
    print(f"   Maintenance Window: {sched_data['maintenance_window']}")
    print(f"   Actions Required:")
    for action in sched_data['actions'][:3]:
        print(f"      - {action}")


def demo_self_healing():
    """Demonstrate self-healing capabilities."""
    print("\n" + "="*60)
    print("SELF-HEALING DEMO")
    print("="*60)
    
    agent = SelfHealingAgent()
    
    # Diagnose device
    print("\n1. Diagnosing device issues...")
    diagnosis = agent.generate({
        "task_type": "diagnose",
        "device_id": "demo_device",
        "symptoms": ["slow performance", "high memory"],
        "metrics": {
            "cpu_usage": 88.0,
            "memory_usage": 92.0,
            "temperature": 75.0
        }
    })
    
    diag_data = diagnosis['diagnosis']
    print(f"   Overall Severity: {diag_data['severity']}")
    print(f"   Issues Found: {len(diag_data['issues'])}")
    
    for issue in diag_data['issues'][:3]:
        print(f"\n   Issue: {issue['type']}")
        print(f"      Description: {issue['description']}")
        print(f"      Severity: {issue['severity']}")
        print(f"      Auto-recoverable: {issue['auto_recoverable']}")
    
    # Attempt recovery
    print("\n2. Attempting automatic recovery...")
    recovery = agent.generate({
        "task_type": "recover",
        "device_id": "demo_device",
        "issue_type": "memory"
    })
    
    print(f"   Actions Taken: {recovery['actions_taken']}")
    for action in recovery['recovery_actions']:
        print(f"      ✓ {action['description']}")
    
    # Repair configuration
    print("\n3. Repairing configuration...")
    repair = agent.generate({
        "task_type": "repair_config",
        "device_id": "demo_device",
        "config_type": "network"
    })
    
    print(f"   Repairs Completed: {repair['repairs_completed']}")
    for r in repair['repairs']:
        print(f"      ✓ {r['item']}: {r['action']}")
    
    # Validate system
    print("\n4. Validating system integrity...")
    validation = agent.generate({
        "task_type": "validate",
        "device_id": "demo_device"
    })
    
    print(f"   Validation Result: {validation['validation_result']}")


def demo_firmware_patching():
    """Demonstrate firmware patching."""
    print("\n" + "="*60)
    print("FIRMWARE PATCHING DEMO")
    print("="*60)
    
    agent = FirmwarePatchAgent()
    
    # Analyze patch needs
    print("\n1. Analyzing patch requirements...")
    analysis = agent.generate({
        "task_type": "analyze",
        "device_id": "demo_device",
        "current_version": "1.0.0",
        "analytics": {
            "security_score": 65,
            "crash_count": 8,
            "performance_score": 60
        }
    })
    
    print(f"   Current Version: {analysis['current_version']}")
    print(f"   Critical Issues: {len(analysis['critical_issues'])}")
    print(f"   Recommended Patches: {len(analysis['recommended_patches'])}")
    
    for patch in analysis['recommended_patches']:
        print(f"\n   Patch: {patch['patch_id']}")
        print(f"      Type: {patch['type']}")
        print(f"      Priority: {patch['priority']}")
        print(f"      Description: {patch['description']}")
    
    # Apply patch
    if analysis['recommended_patches']:
        print("\n2. Applying security patch...")
        patch = agent.generate({
            "task_type": "apply_patch",
            "device_id": "demo_device",
            "patch_id": analysis['recommended_patches'][0]['patch_id'],
            "patch_type": "security"
        })
        
        print(f"   Old Version: {patch['old_version']}")
        print(f"   New Version: {patch['new_version']}")
        print(f"   Patch Application Stages:")
        for stage in patch['stages']:
            print(f"      ✓ {stage['stage']}: {stage['message']}")
        
        # Validate patch
        print("\n3. Validating patch...")
        validation = agent.generate({
            "task_type": "validate",
            "device_id": "demo_device"
        })
        
        print(f"   Validation Result: {validation['validation_result']}")


def demo_monitoring_dashboard():
    """Demonstrate monitoring dashboard."""
    print("\n" + "="*60)
    print("MONITORING DASHBOARD DEMO")
    print("="*60)
    
    monitor = get_health_monitor()
    dashboard = get_dashboard()
    
    # Record metrics for multiple devices
    print("\n1. Recording device metrics...")
    devices = ["device001", "device002", "device003"]
    
    for device in devices:
        monitor.record_metric(device, "cpu_usage", 75.0 + devices.index(device) * 10, "%")
        monitor.record_metric(device, "memory_usage", 60.0 + devices.index(device) * 15, "%")
        monitor.record_metric(device, "temperature", 65.0 + devices.index(device) * 5, "°C")
    
    print(f"   ✓ Recorded metrics for {len(devices)} devices")
    
    # Get overall status
    print("\n2. Getting system status...")
    all_status = monitor.get_all_devices_status()
    
    print(f"   Total Devices: {all_status['total_devices']}")
    print(f"   Status Summary:")
    for status, count in all_status['status_summary'].items():
        print(f"      {status}: {count}")
    
    # Add alert rules
    print("\n3. Configuring alert rules...")
    dashboard.add_alert_rule(
        name="Critical CPU Alert",
        condition="cpu_usage > 90",
        severity="critical",
        notification_channels=["email"]
    )
    print("   ✓ Alert rule added")
    
    # Trigger sample alert
    dashboard.trigger_alert(
        device_id="device003",
        alert_type="cpu_overload",
        severity="high",
        message="CPU usage exceeded threshold"
    )
    
    # Get dashboard summary
    print("\n4. Dashboard Summary:")
    summary = dashboard.get_dashboard_summary()
    
    print(f"   Total Alerts: {summary['summary']['total_alerts']}")
    print(f"   Severity Breakdown:")
    for severity, count in summary['summary']['severity_counts'].items():
        print(f"      {severity}: {count}")
    
    # Get widget data
    print("\n5. Analytics Widgets:")
    severity_dist = dashboard.get_widget_data("severity_distribution")
    print(f"   Severity Distribution: {severity_dist['data']}")


def demo_integrated_workflow():
    """Demonstrate integrated monitoring workflow."""
    print("\n" + "="*60)
    print("INTEGRATED WORKFLOW DEMO")
    print("="*60)
    
    # Initialize all components
    pred_agent = PredictiveMaintenanceAgent()
    heal_agent = SelfHealingAgent()
    monitor = get_health_monitor()
    dashboard = get_dashboard()
    
    device_id = "workflow_device"
    
    print("\n1. Simulating device with issues...")
    # Simulate degrading device metrics
    metrics = {
        "cpu_usage": 92.0,
        "memory_usage": 88.0,
        "temperature": 82.0,
        "disk_usage": 75.0
    }
    
    for metric, value in metrics.items():
        monitor.record_metric(device_id, metric, value, "%")
    
    print("   ✓ Metrics recorded")
    
    # Monitor and detect anomalies
    print("\n2. Monitoring device...")
    monitor_result = pred_agent.generate({
        "task_type": "monitor",
        "device_id": device_id,
        "metrics": metrics
    })
    
    print(f"   Health Score: {monitor_result['health_score']:.1f}/100")
    print(f"   Anomalies: {monitor_result['anomalies_detected']}")
    
    if monitor_result['anomalies_detected'] > 0:
        # Trigger alert
        dashboard.trigger_alert(
            device_id=device_id,
            alert_type="anomaly_detected",
            severity="high",
            message=f"{monitor_result['anomalies_detected']} anomalies detected"
        )
        print("   🚨 Alert triggered")
    
    # Predict failure
    print("\n3. Predicting failure risk...")
    prediction = pred_agent.generate({
        "task_type": "predict",
        "device_id": device_id
    })
    
    risk = prediction['prediction']['risk_level']
    print(f"   Risk Level: {risk}")
    
    if risk in ["high", "critical"]:
        # Diagnose and heal
        print("\n4. Attempting self-healing...")
        diagnosis = heal_agent.generate({
            "task_type": "diagnose",
            "device_id": device_id,
            "symptoms": ["high resource usage"],
            "metrics": metrics
        })
        
        print(f"   Issues Found: {len(diagnosis['diagnosis']['issues'])}")
        
        # Attempt recovery for recoverable issues
        for issue in diagnosis['diagnosis']['issues']:
            if issue.get('auto_recoverable'):
                recovery = heal_agent.generate({
                    "task_type": "recover",
                    "device_id": device_id,
                    "issue_type": issue['type']
                })
                print(f"   ✓ Recovery attempted for {issue['type']}")
    
    # Schedule maintenance
    print("\n5. Scheduling maintenance...")
    schedule = pred_agent.generate({
        "task_type": "schedule",
        "device_id": device_id
    })
    
    print(f"   Priority: {schedule['schedule']['priority']}")
    print(f"   Window: {schedule['schedule']['maintenance_window']}")
    
    # Final report
    print("\n6. Generating final report...")
    report = pred_agent.generate({
        "task_type": "report",
        "device_id": device_id
    })
    
    print(f"   Report generated for {len(report['device_reports'])} device(s)")
    print("   ✓ Workflow completed")


def main():
    """Run all demos."""
    print("\n" + "🚀 " * 20)
    print("PREDICTIVE MAINTENANCE & SELF-HEALING SYSTEM DEMO")
    print("🚀 " * 20)
    
    try:
        # Run individual demos
        demo_anomaly_detection()
        time.sleep(1)
        
        demo_predictive_maintenance()
        time.sleep(1)
        
        demo_self_healing()
        time.sleep(1)
        
        demo_firmware_patching()
        time.sleep(1)
        
        demo_monitoring_dashboard()
        time.sleep(1)
        
        demo_integrated_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
