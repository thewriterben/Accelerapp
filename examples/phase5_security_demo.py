"""
Phase 5 Security & Compliance Demo
Demonstrates network policies, WAF, backups, and security auditing.
"""

from accelerapp.production.security import (
    Phase5SecurityOrchestrator,
    ComplianceStandard,
    PolicyType,
    PolicyAction,
    BackupType,
    AuditEventType,
    Severity
)


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_network_policies(orchestrator):
    """Demonstrate network policy enforcement."""
    print_section("Network Policy Enforcement")
    
    # Create network policy
    orchestrator.network_policy.create_policy(
        "demo-policy",
        "Demo Network Policy",
        "default",
        PolicyType.INGRESS,
        priority=10
    )
    
    # Add allow rule
    orchestrator.network_policy.add_rule(
        "demo-policy",
        "allow-https",
        action=PolicyAction.ALLOW,
        ports=[443],
        protocols=["https"]
    )
    
    print("✓ Created network policy 'demo-policy'")
    print("✓ Added rule to allow HTTPS traffic on port 443")
    
    # Test connection
    result = orchestrator.enforce_network_policies(
        "frontend-app",
        "backend-api",
        443,
        "https"
    )
    
    print(f"\n📊 Connection Test Results:")
    print(f"   Source: frontend-app")
    print(f"   Destination: backend-api")
    print(f"   Port: 443 (HTTPS)")
    print(f"   Allowed: {'✅ Yes' if result['allowed'] else '❌ No'}")
    print(f"   Reason: {result.get('reason', 'N/A')}")
    
    # Get statistics
    stats = orchestrator.network_policy.get_statistics()
    print(f"\n📈 Network Policy Statistics:")
    print(f"   Total Policies: {stats['total_policies']}")
    print(f"   Active Policies: {stats['enabled_policies']}")
    print(f"   Violations Logged: {stats['total_violations']}")


def demo_waf_protection(orchestrator):
    """Demonstrate WAF protection."""
    print_section("Web Application Firewall (WAF)")
    
    # Test legitimate request
    print("Testing legitimate request...")
    result = orchestrator.protect_endpoint(
        "192.168.1.100",
        "/api/users",
        "GET"
    )
    print(f"✅ Legitimate request: {'Allowed' if result['allowed'] else 'Blocked'}")
    
    # Test SQL injection
    print("\nTesting SQL injection attack...")
    result = orchestrator.waf.inspect_request(
        "192.168.1.200",
        "/api/users",
        "GET",
        body="SELECT * FROM users WHERE id=1"
    )
    print(f"🛡️  SQL injection: {'Blocked ✓' if not result['allowed'] else 'Allowed (FAIL)'}")
    if not result['allowed']:
        print(f"   Threat Level: {result.get('threat_level', 'N/A')}")
        print(f"   Reason: {result['reason']}")
    
    # Test XSS attack
    print("\nTesting XSS attack...")
    result = orchestrator.waf.inspect_request(
        "192.168.1.201",
        "/api/comment",
        "POST",
        body="<script>alert(1)</script>"
    )
    print(f"🛡️  XSS attack: {'Blocked ✓' if not result['allowed'] else 'Allowed (FAIL)'}")
    
    # Test path traversal
    print("\nTesting path traversal attack...")
    result = orchestrator.waf.inspect_request(
        "192.168.1.202",
        "/api/file",
        "GET",
        query_params={"path": "../../etc/passwd"}
    )
    print(f"🛡️  Path traversal: {'Blocked ✓' if not result['allowed'] else 'Allowed (FAIL)'}")
    
    # Get WAF statistics
    stats = orchestrator.waf.get_statistics()
    print(f"\n📈 WAF Statistics:")
    print(f"   WAF Enabled: {'✅ Yes' if stats['enabled'] else '❌ No'}")
    print(f"   Active Rules: {stats['enabled_rules']}/{stats['total_rules']}")
    print(f"   Threats Detected: {stats['total_detections']}")
    print(f"   - Critical: {stats['detections_by_level']['critical']}")
    print(f"   - High: {stats['detections_by_level']['high']}")
    print(f"   - Medium: {stats['detections_by_level']['medium']}")
    print(f"   - Low: {stats['detections_by_level']['low']}")


