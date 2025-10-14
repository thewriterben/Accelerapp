"""
Data Governance System.
Manages data classification, retention, and privacy controls.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class DataPolicy:
    """Represents a data governance policy."""
    
    policy_id: str
    name: str
    classification: DataClassification
    retention_days: int
    encryption_required: bool
    anonymization_required: bool


class DataGovernor:
    """
    Manages data governance policies and compliance.
    Provides data classification, retention, and privacy controls.
    """
    
    def __init__(self):
        """Initialize data governor."""
        self.policies: Dict[str, DataPolicy] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default data governance policies."""
        self.create_policy(
            "public_data",
            "Public Data",
            DataClassification.PUBLIC,
            retention_days=365,
            encryption_required=False,
            anonymization_required=False
        )
        
        self.create_policy(
            "confidential_data",
            "Confidential Data",
            DataClassification.CONFIDENTIAL,
            retention_days=180,
            encryption_required=True,
            anonymization_required=False
        )
        
        self.create_policy(
            "restricted_data",
            "Restricted Data",
            DataClassification.RESTRICTED,
            retention_days=90,
            encryption_required=True,
            anonymization_required=True
        )
    
    def create_policy(
        self,
        policy_id: str,
        name: str,
        classification: DataClassification,
        retention_days: int,
        encryption_required: bool,
        anonymization_required: bool
    ) -> DataPolicy:
        """
        Create a data governance policy.
        
        Args:
            policy_id: Unique policy identifier
            name: Policy name
            classification: Data classification level
            retention_days: Data retention period in days
            encryption_required: Whether encryption is required
            anonymization_required: Whether anonymization is required
            
        Returns:
            Created DataPolicy instance
        """
        policy = DataPolicy(
            policy_id=policy_id,
            name=name,
            classification=classification,
            retention_days=retention_days,
            encryption_required=encryption_required,
            anonymization_required=anonymization_required
        )
        
        self.policies[policy_id] = policy
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[DataPolicy]:
        """
        Get a data governance policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            DataPolicy instance or None
        """
        return self.policies.get(policy_id)
    
    def classify_data(
        self,
        data_type: str,
        contains_pii: bool = False,
        contains_sensitive: bool = False
    ) -> DataClassification:
        """
        Classify data based on type and content.
        
        Args:
            data_type: Type of data
            contains_pii: Whether data contains PII
            contains_sensitive: Whether data contains sensitive information
            
        Returns:
            Recommended DataClassification
        """
        if contains_pii or contains_sensitive:
            return DataClassification.RESTRICTED
        elif data_type in ["user_data", "config", "credentials"]:
            return DataClassification.CONFIDENTIAL
        elif data_type in ["system_logs", "metrics"]:
            return DataClassification.INTERNAL
        else:
            return DataClassification.PUBLIC
    
    def check_compliance(
        self,
        data_classification: DataClassification,
        encryption_enabled: bool,
        anonymization_enabled: bool
    ) -> Dict[str, Any]:
        """
        Check if data handling complies with policies.
        
        Args:
            data_classification: Classification of the data
            encryption_enabled: Whether encryption is enabled
            anonymization_enabled: Whether anonymization is enabled
            
        Returns:
            Dictionary with compliance check results
        """
        # Find matching policy
        matching_policy = None
        for policy in self.policies.values():
            if policy.classification == data_classification:
                matching_policy = policy
                break
        
        if not matching_policy:
            return {
                "compliant": False,
                "reason": "No policy found for classification"
            }
        
        issues = []
        
        if matching_policy.encryption_required and not encryption_enabled:
            issues.append("Encryption required but not enabled")
        
        if matching_policy.anonymization_required and not anonymization_enabled:
            issues.append("Anonymization required but not enabled")
        
        return {
            "compliant": len(issues) == 0,
            "policy": matching_policy.policy_id,
            "issues": issues
        }
    
    def list_policies(self) -> List[DataPolicy]:
        """
        List all data governance policies.
        
        Returns:
            List of DataPolicy instances
        """
        return list(self.policies.values())
