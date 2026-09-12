"""
Agent-to-agent communication module for collaborative code generation.
Provides messaging, coordination, and shared context management.
"""

from .agent_coordinator import AgentCoordinator, CoordinationStrategy
from .collaboration_protocols import CollaborationProtocol, ProtocolType
from .message_bus import Message, MessageBus, MessagePriority
from .shared_context import ContextScope, SharedContext

# WebSocket support is optional
try:
    from .websocket_server import EventType as WebSocketEventType
    from .websocket_server import WebSocketCollaborationServer

    __all__ = [
        "MessageBus",
        "Message",
        "MessagePriority",
        "AgentCoordinator",
        "CoordinationStrategy",
        "SharedContext",
        "ContextScope",
        "CollaborationProtocol",
        "ProtocolType",
        "WebSocketCollaborationServer",
        "WebSocketEventType",
    ]
except ImportError:
    __all__ = [
        "MessageBus",
        "Message",
        "MessagePriority",
        "AgentCoordinator",
        "CoordinationStrategy",
        "SharedContext",
        "ContextScope",
        "CollaborationProtocol",
        "ProtocolType",
    ]
