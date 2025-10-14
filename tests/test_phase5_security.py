"""
Tests for Phase 5 Security & Compliance features.
"""

import pytest
from datetime import datetime, timedelta

from accelerapp.production.security import (
    # Network policies
    NetworkPolicyEnforcer,
    PolicyType,
    PolicyAction,
    # WAF
    WebApplicationFirewall,
    ThreatLevel,
    RuleType,
    # Backup & Recovery
    BackupRecoverySystem,
    BackupType,
    BackupStatus,
    RecoveryStatus,
    # Security Audit
    SecurityAuditSystem,
    AuditEventType,
    ComplianceStandard,
    # Orchestrator
    Phase5SecurityOrchestrator
)


class TestNetworkPolicyEnforcement:
    """Tests for network policy enforcement."""
    
    def test_policy_enforcer_initialization(self):
        """Test policy enforcer initialization."""
        enforcer = NetworkPolicyEnforcer()
        assert enforcer is not None
        assert enforcer.enforcement_enabled
        stats = enforcer.get_statistics()
        assert stats["total_policies"] == 0
    
    def test_create_network_policy(self):
        """Test creating network policy."""
        enforcer = NetworkPolicyEnforcer()
        policy = enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "default",
            PolicyType.INGRESS,
            priority=50
        )
        
        assert policy.policy_id == "test-policy"
        assert policy.name == "Test Policy"
        assert policy.namespace == "default"
        assert policy.policy_type == PolicyType.INGRESS
        assert policy.priority == 50
        assert policy.enabled
    
    def test_add_policy_rule(self):
        """Test adding rule to policy."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "default",
            PolicyType.INGRESS
        )
        
        success = enforcer.add_rule(
            "test-policy",
            "allow-https",
            action=PolicyAction.ALLOW,
            ports=[443],
            protocols=["https"]
        )
        
        assert success
        policies = enforcer.list_policies()
        assert len(policies) == 1
        assert len(policies[0].rules) == 1
    
    def test_check_connection_allowed(self):
        """Test checking if connection is allowed."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "default",
            PolicyType.INGRESS,
            priority=10
        )
        enforcer.add_rule(
            "test-policy",
            "allow-https",
            action=PolicyAction.ALLOW,
            ports=[443],
            protocols=["https"]
        )
        
        result = enforcer.check_connection(
            "app-1",
            "app-2",
            443,
            "https"
        )
        
        assert result["allowed"]
    
    def test_check_connection_denied(self):
        """Test checking if connection is denied."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "default",
            PolicyType.INGRESS,
            priority=10
        )
        enforcer.add_rule(
            "test-policy",
            "deny-telnet",
            action=PolicyAction.DENY,
            ports=[23],
            protocols=["tcp"]
        )
        
        result = enforcer.check_connection(
            "app-1",
            "app-2",
            23,
            "tcp"
        )
        
        assert not result["allowed"]
        assert "Denied" in result["reason"]
    
    def test_policy_violations_recorded(self):
        """Test that policy violations are recorded."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.check_connection("app-1", "app-2", 80, "http")
        
        violations = enforcer.get_violations()
        assert len(violations) > 0
    
    def test_enable_disable_policy(self):
        """Test enabling and disabling policies."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "default",
            PolicyType.INGRESS
        )
        
        assert enforcer.disable_policy("test-policy")
        policies = enforcer.list_policies()
        assert not policies[0].enabled
        
        assert enforcer.enable_policy("test-policy")
        policies = enforcer.list_policies()
        assert policies[0].enabled
    
    def test_export_kubernetes_policy(self):
        """Test exporting policy in Kubernetes format."""
        enforcer = NetworkPolicyEnforcer()
        enforcer.create_policy(
            "test-policy",
            "Test Policy",
            "production",
            PolicyType.INGRESS
        )
        
        exported = enforcer.export_policy("test-policy")
        
        assert exported is not None
        assert exported["kind"] == "NetworkPolicy"
        assert exported["metadata"]["name"] == "Test Policy"
        assert exported["metadata"]["namespace"] == "production"


class TestWebApplicationFirewall:
    """Tests for Web Application Firewall."""
    
    def test_waf_initialization(self):
        """Test WAF initialization."""
        waf = WebApplicationFirewall()
        assert waf is not None
        assert waf.enabled
        stats = waf.get_statistics()
        assert stats["total_rules"] > 0  # Should have default rules
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        waf = WebApplicationFirewall()
        
        result = waf.inspect_request(
            "192.168.1.100",
            "/api/users",
            "GET",
            body="SELECT * FROM users WHERE id=1"
        )
        
        assert not result["allowed"]
        assert "sql" in result["rule_id"].lower()
    
    def test_xss_detection(self):
        """Test XSS detection."""
        waf = WebApplicationFirewall()
        
        result = waf.inspect_request(
            "192.168.1.100",
            "/api/comment",
            "POST",
            body="<script>alert(1)</script>"
        )
        
        assert not result["allowed"]
        assert "xss" in result["rule_id"].lower()
    
    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        waf = WebApplicationFirewall()
        
        result = waf.inspect_request(
            "192.168.1.100",
            "/api/file?path=../../etc/passwd",
            "GET"
        )
        
        assert not result["allowed"]
        assert "path" in result["rule_id"].lower()
    
    def test_rate_limiting(self):
        """Test rate limiting."""
        waf = WebApplicationFirewall()
        ip = "192.168.1.100"
        
        # Set a low rate limit
        waf.set_rate_limit(ip, requests_per_minute=5)
        
        # Make requests up to the limit
        for _ in range(5):
            result = waf.inspect_request(ip, "/api/test", "GET")
            assert result["allowed"]
        
        # Next request should be blocked
        result = waf.inspect_request(ip, "/api/test", "GET")
        assert not result["allowed"]
        assert "Rate limit" in result["reason"]
    
    def test_ip_blacklist(self):
        """Test IP blacklist."""
        waf = WebApplicationFirewall()
        ip = "192.168.1.100"
        
        waf.block_ip(ip)
        
        result = waf.inspect_request(ip, "/api/test", "GET")
        assert not result["allowed"]
        assert "blacklist" in result["reason"].lower()
    
    def test_ip_whitelist(self):
        """Test IP whitelist."""
        waf = WebApplicationFirewall()
        ip = "192.168.1.100"
        
        waf.whitelist_ip(ip)
        
        # Even with SQL injection, whitelisted IP should pass
        result = waf.inspect_request(
            ip,
            "/api/test",
            "GET",
            body="SELECT * FROM users"
        )
        
        assert result["allowed"]
        assert "whitelist" in result["reason"].lower()
    
    def test_custom_waf_rule(self):
        """Test adding custom WAF rule."""
        waf = WebApplicationFirewall()
        
        rule = waf.add_rule(
            "custom-rule",
            "Block Evil Pattern",
            RuleType.CUSTOM,
            pattern=r"evil_pattern",
            action="block"
        )
        
        assert rule.rule_id == "custom-rule"
        
        result = waf.inspect_request(
            "192.168.1.100",
            "/api/test",
            "GET",
            body="This contains evil_pattern"
        )
        
        assert not result["allowed"]
    
    def test_threat_detections(self):
        """Test getting threat detections."""
        waf = WebApplicationFirewall()
        
        # Generate some detections
        waf.inspect_request(
            "192.168.1.100",
            "/api/test",
            "GET",
            body="SELECT * FROM users"
        )
        
        detections = waf.get_detections()
        assert len(detections) > 0
    
    def test_waf_security_report(self):
        """Test WAF security report generation."""
        waf = WebApplicationFirewall()
        
        # Generate some activity
        waf.inspect_request("192.168.1.100", "/api/test", "GET", body="SELECT *")
        
        report = waf.generate_security_report()
        
        assert "summary" in report
        assert "high_severity_threats" in report
        assert "recommendations" in report


class TestBackupRecoverySystem:
    """Tests for backup and recovery system."""
    
    def test_backup_system_initialization(self):
        """Test backup system initialization."""
        system = BackupRecoverySystem()
        assert system is not None
        stats = system.get_statistics()
        assert stats["configurations"] == 0
    
    def test_create_backup_config(self):
        """Test creating backup configuration."""
        system = BackupRecoverySystem()
        
        config = system.create_backup_config(
            "daily-backup",
            "Daily Full Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data", "/config"],
            retention_days=30
        )
        
        assert config.config_id == "daily-backup"
        assert config.backup_type == BackupType.FULL
        assert config.retention_days == 30
        assert "/data" in config.target_paths
    
    def test_start_backup(self):
        """Test starting backup operation."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"]
        )
        
        record = system.start_backup("test-backup")
        
        assert record.backup_id is not None
        assert record.config_id == "test-backup"
        assert record.status == BackupStatus.IN_PROGRESS
    
    def test_complete_backup(self):
        """Test completing backup operation."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"]
        )
        
        record = system.start_backup("test-backup")
        completed = system.complete_backup(
            record.backup_id,
            size_bytes=1024 * 1024,
            files_count=100,
            checksum="abc123",
            success=True
        )
        
        assert completed.status == BackupStatus.COMPLETED
        assert completed.size_bytes == 1024 * 1024
        assert completed.files_count == 100
    
    def test_create_recovery_plan(self):
        """Test creating recovery plan."""
        system = BackupRecoverySystem()
        
        steps = [
            {"step": "1", "action": "Stop services"},
            {"step": "2", "action": "Restore data"},
            {"step": "3", "action": "Start services"}
        ]
        
        plan = system.create_recovery_plan(
            "disaster-recovery",
            "Disaster Recovery Plan",
            "Full system recovery procedure",
            steps,
            rto_minutes=240,
            rpo_minutes=60
        )
        
        assert plan.plan_id == "disaster-recovery"
        assert plan.rto_minutes == 240
        assert plan.rpo_minutes == 60
        assert len(plan.steps) == 3
    
    def test_start_recovery(self):
        """Test starting recovery operation."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"]
        )
        
        record = system.start_backup("test-backup")
        system.complete_backup(
            record.backup_id,
            size_bytes=1024,
            files_count=10,
            checksum="abc",
            success=True
        )
        
        operation = system.start_recovery(record.backup_id)
        
        assert operation.operation_id is not None
        assert operation.backup_id == record.backup_id
        assert operation.status == RecoveryStatus.IN_PROGRESS
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"],
            retention_days=1
        )
        
        record = system.start_backup("test-backup")
        system.complete_backup(
            record.backup_id,
            size_bytes=1024,
            files_count=10,
            checksum="abc",
            success=True
        )
        
        # Backups should be cleaned up based on retention policy
        # In real implementation, would test with old timestamp
        result = system.cleanup_old_backups()
        assert "removed_count" in result
    
    def test_verify_backup(self):
        """Test backup verification."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"]
        )
        
        record = system.start_backup("test-backup")
        system.complete_backup(
            record.backup_id,
            size_bytes=1024,
            files_count=10,
            checksum="abc123",
            success=True
        )
        
        verification = system.verify_backup(record.backup_id)
        
        assert verification["valid"]
        assert verification["checksum"] == "abc123"
    
    def test_compliance_report(self):
        """Test backup compliance report."""
        system = BackupRecoverySystem()
        system.create_backup_config(
            "test-backup",
            "Test Backup",
            BackupType.FULL,
            "0 2 * * *",
            ["/data"]
        )
        
        report = system.generate_compliance_report()
        
        assert "summary" in report
        assert "compliance_rate" in report
        assert "recommendations" in report


class TestSecurityAuditSystem:
    """Tests for security audit system."""
    
    def test_audit_system_initialization(self):
        """Test audit system initialization."""
        audit = SecurityAuditSystem()
        assert audit is not None
        assert audit.audit_enabled
        stats = audit.get_statistics()
        assert stats["total_events"] == 0
    
    def test_log_audit_event(self):
        """Test logging audit event."""
        audit = SecurityAuditSystem()
        
        event = audit.log_event(
            AuditEventType.ACCESS,
            "user1",
            "read",
            "/api/data",
            "success",
            ip_address="192.168.1.100"
        )
        
        assert event is not None
        assert event.event_type == AuditEventType.ACCESS
        assert event.actor == "user1"
        assert event.action == "read"
        assert event.result == "success"
    
    def test_get_events_filtered(self):
        """Test getting filtered events."""
        audit = SecurityAuditSystem()
        
        # Log multiple events
        audit.log_event(
            AuditEventType.ACCESS,
            "user1",
            "read",
            "/api/data",
            "success"
        )
        audit.log_event(
            AuditEventType.AUTHENTICATION,
            "user2",
            "login",
            "system",
            "failure"
        )
        
        # Get all events
        all_events = audit.get_events()
        assert len(all_events) >= 2
        
        # Get filtered by type
        access_events = audit.get_events(event_type=AuditEventType.ACCESS)
        assert all(e.event_type == AuditEventType.ACCESS for e in access_events)
        
        # Get filtered by actor
        user1_events = audit.get_events(actor="user1")
        assert all(e.actor == "user1" for e in user1_events)
    
    def test_get_security_violations(self):
        """Test getting security violations."""
        audit = SecurityAuditSystem()
        
        audit.log_event(
            AuditEventType.SECURITY_VIOLATION,
            "attacker",
            "sql_injection",
            "/api/users",
            "blocked",
            severity="critical"
        )
        
        violations = audit.get_security_violations()
        assert len(violations) > 0
        assert violations[0].event_type == AuditEventType.SECURITY_VIOLATION
    
    def test_get_failed_authentications(self):
        """Test getting failed authentications."""
        audit = SecurityAuditSystem()
        
        audit.log_event(
            AuditEventType.AUTHENTICATION,
            "user1",
            "login",
            "system",
            "failure"
        )
        
        failed_auths = audit.get_failed_authentications()
        assert len(failed_auths) > 0
        assert all(e.result == "failure" for e in failed_auths)
    
    def test_compliance_checks(self):
        """Test compliance checks."""
        audit = SecurityAuditSystem()
        
        # Run a specific check
        result = audit.run_compliance_check("soc2-audit-logging")
        
        assert result is not None
        assert result.check_id == "soc2-audit-logging"
        assert isinstance(result.passed, bool)
    
    def test_compliance_scan(self):
        """Test full compliance scan."""
        audit = SecurityAuditSystem()
        
        scan_result = audit.run_compliance_scan(ComplianceStandard.SOC2)
        
        assert "scan_timestamp" in scan_result
        assert "total_checks" in scan_result
        assert "compliance_score" in scan_result
        assert scan_result["total_checks"] > 0
    
    def test_audit_report_generation(self):
        """Test audit report generation."""
        audit = SecurityAuditSystem()
        
        # Generate some events
        audit.log_event(
            AuditEventType.ACCESS,
            "user1",
            "read",
            "/api/data",
            "success"
        )
        
        report = audit.generate_audit_report()
        
        assert "report_period" in report
        assert "summary" in report
        assert "top_actors" in report
        assert "top_resources" in report
    
    def test_export_audit_trail(self):
        """Test exporting audit trail."""
        audit = SecurityAuditSystem()
        
        audit.log_event(
            AuditEventType.ACCESS,
            "user1",
            "read",
            "/api/data",
            "success"
        )
        
        exported = audit.export_audit_trail(format="json")
        
        assert exported is not None
        assert isinstance(exported, str)
        assert "event_id" in exported


class TestPhase5Orchestrator:
    """Tests for Phase 5 security orchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = Phase5SecurityOrchestrator()
        assert orchestrator is not None
        assert orchestrator.network_policy is not None
        assert orchestrator.waf is not None
        assert orchestrator.backup_recovery is not None
        assert orchestrator.security_audit is not None
    
    def test_enforce_network_policies(self):
        """Test network policy enforcement through orchestrator."""
        orchestrator = Phase5SecurityOrchestrator()
        
        result = orchestrator.enforce_network_policies(
            "app-1",
            "app-2",
            443,
            "https"
        )
        
        assert "allowed" in result
    
    def test_protect_endpoint(self):
        """Test endpoint protection through orchestrator."""
        orchestrator = Phase5SecurityOrchestrator()
        
        result = orchestrator.protect_endpoint(
            "192.168.1.100",
            "/api/users",
            "GET"
        )
        
        assert "allowed" in result
    
    def test_backup_system(self):
        """Test backup through orchestrator."""
        orchestrator = Phase5SecurityOrchestrator()
        
        result = orchestrator.backup_system(
            "daily-full-backup",
            "admin"
        )
        
        assert result["success"]
        assert "backup_id" in result
    
    def test_scan_vulnerabilities(self):
        """Test vulnerability scanning through orchestrator."""
        orchestrator = Phase5SecurityOrchestrator()
        
        result = orchestrator.scan_vulnerabilities(
            "dependencies",
            ["package1", "package2"],
            "admin"
        )
        
        assert "scan_id" in result
        assert "total_scanned" in result
    
    def test_run_compliance_check(self):
        """Test compliance check through orchestrator."""
        orchestrator = Phase5SecurityOrchestrator()
        
        result = orchestrator.run_compliance_check(ComplianceStandard.SOC2)
        
        assert "total_checks" in result
        assert "compliance_score" in result
    
    def test_security_dashboard(self):
        """Test security dashboard."""
        orchestrator = Phase5SecurityOrchestrator()
        
        dashboard = orchestrator.get_security_dashboard()
        
        assert "timestamp" in dashboard
        assert "network_policies" in dashboard
        assert "waf" in dashboard
        assert "backups" in dashboard
        assert "audit" in dashboard
        assert "vulnerabilities" in dashboard
    
    def test_security_posture(self):
        """Test security posture assessment."""
        orchestrator = Phase5SecurityOrchestrator()
        
        posture = orchestrator.get_security_posture()
        
        assert "overall_score" in posture
        assert "status" in posture
        assert "component_scores" in posture
        assert "recommendations" in posture
        assert 0 <= posture["overall_score"] <= 100
    
    def test_compliance_report(self):
        """Test compliance report generation."""
        orchestrator = Phase5SecurityOrchestrator()
        
        report = orchestrator.generate_compliance_report()
        
        assert "timestamp" in report
        assert "security_posture" in report
        assert "network_policies" in report
        assert "waf_protection" in report
        assert "backup_compliance" in report
        assert "audit_summary" in report
        assert "vulnerability_summary" in report
