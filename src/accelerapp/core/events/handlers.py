"""
Event handlers for processing events.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

from .bus import Event

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    def handle(self, event: Event) -> None:
        """
        Handle an event.
        
        Args:
            event: Event to handle
        """
        pass
    
    def can_handle(self, event: Event) -> bool:
        """
        Check if this handler can handle the event.
        
        Args:
            event: Event to check
            
        Returns:
            True if handler can process this event
        """
        return True


class AsyncEventHandler(ABC):
    """Base class for async event handlers."""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """
        Handle an event asynchronously.
        
        Args:
            event: Event to handle
        """
        pass
    
    def can_handle(self, event: Event) -> bool:
        """
        Check if this handler can handle the event.
        
        Args:
            event: Event to check
            
        Returns:
            True if handler can process this event
        """
        return True


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def handle(self, event: Event) -> None:
        """Log the event."""
        logger.info(
            f"Event received: {event.event_type} "
            f"(ID: {event.event_id}, Source: {event.source})"
        )


class MetricsEventHandler(EventHandler):
    """Event handler that tracks event metrics."""
    
    def __init__(self):
        """Initialize metrics handler."""
        self._event_counts: Dict[str, int] = {}
    
    def handle(self, event: Event) -> None:
        """Track event metrics."""
        event_type = event.event_type
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1
    
    def get_metrics(self) -> Dict[str, int]:
        """Get event metrics."""
        return self._event_counts.copy()
    
    def reset_metrics(self) -> None:
        """Reset metrics."""
        self._event_counts.clear()
