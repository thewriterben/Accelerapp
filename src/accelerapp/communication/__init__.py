"""
Agent-to-agent communication module for collaborative code generation.
Provides messaging, coordination, and shared context management.
"""

from .message_bus import MessageBus, Message, MessagePriority
from .agent_coordinator import AgentCoordinator, CoordinationStrategy
from .shared_context import SharedContext, ContextScope
from .collaboration_protocols import CollaborationProtocol, ProtocolType

__all__ = [
    "MessageBus",
    "Message",
    "MessagePriority",
    "AgentCoordinator",
    "CoordinationStrategy",
    "SharedContext",
    "ContextScope",
    "CollaborationProtocol",
    "ProtocolType"
]
