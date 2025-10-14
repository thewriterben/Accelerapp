"""
Enterprise Audit Logger.
Comprehensive audit trails for compliance.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json


@dataclass
class AuditEvent:
    """Represents an audit event."""
    
    event_id: str
    timestamp: str
    tenant_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    status: str  # success, failure
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class EnterpriseAuditLogger:
    """
    Enterprise-grade audit logging system.
    Provides comprehensive audit trails for compliance requirements.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            storage_path: Path to store audit logs
        """
        self.storage_path = storage_path or Path.home() / ".accelerapp" / "audit"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.events: List[AuditEvent] = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load audit events from storage."""
        events_file = self.storage_path / "audit_log.json"
        if events_file.exists():
            try:
                with open(events_file, "r") as f:
                    data = json.load(f)
                    self.events = [AuditEvent(**e) for e in data]
            except Exception:
                self.events = []
    
    def _save_events(self) -> None:
        """Save audit events to storage."""
        events_file = self.storage_path / "audit_log.json"
        with open(events_file, "w") as f:
            json.dump([asdict(e) for e in self.events], f, indent=2)
    
    def log_event(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            action: Action performed
            resource_type: Type of resource
            resource_id: Resource identifier
            status: Event status
            details: Additional details
            ip_address: Optional IP address
            user_agent: Optional user agent
            
        Returns:
            Created AuditEvent instance
        """
        import secrets
        
        event = AuditEvent(
            event_id=secrets.token_urlsafe(16),
            timestamp=datetime.utcnow().isoformat(),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.events.append(event)
        self._save_events()
        
        return event
    
    def query_events(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Query audit events with filters.
        
        Args:
            tenant_id: Optional tenant filter
            user_id: Optional user filter
            action: Optional action filter
            resource_type: Optional resource type filter
            status: Optional status filter
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            limit: Maximum number of events to return
            
        Returns:
            List of matching AuditEvent instances
        """
        filtered_events = self.events
        
        if tenant_id:
            filtered_events = [e for e in filtered_events if e.tenant_id == tenant_id]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if action:
            filtered_events = [e for e in filtered_events if e.action == action]
        
        if resource_type:
            filtered_events = [e for e in filtered_events if e.resource_type == resource_type]
        
        if status:
            filtered_events = [e for e in filtered_events if e.status == status]
        
        if start_time:
            filtered_events = [
                e for e in filtered_events
                if e.timestamp >= start_time
            ]
        
        if end_time:
            filtered_events = [
                e for e in filtered_events
                if e.timestamp <= end_time
            ]
        
        # Sort by timestamp descending
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return filtered_events[:limit]
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[AuditEvent]:
        """
        Get recent activity for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of events
            
        Returns:
            List of AuditEvent instances
        """
        return self.query_events(user_id=user_id, limit=limit)
    
    def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[AuditEvent]:
        """
        Get audit history for a specific resource.
        
        Args:
            resource_type: Resource type
            resource_id: Resource identifier
            limit: Maximum number of events
            
        Returns:
            List of AuditEvent instances
        """
        events = [
            e for e in self.events
            if e.resource_type == resource_type and e.resource_id == resource_id
        ]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def get_statistics(
        self,
        tenant_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics.
        
        Args:
            tenant_id: Optional tenant filter
            start_time: Optional start time
            end_time: Optional end time
            
        Returns:
            Dictionary with statistics
        """
        events = self.query_events(
            tenant_id=tenant_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        # Count by action
        actions = {}
        for event in events:
            actions[event.action] = actions.get(event.action, 0) + 1
        
        # Count by status
        status_counts = {}
        for event in events:
            status_counts[event.status] = status_counts.get(event.status, 0) + 1
        
        # Count by user
        user_activity = {}
        for event in events:
            user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
        
        return {
            "total_events": len(events),
            "actions": actions,
            "status_distribution": status_counts,
            "top_users": sorted(
                user_activity.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
