"""
Continuous authentication and behavioral analysis for zero-trust architecture.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics


class TrustLevel(Enum):
    """Device trust levels."""
    UNTRUSTED = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    FULL = 100


@dataclass
class BehaviorMetrics:
    """Device behavior metrics."""
    
    request_count: int = 0
    failed_auth_count: int = 0
    avg_response_time: float = 0.0
    last_activity: Optional[datetime] = None
    suspicious_activities: List[str] = field(default_factory=list)
    
    def update_activity(self, response_time: float):
        """Update activity metrics."""
        self.request_count += 1
        self.last_activity = datetime.now()
        
        # Update moving average of response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.9 + response_time * 0.1)


@dataclass
class DeviceSession:
    """Active device session."""
    
    device_id: str
    session_id: str
    started_at: datetime
    last_activity: datetime
    trust_score: float = 100.0
    metrics: BehaviorMetrics = field(default_factory=BehaviorMetrics)
    authenticated: bool = True
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if session is still active."""
        if not self.authenticated:
            return False
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout


class DeviceAuthenticationService:
    """Continuous authentication and behavioral analysis service."""
    
    def __init__(self, identity_manager):
        """
        Initialize authentication service.
        
        Args:
            identity_manager: Device identity manager instance
        """
        self.identity_manager = identity_manager
        self._sessions: Dict[str, DeviceSession] = {}
        self._behavior_history: Dict[str, List[BehaviorMetrics]] = {}
        self._anomaly_threshold = 0.7  # Threshold for anomaly detection
    
    def authenticate_device(
        self,
        device_id: str,
        fingerprint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Authenticate device and create session.
        
        Args:
            device_id: Device identifier
            fingerprint: Device fingerprint
            metadata: Additional authentication metadata
            
        Returns:
            Session ID if authenticated, None otherwise
        """
        # Verify identity
        if not self.identity_manager.verify_identity(device_id, fingerprint):
            self._record_failed_auth(device_id)
            return None
        
        # Create session
        import secrets
        session_id = secrets.token_hex(16)
        
        session = DeviceSession(
            device_id=device_id,
            session_id=session_id,
            started_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self._sessions[session_id] = session
        return session_id
    
    def verify_session(self, session_id: str) -> bool:
        """
        Verify active session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session is valid and active
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        return session.is_active()
    
    def update_trust_score(
        self,
        session_id: str,
        response_time: float,
        success: bool = True
    ) -> float:
        """
        Update device trust score based on behavior.
        
        Args:
            session_id: Session identifier
            response_time: Operation response time
            success: Whether operation succeeded
            
        Returns:
            Updated trust score
        """
        session = self._sessions.get(session_id)
        if not session:
            return 0.0
        
        # Update metrics
        session.metrics.update_activity(response_time)
        session.last_activity = datetime.now()
        
        if not success:
            session.metrics.failed_auth_count += 1
        
        # Calculate trust score adjustments
        trust_adjustment = 0.0
        
        # Penalize for failed operations
        if not success:
            trust_adjustment -= 5.0
        
        # Penalize for anomalous response times
        if self._is_anomalous_response_time(session.device_id, response_time):
            trust_adjustment -= 2.0
            session.metrics.suspicious_activities.append(
                f"Anomalous response time: {response_time:.3f}s at {datetime.now()}"
            )
        
        # Penalize for high failure rate
        if session.metrics.request_count > 10:
            failure_rate = session.metrics.failed_auth_count / session.metrics.request_count
            if failure_rate > 0.1:
                trust_adjustment -= 10.0
        
        # Update trust score (bounded between 0 and 100)
        session.trust_score = max(0.0, min(100.0, session.trust_score + trust_adjustment))
        
        # Reward good behavior over time
        if success and trust_adjustment == 0:
            session.trust_score = min(100.0, session.trust_score + 0.1)
        
        return session.trust_score
    
    def get_trust_level(self, session_id: str) -> TrustLevel:
        """
        Get device trust level.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Trust level
        """
        session = self._sessions.get(session_id)
        if not session:
            return TrustLevel.UNTRUSTED
        
        score = session.trust_score
        
        if score >= 90:
            return TrustLevel.FULL
        elif score >= 70:
            return TrustLevel.HIGH
        elif score >= 50:
            return TrustLevel.MEDIUM
        elif score >= 25:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    def _is_anomalous_response_time(self, device_id: str, response_time: float) -> bool:
        """
        Detect anomalous response times using historical data.
        
        Args:
            device_id: Device identifier
            response_time: Current response time
            
        Returns:
            True if response time is anomalous
        """
        history = self._behavior_history.get(device_id, [])
        if len(history) < 10:
            # Not enough data for anomaly detection
            self._record_behavior(device_id, response_time)
            return False
        
        # Get recent response times
        recent_times = [m.avg_response_time for m in history[-20:]]
        
        # Calculate statistics
        mean = statistics.mean(recent_times)
        stdev = statistics.stdev(recent_times) if len(recent_times) > 1 else 0
        
        # Record current behavior
        self._record_behavior(device_id, response_time)
        
        # Detect anomaly (more than 3 standard deviations from mean)
        if stdev > 0:
            z_score = abs(response_time - mean) / stdev
            return z_score > 3
        
        return False
    
    def _record_behavior(self, device_id: str, response_time: float):
        """Record device behavior for analysis."""
        if device_id not in self._behavior_history:
            self._behavior_history[device_id] = []
        
        metrics = BehaviorMetrics()
        metrics.avg_response_time = response_time
        metrics.last_activity = datetime.now()
        
        self._behavior_history[device_id].append(metrics)
        
        # Keep only recent history (last 100 entries)
        if len(self._behavior_history[device_id]) > 100:
            self._behavior_history[device_id] = self._behavior_history[device_id][-100:]
    
    def _record_failed_auth(self, device_id: str):
        """Record failed authentication attempt."""
        if device_id not in self._behavior_history:
            self._behavior_history[device_id] = []
        
        metrics = BehaviorMetrics()
        metrics.failed_auth_count = 1
        metrics.suspicious_activities.append(
            f"Failed authentication at {datetime.now()}"
        )
        
        self._behavior_history[device_id].append(metrics)
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate device session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if terminated successfully
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information or None
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        return {
            "device_id": session.device_id,
            "session_id": session.session_id,
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "trust_score": session.trust_score,
            "trust_level": self.get_trust_level(session_id).name,
            "authenticated": session.authenticated,
            "metrics": {
                "request_count": session.metrics.request_count,
                "failed_auth_count": session.metrics.failed_auth_count,
                "avg_response_time": session.metrics.avg_response_time,
                "suspicious_activities": session.metrics.suspicious_activities
            }
        }
    
    def get_device_statistics(self, device_id: str) -> Dict[str, Any]:
        """
        Get device behavior statistics.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Statistics dictionary
        """
        history = self._behavior_history.get(device_id, [])
        
        if not history:
            return {"device_id": device_id, "no_data": True}
        
        total_requests = sum(m.request_count for m in history)
        total_failures = sum(m.failed_auth_count for m in history)
        avg_response_times = [m.avg_response_time for m in history if m.avg_response_time > 0]
        
        return {
            "device_id": device_id,
            "total_requests": total_requests,
            "total_failures": total_failures,
            "failure_rate": total_failures / total_requests if total_requests > 0 else 0,
            "avg_response_time": statistics.mean(avg_response_times) if avg_response_times else 0,
            "history_entries": len(history),
            "suspicious_activities": sum(len(m.suspicious_activities) for m in history)
        }
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 30) -> int:
        """
        Clean up inactive sessions.
        
        Args:
            timeout_minutes: Session timeout in minutes
            
        Returns:
            Number of sessions cleaned up
        """
        inactive = []
        for session_id, session in self._sessions.items():
            if not session.is_active(timeout_minutes):
                inactive.append(session_id)
        
        for session_id in inactive:
            del self._sessions[session_id]
        
        return len(inactive)
