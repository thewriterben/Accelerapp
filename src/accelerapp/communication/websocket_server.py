"""
WebSocket-based real-time communication server for agent collaboration.
Enables real-time synchronization of code changes and agent activities.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# WebSocket support is optional (requires websockets package)
try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None

logger = logging.getLogger(__name__)


class EventType(Enum):
    """WebSocket event types."""

    AGENT_CONNECTED = "agent_connected"
    AGENT_DISCONNECTED = "agent_disconnected"
    CODE_CHANGED = "code_changed"
    AGENT_STATUS = "agent_status"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    MESSAGE = "message"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client."""

    client_id: str
    websocket: Any
    agent_id: Optional[str] = None
    role: str = "viewer"
    connected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "client_id": self.client_id,
            "agent_id": self.agent_id,
            "role": self.role,
            "connected_at": self.connected_at.isoformat(),
        }


class WebSocketCollaborationServer:
    """
    WebSocket server for real-time agent collaboration.
    Manages connections, broadcasts events, and synchronizes state.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket server.

        Args:
            host: Server host address
            port: Server port
        """
        if not WEBSOCKETS_AVAILABLE:
            raise RuntimeError(
                "websockets package not installed. Install with: pip install websockets"
            )

        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketClient] = {}
        self.event_handlers: Dict[EventType, list] = {}
        self.shared_state: Dict[str, Any] = {"code": {}, "agents": {}, "tasks": {}}
        self.server = None

    async def start(self):
        """Start the WebSocket server."""
        self.server = await websockets.serve(self._handle_client, self.host, self.port)
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")

    async def _handle_client(self, websocket, path):
        """
        Handle incoming WebSocket client connection.

        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        client_id = str(id(websocket))
        client = WebSocketClient(client_id=client_id, websocket=websocket)
        self.clients[client_id] = client

        try:
            # Send welcome message
            await self._send_to_client(
                client,
                {
                    "type": "connected",
                    "client_id": client_id,
                    "server_time": datetime.now().isoformat(),
                },
            )

            # Broadcast agent connected event
            await self._broadcast_event(
                EventType.AGENT_CONNECTED,
                {"client_id": client_id, "timestamp": datetime.now().isoformat()},
            )

            # Handle incoming messages
            async for message in websocket:
                await self._process_message(client, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        finally:
            # Clean up
            del self.clients[client_id]
            await self._broadcast_event(
                EventType.AGENT_DISCONNECTED,
                {"client_id": client_id, "timestamp": datetime.now().isoformat()},
            )

    async def _process_message(self, client: WebSocketClient, message: str):
        """
        Process incoming message from client.

        Args:
            client: Client that sent the message
            message: Message content
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "register":
                # Register agent
                client.agent_id = data.get("agent_id")
                client.role = data.get("role", "viewer")

                await self._send_to_client(
                    client, {"type": "registered", "agent_id": client.agent_id, "role": client.role}
                )

            elif msg_type == "code_update":
                # Code change from client
                file_path = data.get("file_path")
                code = data.get("code")

                self.shared_state["code"][file_path] = {
                    "content": code,
                    "updated_by": client.agent_id or client.client_id,
                    "updated_at": datetime.now().isoformat(),
                }

                # Broadcast to other clients
                await self._broadcast_event(
                    EventType.CODE_CHANGED,
                    {
                        "file_path": file_path,
                        "updated_by": client.agent_id or client.client_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    exclude_client=client.client_id,
                )

            elif msg_type == "agent_status":
                # Agent status update
                status = data.get("status")

                self.shared_state["agents"][client.agent_id or client.client_id] = {
                    "status": status,
                    "updated_at": datetime.now().isoformat(),
                }

                await self._broadcast_event(
                    EventType.AGENT_STATUS,
                    {
                        "agent_id": client.agent_id or client.client_id,
                        "status": status,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            elif msg_type == "task_start":
                # Task started
                task_id = data.get("task_id")
                task_info = data.get("task_info", {})

                self.shared_state["tasks"][task_id] = {
                    "status": "in_progress",
                    "started_by": client.agent_id or client.client_id,
                    "started_at": datetime.now().isoformat(),
                    "info": task_info,
                }

                await self._broadcast_event(
                    EventType.TASK_STARTED,
                    {
                        "task_id": task_id,
                        "started_by": client.agent_id or client.client_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            elif msg_type == "task_complete":
                # Task completed
                task_id = data.get("task_id")
                result = data.get("result")

                if task_id in self.shared_state["tasks"]:
                    self.shared_state["tasks"][task_id].update(
                        {
                            "status": "completed",
                            "completed_at": datetime.now().isoformat(),
                            "result": result,
                        }
                    )

                await self._broadcast_event(
                    EventType.TASK_COMPLETED,
                    {"task_id": task_id, "timestamp": datetime.now().isoformat()},
                )

            elif msg_type == "sync_request":
                # Client requests current state
                await self._send_to_client(
                    client,
                    {
                        "type": "sync_response",
                        "state": self.shared_state,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            elif msg_type == "message":
                # Generic message to broadcast
                await self._broadcast_event(
                    EventType.MESSAGE,
                    {
                        "from": client.agent_id or client.client_id,
                        "content": data.get("content"),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client.client_id}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _send_to_client(self, client: WebSocketClient, data: Dict[str, Any]):
        """
        Send data to specific client.

        Args:
            client: Target client
            data: Data to send
        """
        try:
            await client.websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending to client {client.client_id}: {e}")

    async def _broadcast_event(
        self, event_type: EventType, data: Dict[str, Any], exclude_client: Optional[str] = None
    ):
        """
        Broadcast event to all connected clients.

        Args:
            event_type: Type of event
            data: Event data
            exclude_client: Optional client ID to exclude from broadcast
        """
        message = {"type": "event", "event_type": event_type.value, "data": data}

        # Send to all clients except excluded one
        for client_id, client in self.clients.items():
            if client_id != exclude_client:
                await self._send_to_client(client, message)

        # Call registered event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

    def on_event(self, event_type: EventType, handler: Callable):
        """
        Register event handler.

        Args:
            event_type: Type of event to listen for
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def get_connected_clients(self) -> list:
        """Get list of connected clients."""
        return [client.to_dict() for client in self.clients.values()]

    def get_state(self) -> Dict[str, Any]:
        """Get current shared state."""
        return self.shared_state.copy()

    async def broadcast_code_change(self, file_path: str, code: str, author: str):
        """
        Broadcast code change to all clients.

        Args:
            file_path: Path to changed file
            code: New code content
            author: Who made the change
        """
        self.shared_state["code"][file_path] = {
            "content": code,
            "updated_by": author,
            "updated_at": datetime.now().isoformat(),
        }

        await self._broadcast_event(
            EventType.CODE_CHANGED,
            {"file_path": file_path, "updated_by": author, "timestamp": datetime.now().isoformat()},
        )


class WebSocketClient:
    """
    WebSocket client for connecting to collaboration server.
    """

    def __init__(self, server_url: str, agent_id: str, role: str = "developer"):
        """
        Initialize WebSocket client.

        Args:
            server_url: Server URL (e.g., ws://localhost:8765)
            agent_id: Unique agent identifier
            role: Client role
        """
        if not WEBSOCKETS_AVAILABLE:
            raise RuntimeError("websockets package not installed")

        self.server_url = server_url
        self.agent_id = agent_id
        self.role = role
        self.websocket = None
        self.event_handlers: Dict[str, list] = {}

    async def connect(self):
        """Connect to WebSocket server."""
        self.websocket = await websockets.connect(self.server_url)

        # Register with server
        await self.send({"type": "register", "agent_id": self.agent_id, "role": self.role})

        # Start listening for messages
        asyncio.create_task(self._listen())

    async def disconnect(self):
        """Disconnect from server."""
        if self.websocket:
            await self.websocket.close()

    async def send(self, data: Dict[str, Any]):
        """
        Send data to server.

        Args:
            data: Data to send
        """
        if self.websocket:
            await self.websocket.send(json.dumps(data))

    async def send_code_update(self, file_path: str, code: str):
        """
        Send code update to server.

        Args:
            file_path: Path to updated file
            code: New code content
        """
        await self.send({"type": "code_update", "file_path": file_path, "code": code})

    async def send_status_update(self, status: str):
        """
        Send status update to server.

        Args:
            status: Current status
        """
        await self.send({"type": "agent_status", "status": status})

    async def request_sync(self):
        """Request current state from server."""
        await self.send({"type": "sync_request"})

    async def _listen(self):
        """Listen for incoming messages."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get("type")

                # Call registered handlers
                if msg_type in self.event_handlers:
                    for handler in self.event_handlers[msg_type]:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as e:
                            logger.error(f"Error in event handler: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Disconnected from server")

    def on(self, event_type: str, handler: Callable):
        """
        Register event handler.

        Args:
            event_type: Type of event to listen for
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
