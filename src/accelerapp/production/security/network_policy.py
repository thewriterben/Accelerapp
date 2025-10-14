"""
Network policy enforcement for cluster-wide security.
Implements Kubernetes-style network policies with enforcement capabilities.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PolicyAction(Enum):
    """Network policy actions."""
    
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"


class PolicyType(Enum):
    """Network policy types."""
    
    INGRESS = "ingress"
    EGRESS = "egress"
    BOTH = "both"


@dataclass
class NetworkRule:
    """Network policy rule."""
    
    rule_id: str
    source_cidr: Optional[str] = None
    destination_cidr: Optional[str] = None
    source_labels: Dict[str, str] = field(default_factory=dict)
    destination_labels: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    action: PolicyAction = PolicyAction.ALLOW


@dataclass
class NetworkPolicy:
    """Cluster-wide network policy."""
    
    policy_id: str
    name: str
    namespace: str
    policy_type: PolicyType
    rules: List[NetworkRule] = field(default_factory=list)
    enabled: bool = True
    priority: int = 100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyViolation:
    """Network policy violation record."""
    
    violation_id: str
    policy_id: str
    source: str
    destination: str
    port: int
    protocol: str
    timestamp: str
    action_taken: str
    details: Dict[str, Any] = field(default_factory=dict)


class NetworkPolicyEnforcer:
    """
    Enforces network policies across clusters.
    Implements policy-based network access control.
    """
    
    def __init__(self):
        """Initialize network policy enforcer."""
        self.policies: Dict[str, NetworkPolicy] = {}
        self.violations: List[PolicyViolation] = []
        self.enforcement_enabled = True
    
    def create_policy(
        self,
        policy_id: str,
        name: str,
        namespace: str,
        policy_type: PolicyType,
        priority: int = 100,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NetworkPolicy:
        """
        Create network policy.
        
        Args:
            policy_id: Policy identifier
            name: Policy name
            namespace: Kubernetes namespace
            policy_type: Policy type (ingress/egress)
            priority: Policy priority (lower = higher priority)
            metadata: Additional metadata
            
        Returns:
            NetworkPolicy
        """
        policy = NetworkPolicy(
            policy_id=policy_id,
            name=name,
            namespace=namespace,
            policy_type=policy_type,
            priority=priority,
            metadata=metadata or {}
        )
        self.policies[policy_id] = policy
        return policy
    
    def add_rule(
        self,
        policy_id: str,
        rule_id: str,
        action: PolicyAction = PolicyAction.ALLOW,
        source_cidr: Optional[str] = None,
        destination_cidr: Optional[str] = None,
        source_labels: Optional[Dict[str, str]] = None,
        destination_labels: Optional[Dict[str, str]] = None,
        ports: Optional[List[int]] = None,
        protocols: Optional[List[str]] = None
    ) -> bool:
        """
        Add rule to network policy.
        
        Args:
            policy_id: Policy identifier
            rule_id: Rule identifier
            action: Rule action
            source_cidr: Source CIDR block
            destination_cidr: Destination CIDR block
            source_labels: Source pod labels
            destination_labels: Destination pod labels
            ports: Allowed ports
            protocols: Allowed protocols
            
        Returns:
            True if rule added successfully
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return False
        
        rule = NetworkRule(
            rule_id=rule_id,
            source_cidr=source_cidr,
            destination_cidr=destination_cidr,
            source_labels=source_labels or {},
            destination_labels=destination_labels or {},
            ports=ports or [],
            protocols=protocols or [],
            action=action
        )
        policy.rules.append(rule)
        return True
    
    def check_connection(
        self,
        source: str,
        destination: str,
        port: int,
        protocol: str,
        source_labels: Optional[Dict[str, str]] = None,
        destination_labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Check if connection is allowed by policies.
        
        Args:
            source: Source IP or identifier
            destination: Destination IP or identifier
            port: Connection port
            protocol: Connection protocol
            source_labels: Source labels
            destination_labels: Destination labels
            
        Returns:
            Check result with allowed status and matched policy
        """
        if not self.enforcement_enabled:
            return {"allowed": True, "reason": "Enforcement disabled"}
        
        # Sort policies by priority
        sorted_policies = sorted(
            self.policies.values(),
            key=lambda p: p.priority
        )
        
        # Check each policy
        for policy in sorted_policies:
            if not policy.enabled:
                continue
            
            for rule in policy.rules:
                if self._rule_matches(
                    rule, source, destination, port, protocol,
                    source_labels or {}, destination_labels or {}
                ):
                    if rule.action == PolicyAction.DENY:
                        self._record_violation(
                            policy.policy_id, source, destination,
                            port, protocol, "DENIED"
                        )
                        return {
                            "allowed": False,
                            "reason": f"Denied by policy {policy.name}",
                            "policy_id": policy.policy_id
                        }
                    elif rule.action == PolicyAction.ALLOW:
                        return {
                            "allowed": True,
                            "reason": f"Allowed by policy {policy.name}",
                            "policy_id": policy.policy_id
                        }
                    elif rule.action == PolicyAction.LOG:
                        self._record_violation(
                            policy.policy_id, source, destination,
                            port, protocol, "LOGGED"
                        )
        
        # Default deny if no matching rule
        self._record_violation(
            "default", source, destination, port, protocol, "DEFAULT_DENY"
        )
        return {
            "allowed": False,
            "reason": "No matching policy found (default deny)"
        }
    
    def _rule_matches(
        self,
        rule: NetworkRule,
        source: str,
        destination: str,
        port: int,
        protocol: str,
        source_labels: Dict[str, str],
        destination_labels: Dict[str, str]
    ) -> bool:
        """Check if rule matches connection parameters."""
        # Check port
        if rule.ports and port not in rule.ports:
            return False
        
        # Check protocol
        if rule.protocols and protocol not in rule.protocols:
            return False
        
        # Check source labels
        if rule.source_labels:
            if not all(
                source_labels.get(k) == v
                for k, v in rule.source_labels.items()
            ):
                return False
        
        # Check destination labels
        if rule.destination_labels:
            if not all(
                destination_labels.get(k) == v
                for k, v in rule.destination_labels.items()
            ):
                return False
        
        return True
    
    def _record_violation(
        self,
        policy_id: str,
        source: str,
        destination: str,
        port: int,
        protocol: str,
        action: str
    ):
        """Record policy violation."""
        violation = PolicyViolation(
            violation_id=f"violation-{len(self.violations) + 1}",
            policy_id=policy_id,
            source=source,
            destination=destination,
            port=port,
            protocol=protocol,
            timestamp=datetime.utcnow().isoformat(),
            action_taken=action
        )
        self.violations.append(violation)
    
    def enable_policy(self, policy_id: str) -> bool:
        """Enable network policy."""
        policy = self.policies.get(policy_id)
        if policy:
            policy.enabled = True
            return True
        return False
    
    def disable_policy(self, policy_id: str) -> bool:
        """Disable network policy."""
        policy = self.policies.get(policy_id)
        if policy:
            policy.enabled = False
            return True
        return False
    
    def list_policies(
        self,
        namespace: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[NetworkPolicy]:
        """
        List network policies.
        
        Args:
            namespace: Filter by namespace
            enabled_only: Only return enabled policies
            
        Returns:
            List of NetworkPolicy
        """
        policies = list(self.policies.values())
        
        if namespace:
            policies = [p for p in policies if p.namespace == namespace]
        
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        
        return policies
    
    def get_violations(
        self,
        policy_id: Optional[str] = None,
        limit: int = 100
    ) -> List[PolicyViolation]:
        """
        Get policy violations.
        
        Args:
            policy_id: Filter by policy ID
            limit: Maximum violations to return
            
        Returns:
            List of PolicyViolation
        """
        violations = self.violations
        
        if policy_id:
            violations = [v for v in violations if v.policy_id == policy_id]
        
        return violations[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get enforcement statistics.
        
        Returns:
            Statistics dictionary
        """
        total_policies = len(self.policies)
        enabled_policies = sum(1 for p in self.policies.values() if p.enabled)
        total_violations = len(self.violations)
        
        violation_by_action = {}
        for violation in self.violations:
            action = violation.action_taken
            violation_by_action[action] = violation_by_action.get(action, 0) + 1
        
        return {
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_violations": total_violations,
            "violations_by_action": violation_by_action,
            "enforcement_enabled": self.enforcement_enabled
        }
    
    def export_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Export policy in Kubernetes format.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy in Kubernetes NetworkPolicy format
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return None
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": policy.name,
                "namespace": policy.namespace
            },
            "spec": {
                "podSelector": policy.metadata.get("podSelector", {}),
                "policyTypes": [policy.policy_type.value.upper()],
                "ingress": self._export_rules(policy.rules, "ingress"),
                "egress": self._export_rules(policy.rules, "egress")
            }
        }
    
    def _export_rules(
        self,
        rules: List[NetworkRule],
        rule_type: str
    ) -> List[Dict[str, Any]]:
        """Export rules in Kubernetes format."""
        exported = []
        for rule in rules:
            rule_spec = {
                "ports": [{"port": p, "protocol": "TCP"} for p in rule.ports]
            }
            if rule.source_labels:
                rule_spec["from"] = [{"podSelector": {"matchLabels": rule.source_labels}}]
            exported.append(rule_spec)
        return exported
