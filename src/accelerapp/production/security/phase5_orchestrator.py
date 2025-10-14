"""
Phase 5 Security & Compliance Orchestrator.
Integrates network policies, WAF, backups, and security auditing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .network_policy import NetworkPolicyEnforcer, PolicyType, PolicyAction
from .waf import WebApplicationFirewall, ThreatLevel
from .backup_recovery import BackupRecoverySystem, BackupType, RecoveryStatus
from .security_audit import SecurityAuditSystem, AuditEventType, ComplianceStandard
from .vulnerability_scan import VulnerabilityScanner, Severity


class Phase5SecurityOrchestrator:
    """
    Orchestrates all Phase 5 security and compliance components.
    Provides unified interface for security operations.
    """
    
    def __init__(self):
        """Initialize Phase 5 orchestrator."""
        self.network_policy = NetworkPolicyEnforcer()
        self.waf = WebApplicationFirewall()
        self.backup_recovery = BackupRecoverySystem()
        self.security_audit = SecurityAuditSystem()
        self.vulnerability_scanner = VulnerabilityScanner()
        
        # Initialize with default security configuration
        self._setup_default_security()
    
    def _setup_default_security(self):
        """Set up default security configuration."""
        # Create default network policies
        self.network_policy.create_policy(
            "default-ingress",
            "Default Ingress Policy",
            "default",
            PolicyType.INGRESS,
            priority=100
        )
        
        # Add default ingress rule
        self.network_policy.add_rule(
            "default-ingress",
            "allow-https",
            action=PolicyAction.ALLOW,
            ports=[443],
            protocols=["https"]
        )
        
        # Create default backup config
        self.backup_recovery.create_backup_config(
            "daily-full-backup",
            "Daily Full Backup",
            BackupType.FULL,
            "0 2 * * *",  # 2 AM daily
            target_paths=["/data", "/config"],
            retention_days=30
        )
        
        # Log initialization
        self.security_audit.log_event(
            AuditEventType.SYSTEM_EVENT,
            "system",
            "initialize",
            "phase5_orchestrator",
            "success",
            severity="info"
        )
    
    def enforce_network_policies(
        self,
        source: str,
        destination: str,
        port: int,
        protocol: str
    ) -> Dict[str, Any]:
        """
        Enforce network policies for connection.
        
        Args:
            source: Source identifier
            destination: Destination identifier
            port: Connection port
            protocol: Connection protocol
            
        Returns:
            Enforcement result
        """
        result = self.network_policy.check_connection(
            source, destination, port, protocol
        )
        
        # Log the enforcement decision
        self.security_audit.log_event(
            AuditEventType.AUTHORIZATION,
            source,
            f"connect:{protocol}:{port}",
            destination,
            "success" if result["allowed"] else "denied",
            severity="warning" if not result["allowed"] else "info"
        )
        
        return result
    
    def protect_endpoint(
        self,
        source_ip: str,
        endpoint: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Protect endpoint with WAF.
        
        Args:
            source_ip: Client IP address
            endpoint: Request endpoint
            method: HTTP method
            headers: Request headers
            body: Request body
            
        Returns:
            Protection result
        """
        result = self.waf.inspect_request(
            source_ip, endpoint, method, headers, body
        )
        
        # Log WAF decision
        if not result.get("allowed", True):
            self.security_audit.log_event(
                AuditEventType.SECURITY_VIOLATION,
                source_ip,
                f"{method} {endpoint}",
                "waf",
                "blocked",
                ip_address=source_ip,
                severity="warning" if result.get("threat_level") == "medium" else "error"
            )
        
        return result
    
    def backup_system(
        self,
        config_id: str,
        initiated_by: str
    ) -> Dict[str, Any]:
        """
        Execute system backup.
        
        Args:
            config_id: Backup configuration ID
            initiated_by: User or system initiating backup
            
        Returns:
            Backup result
        """
        try:
            record = self.backup_recovery.start_backup(config_id)
            
            # Simulate backup completion
            # In real implementation, would perform actual backup
            self.backup_recovery.complete_backup(
                record.backup_id,
                size_bytes=1024 * 1024 * 100,  # 100 MB
                files_count=1000,
                checksum="abc123",
                success=True
            )
            
            # Log backup
            self.security_audit.log_event(
                AuditEventType.SYSTEM_EVENT,
                initiated_by,
                "backup",
                config_id,
                "success",
                severity="info"
            )
            
            return {
                "success": True,
                "backup_id": record.backup_id,
                "status": "completed"
            }
        except Exception as e:
            self.security_audit.log_event(
                AuditEventType.SYSTEM_EVENT,
                initiated_by,
                "backup",
                config_id,
                "failure",
                details={"error": str(e)},
                severity="error"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    def recover_system(
        self,
        backup_id: str,
        initiated_by: str,
        plan_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute system recovery.
        
        Args:
            backup_id: Backup to recover from
            initiated_by: User or system initiating recovery
            plan_id: Optional recovery plan
            
        Returns:
            Recovery result
        """
        try:
            operation = self.backup_recovery.start_recovery(backup_id, plan_id=plan_id)
            
            # Simulate recovery completion
            # In real implementation, would perform actual recovery
            self.backup_recovery.complete_recovery(
                operation.operation_id,
                restored_files=1000,
                failed_files=0,
                success=True
            )
            
            # Log recovery
            self.security_audit.log_event(
                AuditEventType.SYSTEM_EVENT,
                initiated_by,
                "recovery",
                backup_id,
                "success",
                severity="warning"
            )
            
            return {
                "success": True,
                "operation_id": operation.operation_id,
                "status": "completed"
            }
        except Exception as e:
            self.security_audit.log_event(
                AuditEventType.SYSTEM_EVENT,
                initiated_by,
                "recovery",
                backup_id,
                "failure",
                details={"error": str(e)},
                severity="critical"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    def scan_vulnerabilities(
        self,
        scan_type: str,
        targets: List[str],
        initiated_by: str
    ) -> Dict[str, Any]:
        """
        Scan for security vulnerabilities.
        
        Args:
            scan_type: Type of scan (dependencies, code)
            targets: Targets to scan
            initiated_by: User or system initiating scan
            
        Returns:
            Scan result
        """
        if scan_type == "dependencies":
            result = self.vulnerability_scanner.scan_dependencies(targets)
        elif scan_type == "code":
            result = self.vulnerability_scanner.scan_code(targets)
        else:
            return {"error": f"Unknown scan type: {scan_type}"}
        
        # Log scan
        self.security_audit.log_event(
            AuditEventType.SYSTEM_EVENT,
            initiated_by,
            f"vulnerability_scan:{scan_type}",
            ",".join(targets),
            "success",
            severity="info"
        )
        
        return {
            "scan_id": result.scan_id,
            "total_scanned": result.total_scanned,
            "vulnerabilities_found": len(result.vulnerabilities),
            "critical": len([
                v for v in result.vulnerabilities
                if v.severity == Severity.CRITICAL
            ])
        }
    
    def run_compliance_check(
        self,
        standard: Optional[ComplianceStandard] = None
    ) -> Dict[str, Any]:
        """
        Run compliance check.
        
        Args:
            standard: Compliance standard to check
            
        Returns:
            Compliance result
        """
        result = self.security_audit.run_compliance_scan(standard)
        
        # Log compliance check
        self.security_audit.log_event(
            AuditEventType.SYSTEM_EVENT,
            "system",
            "compliance_check",
            standard.value if standard else "all",
            "success",
            severity="info"
        )
        
        return result
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive security dashboard.
        
        Returns:
            Security dashboard data
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "network_policies": self.network_policy.get_statistics(),
            "waf": self.waf.get_statistics(),
            "backups": self.backup_recovery.get_statistics(),
            "audit": self.security_audit.get_statistics(),
            "vulnerabilities": self.vulnerability_scanner.get_statistics()
        }
    
    def get_security_posture(self) -> Dict[str, Any]:
        """
        Get overall security posture assessment.
        
        Returns:
            Security posture assessment
        """
        # Get statistics from all components
        network_stats = self.network_policy.get_statistics()
        waf_stats = self.waf.get_statistics()
        backup_stats = self.backup_recovery.get_statistics()
        vuln_stats = self.vulnerability_scanner.get_statistics()
        
        # Calculate overall score
        scores = []
        
        # Network policy score
        if network_stats["enabled_policies"] > 0:
            scores.append(100)
        else:
            scores.append(50)
        
        # WAF score
        if waf_stats["enabled"]:
            waf_score = 100
            if waf_stats["detections_by_level"].get("critical", 0) > 0:
                waf_score -= 30
            if waf_stats["detections_by_level"].get("high", 0) > 5:
                waf_score -= 20
            scores.append(max(0, waf_score))
        else:
            scores.append(0)
        
        # Backup score
        backup_score = 0
        if backup_stats["completed_backups"] > 0:
            backup_score = 80
            if backup_stats["failed_backups"] == 0:
                backup_score = 100
        scores.append(backup_score)
        
        # Vulnerability score
        vuln_score = 100
        if vuln_stats["vulnerabilities_by_severity"].get("critical", 0) > 0:
            vuln_score -= 50
        if vuln_stats["vulnerabilities_by_severity"].get("high", 0) > 0:
            vuln_score -= 20
        scores.append(max(0, vuln_score))
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Determine status
        if overall_score >= 80:
            status = "excellent"
        elif overall_score >= 60:
            status = "good"
        elif overall_score >= 40:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "overall_score": round(overall_score, 2),
            "status": status,
            "component_scores": {
                "network_policies": scores[0] if len(scores) > 0 else 0,
                "waf": scores[1] if len(scores) > 1 else 0,
                "backups": scores[2] if len(scores) > 2 else 0,
                "vulnerabilities": scores[3] if len(scores) > 3 else 0
            },
            "recommendations": self._generate_recommendations(overall_score, scores)
        }
    
    def _generate_recommendations(
        self,
        overall_score: float,
        component_scores: List[float]
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("URGENT: Security posture needs immediate attention")
        
        if len(component_scores) > 0 and component_scores[0] < 80:
            recommendations.append("Review and enforce network policies")
        
        if len(component_scores) > 1 and component_scores[1] < 80:
            recommendations.append("Review WAF detections and update rules")
        
        if len(component_scores) > 2 and component_scores[2] < 80:
            recommendations.append("Verify backup procedures are working correctly")
        
        if len(component_scores) > 3 and component_scores[3] < 80:
            recommendations.append("Address identified security vulnerabilities")
        
        if overall_score >= 80:
            recommendations.append("Security posture is strong")
            recommendations.append("Continue regular monitoring and auditing")
        
        return recommendations
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.
        
        Returns:
            Compliance report
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "security_posture": self.get_security_posture(),
            "network_policies": {
                "status": self.network_policy.get_statistics(),
                "violations": len(self.network_policy.get_violations())
            },
            "waf_protection": self.waf.generate_security_report(),
            "backup_compliance": self.backup_recovery.generate_compliance_report(),
            "audit_summary": self.security_audit.generate_audit_report(),
            "vulnerability_summary": self.vulnerability_scanner.generate_security_report()
        }
