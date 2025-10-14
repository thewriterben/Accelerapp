"""
Collaboration protocols for agent interaction.
Defines rules and patterns for agent collaboration.
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass


class ProtocolType(Enum):
    """Types of collaboration protocols."""

    REQUEST_RESPONSE = "request_response"
    BROADCAST = "broadcast"
    CONSENSUS = "consensus"
    HANDOFF = "handoff"
    REVIEW = "review"


@dataclass
class ProtocolRule:
    """Rule for a collaboration protocol."""

    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Any]
    priority: int = 1


class CollaborationProtocol:
    """
    Base class for collaboration protocols.
    Defines how agents interact and coordinate.
    """

    def __init__(self, protocol_type: ProtocolType):
        """
        Initialize collaboration protocol.

        Args:
            protocol_type: Type of protocol
        """
        self.protocol_type = protocol_type
        self.rules: List[ProtocolRule] = []
        self.metadata: Dict[str, Any] = {}

    def add_rule(self, rule: ProtocolRule) -> None:
        """
        Add a protocol rule.

        Args:
            rule: Protocol rule to add
        """
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute protocol with given context.

        Args:
            context: Execution context

        Returns:
            Protocol result
        """
        for rule in self.rules:
            try:
                if rule.condition(context):
                    return rule.action(context)
            except Exception as e:
                print(f"Error executing rule {rule.name}: {e}")

        return None

    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate context against protocol requirements.

        Args:
            context: Context to validate

        Returns:
            True if valid
        """
        required_keys = self.metadata.get("required_keys", [])
        return all(key in context for key in required_keys)


class RequestResponseProtocol(CollaborationProtocol):
    """
    Request-response protocol for agent communication.
    One agent requests, another responds.
    """

    def __init__(self):
        """Initialize request-response protocol."""
        super().__init__(ProtocolType.REQUEST_RESPONSE)
        self.metadata["required_keys"] = ["requester", "request_type", "data"]

        # Add default rule for basic request-response
        self.add_rule(
            ProtocolRule(
                name="basic_response",
                condition=lambda ctx: "request_type" in ctx,
                action=lambda ctx: {
                    "status": "received",
                    "request_type": ctx.get("request_type"),
                    "requester": ctx.get("requester"),
                },
                priority=1,
            )
        )


class BroadcastProtocol(CollaborationProtocol):
    """
    Broadcast protocol for one-to-many communication.
    One agent broadcasts to all listening agents.
    """

    def __init__(self):
        """Initialize broadcast protocol."""
        super().__init__(ProtocolType.BROADCAST)
        self.metadata["required_keys"] = ["broadcaster", "message"]


class ConsensusProtocol(CollaborationProtocol):
    """
    Consensus protocol for multi-agent agreement.
    Multiple agents must agree on an action or result.
    """

    def __init__(self, threshold: float = 0.67):
        """
        Initialize consensus protocol.

        Args:
            threshold: Minimum agreement threshold (0-1)
        """
        super().__init__(ProtocolType.CONSENSUS)
        self.threshold = threshold
        self.metadata["required_keys"] = ["proposal", "voters"]

    def calculate_consensus(self, votes: List[bool]) -> bool:
        """
        Calculate if consensus is reached.

        Args:
            votes: List of boolean votes

        Returns:
            True if consensus reached
        """
        if not votes:
            return False

        agreement = sum(1 for v in votes if v) / len(votes)
        return agreement >= self.threshold


class HandoffProtocol(CollaborationProtocol):
    """
    Handoff protocol for passing work between agents.
    One agent completes part of work and hands off to next.
    """

    def __init__(self):
        """Initialize handoff protocol."""
        super().__init__(ProtocolType.HANDOFF)
        self.metadata["required_keys"] = ["from_agent", "to_agent", "work_item", "state"]


class ReviewProtocol(CollaborationProtocol):
    """
    Review protocol for code review between agents.
    One agent generates code, another reviews it.
    """

    def __init__(self):
        """Initialize review protocol."""
        super().__init__(ProtocolType.REVIEW)
        self.metadata["required_keys"] = ["author_agent", "reviewer_agent", "code", "review_type"]

    def create_review_request(
        self, author: str, reviewer: str, code: str, review_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Create a review request.

        Args:
            author: Author agent ID
            reviewer: Reviewer agent ID
            code: Code to review
            review_type: Type of review

        Returns:
            Review request dictionary
        """
        return {
            "author_agent": author,
            "reviewer_agent": reviewer,
            "code": code,
            "review_type": review_type,
            "protocol": self.protocol_type.value,
        }


def create_protocol(protocol_type: ProtocolType) -> CollaborationProtocol:
    """
    Factory function to create protocol instances.

    Args:
        protocol_type: Type of protocol to create

    Returns:
        Protocol instance
    """
    protocol_map = {
        ProtocolType.REQUEST_RESPONSE: RequestResponseProtocol,
        ProtocolType.BROADCAST: BroadcastProtocol,
        ProtocolType.CONSENSUS: ConsensusProtocol,
        ProtocolType.HANDOFF: HandoffProtocol,
        ProtocolType.REVIEW: ReviewProtocol,
    }

    protocol_class = protocol_map.get(protocol_type, CollaborationProtocol)
    if protocol_class == CollaborationProtocol:
        return CollaborationProtocol(protocol_type)
    return protocol_class()
