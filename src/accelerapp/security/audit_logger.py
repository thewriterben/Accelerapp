"""
Audit logging for security-critical operations.
"""

from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class AuditLogger:
    """Logs security-critical operations for compliance."""

    def __init__(self, log_dir: Path):
        """Initialize audit logger."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.log"
        self.events: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        user: str,
        action: str,
        resource: str,
        success: bool,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Log security event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "user": user,
            "action": action,
            "resource": resource,
            "success": success,
            "metadata": metadata or {},
        }

        self.events.append(event)

        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events."""
        return self.events[-limit:]
