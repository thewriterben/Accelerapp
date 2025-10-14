"""
Usage analytics and tracking system.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UsageEvent:
    """Represents a usage event."""

    event_id: str
    user_id: str
    event_type: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class UserMetrics:
    """User-level metrics."""

    user_id: str
    total_events: int = 0
    first_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    features_used: List[str] = field(default_factory=list)


class UsageAnalytics:
    """
    Usage analytics and tracking system for feature adoption and user behavior.
    """

    def __init__(self):
        """Initialize usage analytics."""
        self.events: List[UsageEvent] = []
        self.user_metrics: Dict[str, UserMetrics] = {}

    def track_event(
        self, user_id: str, event_type: str, event_data: Optional[Dict[str, Any]] = None
    ) -> UsageEvent:
        """
        Track a usage event.

        Args:
            user_id: User identifier
            event_type: Type of event
            event_data: Optional event data

        Returns:
            Created UsageEvent
        """
        event_id = f"evt-{len(self.events)}"
        event = UsageEvent(
            event_id=event_id,
            user_id=user_id,
            event_type=event_type,
            event_data=event_data or {},
        )

        self.events.append(event)
        self._update_user_metrics(user_id, event_type)

        return event

    def _update_user_metrics(self, user_id: str, event_type: str):
        """Update user metrics."""
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = UserMetrics(user_id=user_id)

        metrics = self.user_metrics[user_id]
        metrics.total_events += 1
        metrics.last_seen = datetime.utcnow().isoformat()

        if event_type not in metrics.features_used:
            metrics.features_used.append(event_type)

    def get_user_metrics(self, user_id: str) -> Optional[UserMetrics]:
        """
        Get metrics for a specific user.

        Args:
            user_id: User identifier

        Returns:
            UserMetrics or None
        """
        return self.user_metrics.get(user_id)

    def get_active_users(self, days: int = 30) -> int:
        """
        Get count of active users in last N days.

        Args:
            days: Number of days

        Returns:
            Active user count
        """
        # Simplified - in real implementation would check timestamps
        return len(self.user_metrics)

    def get_feature_adoption(self) -> Dict[str, int]:
        """
        Get feature adoption metrics.

        Returns:
            Dictionary of feature usage counts
        """
        feature_counts: Dict[str, int] = {}

        for event in self.events:
            event_type = event.event_type
            feature_counts[event_type] = feature_counts.get(event_type, 0) + 1

        return feature_counts

    def get_top_features(self, limit: int = 10) -> List[tuple]:
        """
        Get top used features.

        Args:
            limit: Number of features to return

        Returns:
            List of (feature, count) tuples
        """
        feature_counts = self.get_feature_adoption()
        sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_features[:limit]

    def get_retention_metrics(self) -> Dict[str, Any]:
        """
        Calculate user retention metrics.

        Returns:
            Retention metrics dictionary
        """
        total_users = len(self.user_metrics)
        # Simplified retention calculation
        returning_users = sum(1 for m in self.user_metrics.values() if m.total_events > 1)

        return {
            "total_users": total_users,
            "returning_users": returning_users,
            "retention_rate": (returning_users / total_users * 100) if total_users > 0 else 0,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics statistics.

        Returns:
            Statistics dictionary
        """
        total_events = len(self.events)
        unique_users = len(self.user_metrics)
        feature_adoption = self.get_feature_adoption()
        retention = self.get_retention_metrics()

        return {
            "total_events": total_events,
            "unique_users": unique_users,
            "events_per_user": total_events / unique_users if unique_users > 0 else 0,
            "features_tracked": len(feature_adoption),
            "top_features": self.get_top_features(5),
            "retention": retention,
        }

    def generate_report(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate analytics report.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Analytics report
        """
        stats = self.get_statistics()
        feature_adoption = self.get_feature_adoption()

        return {
            "summary": stats,
            "feature_adoption": feature_adoption,
            "active_users_30d": self.get_active_users(30),
            "retention_metrics": self.get_retention_metrics(),
        }
