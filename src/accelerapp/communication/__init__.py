"""
Agent-to-agent communication module for collaborative code generation.
Provides messaging, coordination, and shared context management.
"""

from .agent_coordinator import AgentCoordinator, CoordinationStrategy
from .collaboration_protocols import CollaborationProtocol, ProtocolType
from .message_bus import Message, MessageBus, MessagePriority
from .shared_context import ContextScope, SharedContext

# WebSocket support is optional
# Optional dependencies: these names are imported for re-export and are listed
# in __all__ below. That __all__ is assigned (or extended) inside the same
# try/except ImportError guard, and pyflakes only honours a plain top-level
# __all__ -- so it reports these as unused. They are not; hence the markers.
try:
    from .websocket_server import EventType as WebSocketEventType  # noqa: F401
    from .websocket_server import WebSocketCollaborationServer  # noqa: F401

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
