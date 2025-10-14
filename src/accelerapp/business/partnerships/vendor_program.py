"""
Partnership and vendor program management.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PartnerType(Enum):
    """Partner types."""

    HARDWARE_VENDOR = "hardware_vendor"
    CLOUD_PROVIDER = "cloud_provider"
    TECHNOLOGY_PARTNER = "technology_partner"
    RESELLER = "reseller"


class PartnerTier(Enum):
    """Partner tier levels."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass
class Partner:
    """Represents a partner."""

    partner_id: str
    name: str
    partner_type: PartnerType
    tier: PartnerTier
    contact_email: str
    website: Optional[str] = None
    joined_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    integrations: List[str] = field(default_factory=list)
    is_active: bool = True


class PartnershipManager:
    """
    Manages partnerships, vendor programs, and technology integrations.
    """

    def __init__(self):
        """Initialize partnership manager."""
        self.partners: Dict[str, Partner] = {}
        self._initialize_default_partners()

    def _initialize_default_partners(self):
        """Initialize default partner relationships."""
        default_partners = [
            Partner(
                partner_id="arduino",
                name="Arduino",
                partner_type=PartnerType.HARDWARE_VENDOR,
                tier=PartnerTier.GOLD,
                contact_email="partnerships@arduino.cc",
                website="https://arduino.cc",
                integrations=["arduino_ide", "arduino_cli"],
            ),
            Partner(
                partner_id="espressif",
                name="Espressif Systems",
                partner_type=PartnerType.HARDWARE_VENDOR,
                tier=PartnerTier.GOLD,
                contact_email="sales@espressif.com",
                website="https://www.espressif.com",
                integrations=["esp_idf", "arduino_core_esp32"],
            ),
            Partner(
                partner_id="aws",
                name="Amazon Web Services",
                partner_type=PartnerType.CLOUD_PROVIDER,
                tier=PartnerTier.PLATINUM,
                contact_email="partnerships@aws.com",
                website="https://aws.amazon.com",
                integrations=["aws_iot_core", "aws_lambda", "aws_marketplace"],
            ),
            Partner(
                partner_id="microsoft",
                name="Microsoft Azure",
                partner_type=PartnerType.CLOUD_PROVIDER,
                tier=PartnerTier.PLATINUM,
                contact_email="partnerships@microsoft.com",
                website="https://azure.microsoft.com",
                integrations=["azure_iot_hub", "azure_functions", "azure_marketplace"],
            ),
        ]

        for partner in default_partners:
            self.partners[partner.partner_id] = partner

    def register_partner(
        self,
        partner_id: str,
        name: str,
        partner_type: PartnerType,
        tier: PartnerTier,
        contact_email: str,
        website: Optional[str] = None,
        integrations: Optional[List[str]] = None,
    ) -> Partner:
        """
        Register a new partner.

        Args:
            partner_id: Partner identifier
            name: Partner name
            partner_type: Type of partner
            tier: Partner tier
            contact_email: Contact email
            website: Optional website
            integrations: Optional list of integrations

        Returns:
            Created Partner
        """
        partner = Partner(
            partner_id=partner_id,
            name=name,
            partner_type=partner_type,
            tier=tier,
            contact_email=contact_email,
            website=website,
            integrations=integrations or [],
        )

        self.partners[partner_id] = partner
        return partner

    def get_partner(self, partner_id: str) -> Optional[Partner]:
        """
        Get partner details.

        Args:
            partner_id: Partner identifier

        Returns:
            Partner or None
        """
        return self.partners.get(partner_id)

    def list_partners(
        self,
        partner_type: Optional[PartnerType] = None,
        tier: Optional[PartnerTier] = None,
        active_only: bool = True,
    ) -> List[Partner]:
        """
        List partners with optional filters.

        Args:
            partner_type: Optional partner type filter
            tier: Optional tier filter
            active_only: Only show active partners

        Returns:
            List of Partner
        """
        partners = list(self.partners.values())

        if active_only:
            partners = [p for p in partners if p.is_active]

        if partner_type:
            partners = [p for p in partners if p.partner_type == partner_type]

        if tier:
            partners = [p for p in partners if p.tier == tier]

        return partners

    def add_integration(self, partner_id: str, integration_name: str) -> bool:
        """
        Add an integration for a partner.

        Args:
            partner_id: Partner identifier
            integration_name: Integration name

        Returns:
            True if successful
        """
        if partner_id not in self.partners:
            return False

        partner = self.partners[partner_id]
        if integration_name not in partner.integrations:
            partner.integrations.append(integration_name)
            return True

        return False

    def upgrade_partner_tier(self, partner_id: str, new_tier: PartnerTier) -> bool:
        """
        Upgrade partner tier.

        Args:
            partner_id: Partner identifier
            new_tier: New tier level

        Returns:
            True if successful
        """
        if partner_id not in self.partners:
            return False

        self.partners[partner_id].tier = new_tier
        return True

    def deactivate_partner(self, partner_id: str) -> bool:
        """
        Deactivate a partner.

        Args:
            partner_id: Partner identifier

        Returns:
            True if successful
        """
        if partner_id not in self.partners:
            return False

        self.partners[partner_id].is_active = False
        return True

    def get_partner_benefits(self, tier: PartnerTier) -> List[str]:
        """
        Get benefits for a partner tier.

        Args:
            tier: Partner tier

        Returns:
            List of benefits
        """
        benefits = {
            PartnerTier.BRONZE: [
                "Listed in partner directory",
                "Access to partner resources",
                "Quarterly business reviews",
            ],
            PartnerTier.SILVER: [
                "All Bronze benefits",
                "Featured placement in directory",
                "Co-marketing opportunities",
                "Monthly business reviews",
            ],
            PartnerTier.GOLD: [
                "All Silver benefits",
                "Priority technical support",
                "Joint case studies",
                "Weekly sync meetings",
                "Early access to new features",
            ],
            PartnerTier.PLATINUM: [
                "All Gold benefits",
                "Dedicated partner manager",
                "Custom integration support",
                "Executive sponsorship",
                "Co-development opportunities",
            ],
        }

        return benefits.get(tier, [])

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get partnership statistics.

        Returns:
            Statistics dictionary
        """
        total_partners = len(self.partners)
        active_partners = sum(1 for p in self.partners.values() if p.is_active)

        by_type = {}
        by_tier = {}

        for partner in self.partners.values():
            if partner.is_active:
                by_type[partner.partner_type.value] = by_type.get(partner.partner_type.value, 0) + 1
                by_tier[partner.tier.value] = by_tier.get(partner.tier.value, 0) + 1

        return {
            "total_partners": total_partners,
            "active_partners": active_partners,
            "by_type": by_type,
            "by_tier": by_tier,
        }
