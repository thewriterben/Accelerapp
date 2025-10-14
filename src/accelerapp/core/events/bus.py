"""
Event bus implementation for publish-subscribe messaging.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base event class."""
    
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
        }


class EventBus:
    """
    Event bus for publish-subscribe messaging.
    
    Features:
    - Topic-based routing
    - Multiple subscribers per topic
    - Async event handling
    - Dead letter queue for failed events
    - Event ordering guarantees
    """
    
    def __init__(self, max_queue_size: int = 10000):
        """
        Initialize event bus.
        
        Args:
            max_queue_size: Maximum event queue size
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._dead_letter_queue: List[Event] = []
        self._processing = False
        self._processor_task: Optional[asyncio.Task] = None
        self._event_history: List[Event] = []
        self._max_history_size = 1000
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Handler function (can be sync or async)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Event type
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.info(f"Unsubscribed handler from event type: {event_type}")
            except ValueError:
                pass
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event: Event to publish
        """
        try:
            await self._event_queue.put(event)
            logger.debug(f"Published event: {event.event_type} (ID: {event.event_id})")
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event: {event.event_type}")
            self._dead_letter_queue.append(event)
    
    async def start_processing(self) -> None:
        """Start processing events from the queue."""
        if self._processing:
            logger.warning("Event processing is already running")
            return
        
        self._processing = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("Started event processing")
    
    async def stop_processing(self) -> None:
        """Stop processing events."""
        self._processing = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped event processing")
    
    async def _process_events(self) -> None:
        """Main event processing loop."""
        while self._processing:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._dispatch_event(event)
                self._event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _dispatch_event(self, event: Event) -> None:
        """
        Dispatch event to subscribers.
        
        Args:
            event: Event to dispatch
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
        
        # Get subscribers for this event type
        handlers = self._subscribers.get(event.event_type, [])
        
        if not handlers:
            logger.debug(f"No handlers registered for event type: {event.event_type}")
            return
        
        # Execute all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                
                logger.debug(
                    f"Handler executed for event: {event.event_type} "
                    f"(ID: {event.event_id})"
                )
            except Exception as e:
                logger.error(
                    f"Handler failed for event {event.event_type} "
                    f"(ID: {event.event_id}): {e}"
                )
                self._dead_letter_queue.append(event)
    
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """
        Get subscribers for an event type.
        
        Args:
            event_type: Event type
            
        Returns:
            List of subscriber handlers
        """
        return self._subscribers.get(event_type, []).copy()
    
    def get_all_subscribers(self) -> Dict[str, int]:
        """
        Get count of subscribers for all event types.
        
        Returns:
            Dictionary mapping event types to subscriber counts
        """
        return {
            event_type: len(handlers)
            for event_type, handlers in self._subscribers.items()
        }
    
    def get_dead_letter_queue(self) -> List[Event]:
        """
        Get events in the dead letter queue.
        
        Returns:
            List of failed events
        """
        return self._dead_letter_queue.copy()
    
    def clear_dead_letter_queue(self) -> None:
        """Clear the dead letter queue."""
        self._dead_letter_queue.clear()
    
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self._event_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "queue_size": self._event_queue.qsize(),
            "max_queue_size": self._event_queue.maxsize,
            "dead_letter_count": len(self._dead_letter_queue),
            "total_subscribers": sum(len(h) for h in self._subscribers.values()),
            "event_types": len(self._subscribers),
            "processing": self._processing,
        }