def demo_backup_recovery(orchestrator):
    """Demonstrate backup and recovery."""
    print_section("Backup & Disaster Recovery")
    
    # Create backup configuration
    config = orchestrator.backup_recovery.create_backup_config(
        "demo-backup",
        "Demo Backup Configuration",
        BackupType.FULL,
        "0 2 * * *",  # 2 AM daily
        target_paths=["/data", "/config"],
        retention_days=30
    )
    
    print("✓ Created backup configuration:")
    print(f"   ID: {config.config_id}")
    print(f"   Type: {config.backup_type.value}")
    print(f"   Schedule: {config.schedule_cron}")
    print(f"   Retention: {config.retention_days} days")
    
    # Execute backup
    print("\n⏳ Executing backup...")
    result = orchestrator.backup_system("demo-backup", "demo-user")
    
    if result['success']:
        print(f"✅ Backup completed successfully")
        print(f"   Backup ID: {result['backup_id']}")
        print(f"   Status: {result['status']}")
    
    # Create recovery plan
    plan = orchestrator.backup_recovery.create_recovery_plan(
        "demo-recovery",
        "Demo Recovery Plan",
        "Emergency recovery procedure for demo environment",
        steps=[
            {"step": "1", "action": "Stop all services"},
            {"step": "2", "action": "Restore data from backup"},
            {"step": "3", "action": "Verify data integrity"},
            {"step": "4", "action": "Start services"}
        ],
        rto_minutes=60,
        rpo_minutes=30
    )
    
    print(f"\n✓ Created recovery plan:")
    print(f"   Name: {plan.name}")
    print(f"   RTO: {plan.rto_minutes} minutes")
    print(f"   RPO: {plan.rpo_minutes} minutes")
    print(f"   Steps: {len(plan.steps)}")
    
    # Get backup statistics
    stats = orchestrator.backup_recovery.get_statistics()
    print(f"\n📈 Backup Statistics:")
    print(f"   Configurations: {stats['configurations']}")
    print(f"   Total Backups: {stats['total_backups']}")
    print(f"   Completed: {stats['completed_backups']}")
    print(f"   Failed: {stats['failed_backups']}")
    print(f"   Recovery Plans: {stats['recovery_plans']}")


def demo_security_audit(orchestrator):
    """Demonstrate security auditing."""
    print_section("Security Auditing & Compliance")
    
    # Log various security events
    print("Logging security events...")
    
    orchestrator.security_audit.log_event(
        AuditEventType.ACCESS,
        "user@example.com",
        "read",
        "/api/data",
        "success",
        ip_address="192.168.1.100"
    )
    print("✓ Logged access event")
    
    orchestrator.security_audit.log_event(
        AuditEventType.AUTHENTICATION,
        "admin@example.com",
        "login",
        "system",
        "success",
        ip_address="192.168.1.101"
    )
    print("✓ Logged authentication event")
    
    orchestrator.security_audit.log_event(
        AuditEventType.CONFIGURATION_CHANGE,
        "admin@example.com",
        "update_policy",
        "network_policy:demo-policy",
        "success"
    )
    print("✓ Logged configuration change")
    
    # Run compliance check
    print("\n🔍 Running SOC2 compliance scan...")
    result = orchestrator.run_compliance_check(ComplianceStandard.SOC2)
    
    print(f"\n📋 Compliance Results:")
    print(f"   Standard: SOC2")
    print(f"   Total Checks: {result['total_checks']}")
    print(f"   Passed: {result['passed_checks']}")
    print(f"   Failed: {result['failed_checks']}")
    print(f"   Compliance Score: {result['compliance_score']}%")
    
    # Get audit statistics
    stats = orchestrator.security_audit.get_statistics()
    print(f"\n📈 Audit Statistics:")
    print(f"   Total Events: {stats['total_events']}")
    print(f"   Events by Severity:")
    print(f"   - Critical: {stats['events_by_severity']['critical']}")
    print(f"   - Error: {stats['events_by_severity']['error']}")
    print(f"   - Warning: {stats['events_by_severity']['warning']}")
    print(f"   - Info: {stats['events_by_severity']['info']}")


