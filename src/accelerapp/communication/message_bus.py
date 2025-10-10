"""
Internal message bus for agent-to-agent communication.
Provides pub/sub messaging system for collaborative code generation.
"""

from typing import Dict, Any, List, Callable, Optional
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from datetime import datetime
from queue import PriorityQueue, Queue, Empty
import threading
import uuid


class MessagePriority(IntEnum):
    """Message priority levels."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass
class Message:
    """
    Message object for agent communication.
    """
    sender: str
    topic: str
    content: Any
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: 'Message') -> bool:
        """Compare messages by priority for queue ordering."""
        return self.priority < other.priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'topic': self.topic,
            'content': self.content,
            'priority': self.priority.name,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class MessageBus:
    """
    Internal message bus for agent communication.
    Supports pub/sub pattern with priority queuing.
    """
    
    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize message bus.
        
        Args:
            max_queue_size: Maximum number of messages in queue
        """
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        self.message_history: List[Message] = []
        self.max_history_size: int = 1000
        self._running: bool = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
    
    def subscribe(
        self, 
        topic: str, 
        handler: Callable[[Message], None]
    ) -> None:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Callback function to handle messages
        """
        with self._lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(handler)
    
    def unsubscribe(
        self, 
        topic: str, 
        handler: Callable[[Message], None]
    ) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            handler: Handler to remove
            
        Returns:
            True if unsubscribed, False if not found
        """
        with self._lock:
            if topic in self.subscribers:
                try:
                    self.subscribers[topic].remove(handler)
                    if not self.subscribers[topic]:
                        del self.subscribers[topic]
                    return True
                except ValueError:
                    pass
            return False
    
    def publish(
        self,
        sender: str,
        topic: str,
        content: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a message to a topic.
        
        Args:
            sender: Agent identifier sending the message
            topic: Topic to publish to
            content: Message content
            priority: Message priority
            metadata: Optional metadata
            
        Returns:
            Message ID
        """
        message = Message(
            sender=sender,
            topic=topic,
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        
        try:
            self.message_queue.put_nowait(message)
            self._add_to_history(message)
            return message.message_id
        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {str(e)}")
    
    def start(self) -> None:
        """Start message bus worker thread."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_messages, daemon=True)
        self._worker_thread.start()
    
    def stop(self) -> None:
        """Stop message bus worker thread."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def _process_messages(self) -> None:
        """Worker thread to process messages from queue."""
        while self._running:
            try:
                message = self.message_queue.get(timeout=0.1)
                self._deliver_message(message)
                self.message_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def _deliver_message(self, message: Message) -> None:
        """
        Deliver message to subscribers.
        
        Args:
            message: Message to deliver
        """
        with self._lock:
            handlers = self.subscribers.get(message.topic, [])
            
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                print(f"Error in message handler: {e}")
    
    def _add_to_history(self, message: Message) -> None:
        """
        Add message to history.
        
        Args:
            message: Message to add
        """
        self.message_history.append(message)
        
        # Trim history if needed
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
    
    def get_history(
        self,
        topic: Optional[str] = None,
        sender: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Get message history.
        
        Args:
            topic: Optional filter by topic
            sender: Optional filter by sender
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        messages = self.message_history[-limit:]
        
        if topic:
            messages = [m for m in messages if m.topic == topic]
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        
        return messages
    
    def clear_history(self) -> None:
        """Clear message history."""
        self.message_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get message bus statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            return {
                'running': self._running,
                'queue_size': self.message_queue.qsize(),
                'subscribers_count': len(self.subscribers),
                'topics': list(self.subscribers.keys()),
                'history_size': len(self.message_history),
                'total_handlers': sum(len(h) for h in self.subscribers.values())
            }
