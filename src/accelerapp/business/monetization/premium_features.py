"""
Premium features and monetization management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SubscriptionTier(Enum):
    """Subscription tier levels."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class Feature:
    """Represents a platform feature."""

    id: str
    name: str
    description: str
    tier: SubscriptionTier
    enabled_by_default: bool = False


@dataclass
class Subscription:
    """Represents a user subscription."""

    user_id: str
    tier: SubscriptionTier
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    auto_renew: bool = True
    features: List[str] = field(default_factory=list)


class PremiumFeatureManager:
    """
    Manages premium features and subscription tiers.
    """

    def __init__(self):
        """Initialize premium feature manager."""
        self.features: Dict[str, Feature] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self._initialize_features()

    def _initialize_features(self):
        """Initialize feature catalog."""
        features = [
            # Free tier
            Feature(
                id="code-generation",
                name="Basic Code Generation",
                description="Generate firmware for Arduino, ESP32, and STM32",
                tier=SubscriptionTier.FREE,
                enabled_by_default=True,
            ),
            Feature(
                id="templates",
                name="Community Templates",
                description="Access to community-contributed templates",
                tier=SubscriptionTier.FREE,
                enabled_by_default=True,
            ),
            # Basic tier
            Feature(
                id="advanced-templates",
                name="Advanced Templates",
                description="Premium templates and configurations",
                tier=SubscriptionTier.BASIC,
            ),
            Feature(
                id="cloud-generation",
                name="Cloud Generation",
                description="Use cloud-based generation service",
                tier=SubscriptionTier.BASIC,
            ),
            Feature(
                id="priority-support",
                name="Priority Support",
                description="Priority email support",
                tier=SubscriptionTier.BASIC,
            ),
            # Professional tier
            Feature(
                id="ai-optimization",
                name="AI Code Optimization",
                description="AI-powered code optimization and analysis",
                tier=SubscriptionTier.PROFESSIONAL,
            ),
            Feature(
                id="team-collaboration",
                name="Team Collaboration",
                description="Share projects with team members",
                tier=SubscriptionTier.PROFESSIONAL,
            ),
            Feature(
                id="advanced-analytics",
                name="Advanced Analytics",
                description="Detailed usage analytics and insights",
                tier=SubscriptionTier.PROFESSIONAL,
            ),
            # Enterprise tier
            Feature(
                id="sso",
                name="Single Sign-On",
                description="SSO integration with corporate identity providers",
                tier=SubscriptionTier.ENTERPRISE,
            ),
            Feature(
                id="dedicated-support",
                name="Dedicated Support",
                description="24/7 dedicated support with SLA",
                tier=SubscriptionTier.ENTERPRISE,
            ),
            Feature(
                id="on-premise",
                name="On-Premise Deployment",
                description="Self-hosted deployment options",
                tier=SubscriptionTier.ENTERPRISE,
            ),
            Feature(
                id="custom-integrations",
                name="Custom Integrations",
                description="Custom integration development support",
                tier=SubscriptionTier.ENTERPRISE,
            ),
        ]

        for feature in features:
            self.features[feature.id] = feature

    def create_subscription(
        self, user_id: str, tier: SubscriptionTier, expires_at: Optional[str] = None
    ) -> Subscription:
        """
        Create a new subscription.

        Args:
            user_id: User identifier
            tier: Subscription tier
            expires_at: Optional expiration date

        Returns:
            Created Subscription
        """
        # Get features for tier
        tier_features = [
            f.id
            for f in self.features.values()
            if f.tier.value <= tier.value or f.enabled_by_default
        ]

        subscription = Subscription(
            user_id=user_id, tier=tier, expires_at=expires_at, features=tier_features
        )

        self.subscriptions[user_id] = subscription
        return subscription

    def upgrade_subscription(self, user_id: str, new_tier: SubscriptionTier) -> bool:
        """
        Upgrade user subscription.

        Args:
            user_id: User identifier
            new_tier: New subscription tier

        Returns:
            True if successful
        """
        if user_id not in self.subscriptions:
            return False

        subscription = self.subscriptions[user_id]
        subscription.tier = new_tier

        # Update features
        tier_features = [
            f.id
            for f in self.features.values()
            if f.tier.value <= new_tier.value or f.enabled_by_default
        ]
        subscription.features = tier_features

        return True

    def check_feature_access(self, user_id: str, feature_id: str) -> bool:
        """
        Check if user has access to a feature.

        Args:
            user_id: User identifier
            feature_id: Feature identifier

        Returns:
            True if user has access
        """
        if user_id not in self.subscriptions:
            # No subscription - only free features
            feature = self.features.get(feature_id)
            return feature is not None and feature.tier == SubscriptionTier.FREE

        subscription = self.subscriptions[user_id]
        return feature_id in subscription.features

    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """
        Get user subscription.

        Args:
            user_id: User identifier

        Returns:
            Subscription or None
        """
        return self.subscriptions.get(user_id)

    def list_features(self, tier: Optional[SubscriptionTier] = None) -> List[Feature]:
        """
        List features, optionally filtered by tier.

        Args:
            tier: Optional tier filter

        Returns:
            List of Feature
        """
        features = list(self.features.values())

        if tier:
            features = [f for f in features if f.tier == tier]

        return features

    def get_tier_pricing(self) -> Dict[str, Dict[str, Any]]:
        """
        Get pricing information for all tiers.

        Returns:
            Pricing dictionary
        """
        return {
            "free": {
                "name": "Free",
                "price_monthly": 0,
                "price_yearly": 0,
                "description": "Perfect for hobbyists and learning",
                "features": [
                    f.name for f in self.features.values() if f.tier == SubscriptionTier.FREE
                ],
            },
            "basic": {
                "name": "Basic",
                "price_monthly": 19,
                "price_yearly": 190,
                "description": "For individual developers",
                "features": [
                    f.name
                    for f in self.features.values()
                    if f.tier == SubscriptionTier.BASIC or f.tier == SubscriptionTier.FREE
                ],
            },
            "professional": {
                "name": "Professional",
                "price_monthly": 49,
                "price_yearly": 490,
                "description": "For professional teams",
                "features": [
                    f.name
                    for f in self.features.values()
                    if f.tier.value <= SubscriptionTier.PROFESSIONAL.value
                ],
            },
            "enterprise": {
                "name": "Enterprise",
                "price_monthly": "Custom",
                "price_yearly": "Custom",
                "description": "For large organizations",
                "features": [f.name for f in self.features.values()],
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get subscription statistics.

        Returns:
            Statistics dictionary
        """
        total_subscriptions = len(self.subscriptions)
        by_tier = {
            "free": 0,
            "basic": 0,
            "professional": 0,
            "enterprise": 0,
        }

        for subscription in self.subscriptions.values():
            by_tier[subscription.tier.value] += 1

        return {
            "total_subscriptions": total_subscriptions,
            "by_tier": by_tier,
            "total_features": len(self.features),
        }
