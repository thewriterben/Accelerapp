"""
Comprehensive security auditing and compliance system.
Tracks security events, generates audit trails, and ensures compliance.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class AuditEventType(Enum):
    """Audit event types."""
    
    ACCESS = "access"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    POLICY_CHANGE = "policy_change"
    SYSTEM_EVENT = "system_event"


class ComplianceStandard(Enum):
    """Compliance standards."""
    
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"


@dataclass
class AuditEvent:
    """Security audit event."""
    
    event_id: str
    event_type: AuditEventType
    timestamp: str
    actor: str
    action: str
    resource: str
    result: str  # success, failure, denied
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical


@dataclass
class ComplianceCheck:
    """Compliance check definition."""
    
    check_id: str
    name: str
    standard: ComplianceStandard
    description: str
    check_function: Optional[str] = None
    remediation: str = ""
    severity: str = "medium"


@dataclass
class ComplianceResult:
    """Compliance check result."""
    
    check_id: str
    passed: bool
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    score: float = 0.0


class SecurityAuditSystem:
    """
    Comprehensive security auditing and compliance system.
    Tracks events, generates audit trails, and ensures compliance.
    """
    
    def __init__(self):
        """Initialize security audit system."""
        self.events: List[AuditEvent] = []
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.compliance_results: List[ComplianceResult] = []
        self.audit_enabled = True
        
        # Initialize compliance checks
        self._init_compliance_checks()
    
    def _init_compliance_checks(self):
        """Initialize default compliance checks."""
        # SOC2 checks
        self.add_compliance_check(
            "soc2-access-control",
            "Access Control Implementation",
            ComplianceStandard.SOC2,
            "Verify access controls are properly implemented",
            remediation="Implement role-based access control"
        )
        
        self.add_compliance_check(
            "soc2-audit-logging",
            "Audit Logging",
            ComplianceStandard.SOC2,
            "Verify comprehensive audit logging is enabled",
            remediation="Enable audit logging for all security events"
        )
        
        # ISO 27001 checks
        self.add_compliance_check(
            "iso27001-encryption",
            "Data Encryption",
            ComplianceStandard.ISO27001,
            "Verify data encryption at rest and in transit",
            remediation="Implement encryption for sensitive data"
        )
        
        self.add_compliance_check(
            "iso27001-backup",
            "Backup Procedures",
            ComplianceStandard.ISO27001,
            "Verify automated backup procedures are in place",
            remediation="Configure automated backups with retention policies"
        )
    
    def add_compliance_check(
        self,
        check_id: str,
        name: str,
        standard: ComplianceStandard,
        description: str,
        remediation: str = "",
        severity: str = "medium"
    ) -> ComplianceCheck:
        """
        Add compliance check.
        
        Args:
            check_id: Check identifier
            name: Check name
            standard: Compliance standard
            description: Check description
            remediation: Remediation steps
            severity: Check severity
            
        Returns:
            ComplianceCheck
        """
        check = ComplianceCheck(
            check_id=check_id,
            name=name,
            standard=standard,
            description=description,
            remediation=remediation,
            severity=severity
        )
        self.compliance_checks[check_id] = check
        return check
    
    def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        resource: str,
        result: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> AuditEvent:
        """
        Log security audit event.
        
        Args:
            event_type: Type of event
            actor: User or system performing action
            action: Action performed
            resource: Resource affected
            result: Action result
            ip_address: Source IP address
            user_agent: User agent string
            details: Additional details
            severity: Event severity
            
        Returns:
            AuditEvent
        """
        if not self.audit_enabled:
            return None
        
        event = AuditEvent(
            event_id=f"event-{len(self.events) + 1}",
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat(),
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            severity=severity
        )
        
        self.events.append(event)
        return event
    
    def run_compliance_check(
        self,
        check_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Run compliance check.
        
        Args:
            check_id: Check identifier
            context: Check context data
            
        Returns:
            ComplianceResult
        """
        check = self.compliance_checks.get(check_id)
        if not check:
            raise ValueError(f"Check {check_id} not found")
        
        # Simulate check execution
        # In real implementation, would execute actual checks
        passed = True
        findings = []
        score = 100.0
        
        # Example checks based on check_id
        if check_id == "soc2-audit-logging":
            if not self.audit_enabled:
                passed = False
                findings.append("Audit logging is disabled")
                score = 0.0
        
        if check_id == "soc2-access-control":
            # Would check actual access control implementation
            pass
        
        result = ComplianceResult(
            check_id=check_id,
            passed=passed,
            timestamp=datetime.utcnow().isoformat(),
            details=context or {},
            findings=findings,
            score=score
        )
        
        self.compliance_results.append(result)
        return result
    
    def run_compliance_scan(
        self,
        standard: Optional[ComplianceStandard] = None
    ) -> Dict[str, Any]:
        """
        Run full compliance scan.
        
        Args:
            standard: Filter by compliance standard
            
        Returns:
            Scan results
        """
        checks = self.compliance_checks.values()
        if standard:
            checks = [c for c in checks if c.standard == standard]
        
        results = []
        for check in checks:
            result = self.run_compliance_check(check.check_id)
            results.append(result)
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.passed)
        avg_score = sum(r.score for r in results) / total_checks if total_checks else 0
        
        return {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "standard": standard.value if standard else "all",
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "compliance_score": round(avg_score, 2),
            "results": [
                {
                    "check_id": r.check_id,
                    "passed": r.passed,
                    "score": r.score,
                    "findings": r.findings
                }
                for r in results
            ]
        }
    
    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Get audit events with filters.
        
        Args:
            event_type: Filter by event type
            actor: Filter by actor
            start_time: Filter by start time
            end_time: Filter by end time
            severity: Filter by severity
            limit: Maximum events to return
            
        Returns:
            List of AuditEvent
        """
        events = self.events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if actor:
            events = [e for e in events if e.actor == actor]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if start_time:
            events = [
                e for e in events
                if datetime.fromisoformat(e.timestamp) >= start_time
            ]
        
        if end_time:
            events = [
                e for e in events
                if datetime.fromisoformat(e.timestamp) <= end_time
            ]
        
        return events[-limit:]
    
    def get_security_violations(self, limit: int = 100) -> List[AuditEvent]:
        """
        Get security violation events.
        
        Args:
            limit: Maximum violations to return
            
        Returns:
            List of security violations
        """
        return self.get_events(
            event_type=AuditEventType.SECURITY_VIOLATION,
            limit=limit
        )
    
    def get_failed_authentications(
        self,
        actor: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Get failed authentication attempts.
        
        Args:
            actor: Filter by actor
            limit: Maximum events to return
            
        Returns:
            List of failed authentication events
        """
        events = self.get_events(
            event_type=AuditEventType.AUTHENTICATION,
            actor=actor,
            limit=limit
        )
        return [e for e in events if e.result == "failure"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Returns:
            Statistics dictionary
        """
        total_events = len(self.events)
        
        events_by_type = {}
        for event in self.events:
            event_type = event.event_type.value
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
        events_by_severity = {
            "info": 0,
            "warning": 0,
            "error": 0,
            "critical": 0
        }
        for event in self.events:
            events_by_severity[event.severity] += 1
        
        return {
            "audit_enabled": self.audit_enabled,
            "total_events": total_events,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "compliance_checks": len(self.compliance_checks),
            "compliance_scans": len(self.compliance_results)
        }
    
    def generate_audit_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report.
        
        Args:
            start_time: Report start time
            end_time: Report end time
            
        Returns:
            Audit report
        """
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=30)
        if not end_time:
            end_time = datetime.utcnow()
        
        events = self.get_events(start_time=start_time, end_time=end_time, limit=10000)
        
        # Analyze events
        security_violations = [
            e for e in events
            if e.event_type == AuditEventType.SECURITY_VIOLATION
        ]
        
        failed_auths = [
            e for e in events
            if e.event_type == AuditEventType.AUTHENTICATION and e.result == "failure"
        ]
        
        critical_events = [e for e in events if e.severity == "critical"]
        
        # Get unique actors
        actors = set(e.actor for e in events)
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "total_events": len(events),
                "unique_actors": len(actors),
                "security_violations": len(security_violations),
                "failed_authentications": len(failed_auths),
                "critical_events": len(critical_events)
            },
            "top_actors": self._get_top_actors(events),
            "top_resources": self._get_top_resources(events),
            "recent_critical_events": [
                {
                    "timestamp": e.timestamp,
                    "actor": e.actor,
                    "action": e.action,
                    "resource": e.resource
                }
                for e in critical_events[-10:]
            ]
        }
    
    def _get_top_actors(self, events: List[AuditEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top actors by event count."""
        actor_counts = {}
        for event in events:
            actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1
        
        top_actors = sorted(
            actor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"actor": actor, "event_count": count}
            for actor, count in top_actors
        ]
    
    def _get_top_resources(self, events: List[AuditEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top resources by access count."""
        resource_counts = {}
        for event in events:
            resource_counts[event.resource] = resource_counts.get(event.resource, 0) + 1
        
        top_resources = sorted(
            resource_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"resource": resource, "access_count": count}
            for resource, count in top_resources
        ]
    
    def export_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """
        Export audit trail for compliance.
        
        Args:
            start_time: Export start time
            end_time: Export end time
            format: Export format (json, csv)
            
        Returns:
            Exported audit trail as string
        """
        events = self.get_events(start_time=start_time, end_time=end_time, limit=100000)
        
        if format == "json":
            import json
            return json.dumps([
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp,
                    "event_type": e.event_type.value,
                    "actor": e.actor,
                    "action": e.action,
                    "resource": e.resource,
                    "result": e.result,
                    "severity": e.severity
                }
                for e in events
            ], indent=2)
        
        return str(events)