def demo_security_posture(orchestrator):
    """Demonstrate security posture assessment."""
    print_section("Security Posture Assessment")
    
    # Get security dashboard
    dashboard = orchestrator.get_security_dashboard()
    
    print("📊 Security Dashboard:")
    print(f"\n🔐 Network Policies:")
    print(f"   Total: {dashboard['network_policies']['total_policies']}")
    print(f"   Active: {dashboard['network_policies']['enabled_policies']}")
    
    print(f"\n🛡️  Web Application Firewall:")
    print(f"   Enabled: {'✅' if dashboard['waf']['enabled'] else '❌'}")
    print(f"   Active Rules: {dashboard['waf']['enabled_rules']}")
    print(f"   Detections: {dashboard['waf']['total_detections']}")
    
    print(f"\n💾 Backup & Recovery:")
    print(f"   Configurations: {dashboard['backups']['configurations']}")
    print(f"   Completed Backups: {dashboard['backups']['completed_backups']}")
    
    print(f"\n📝 Security Audit:")
    print(f"   Total Events: {dashboard['audit']['total_events']}")
    print(f"   Compliance Checks: {dashboard['audit']['compliance_checks']}")
    
    # Get security posture
    print("\n" + "-" * 60)
    posture = orchestrator.get_security_posture()
    
    print(f"\n🎯 Overall Security Posture:")
    print(f"   Score: {posture['overall_score']}/100")
    print(f"   Status: {posture['status'].upper()}")
    
    print(f"\n📊 Component Scores:")
    for component, score in posture['component_scores'].items():
        status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        print(f"   {status} {component.replace('_', ' ').title()}: {score}/100")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(posture['recommendations'], 1):
        print(f"   {i}. {rec}")


def demo_vulnerability_scanning(orchestrator):
    """Demonstrate vulnerability scanning."""
    print_section("Vulnerability Scanning")
    
    # Add some known vulnerabilities for demo
    orchestrator.vulnerability_scanner.add_vulnerability(
        "demo-vuln-1",
        "Outdated Package Version",
        "Package has known security vulnerability",
        Severity.HIGH,
        "example-package",
        affected_versions=["1.0.0", "1.0.1"],
        fixed_version="1.0.2",
        cve_id="CVE-2024-12345"
    )
    
    print("✓ Added test vulnerability to database")
    
    # Scan dependencies
    result = orchestrator.scan_vulnerabilities(
        "dependencies",
        ["example-package", "safe-package"],
        "demo-user"
    )
    
    print(f"\n🔍 Dependency Scan Results:")
    print(f"   Scan ID: {result['scan_id']}")
    print(f"   Packages Scanned: {result['total_scanned']}")
    print(f"   Vulnerabilities Found: {result['vulnerabilities_found']}")
    print(f"   Critical: {result['critical']}")
    
    # Generate security report
    report = orchestrator.vulnerability_scanner.generate_security_report()
    print(f"\n📋 Vulnerability Summary:")
    print(f"   Total Scans: {report['summary']['total_scans']}")
    print(f"   Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
    
    if report['critical_vulnerabilities']:
        print(f"\n⚠️  Critical Vulnerabilities:")
        for vuln in report['critical_vulnerabilities']:
            print(f"   - {vuln['title']} ({vuln['cve_id']})")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")


def main():
    """Run Phase 5 security demo."""
    print("\n" + "=" * 60)
    print("  Phase 5: Security & Compliance Demo")
    print("  Accelerapp Production Security Features")
    print("=" * 60)
    
    # Initialize orchestrator
    print("\n⏳ Initializing Phase 5 Security Orchestrator...")
    orchestrator = Phase5SecurityOrchestrator()
    print("✅ Orchestrator initialized\n")
    
    # Run demos
    demo_network_policies(orchestrator)
    demo_waf_protection(orchestrator)
    demo_backup_recovery(orchestrator)
    demo_security_audit(orchestrator)
    demo_vulnerability_scanning(orchestrator)
    demo_security_posture(orchestrator)
    
    # Final summary
    print_section("Demo Complete")
    print("✅ All Phase 5 security features demonstrated successfully!")
    print("\n📚 Documentation: PHASE5_IMPLEMENTATION.md")
    print("🧪 Tests: tests/test_phase5_security.py")
    print("💻 Source: src/accelerapp/production/security/")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
