"""
Event sourcing implementation for audit and replay capabilities.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import logging

from .bus import Event

logger = logging.getLogger(__name__)


class EventStore:
    """
    Stores events for event sourcing.
    
    Features:
    - Persistent event storage
    - Event replay capabilities
    - Aggregate state reconstruction
    - Event versioning
    """
    
    def __init__(self, storage_backend: str = "memory"):
        """
        Initialize event store.
        
        Args:
            storage_backend: Storage backend type (memory, file, database)
        """
        self._storage_backend = storage_backend
        self._events: List[Event] = []
        self._snapshots: Dict[str, Any] = {}
    
    async def append(self, event: Event) -> None:
        """
        Append an event to the store.
        
        Args:
            event: Event to store
        """
        self._events.append(event)
        logger.debug(f"Event stored: {event.event_type} (ID: {event.event_id})")
    
    async def get_events(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
    ) -> List[Event]:
        """
        Retrieve events from the store.
        
        Args:
            aggregate_id: Filter by aggregate ID
            event_type: Filter by event type
            from_timestamp: Filter by start timestamp
            to_timestamp: Filter by end timestamp
            
        Returns:
            List of matching events
        """
        filtered_events = self._events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if aggregate_id:
            filtered_events = [
                e for e in filtered_events
                if e.data.get("aggregate_id") == aggregate_id
            ]
        
        if from_timestamp:
            filtered_events = [e for e in filtered_events if e.timestamp >= from_timestamp]
        
        if to_timestamp:
            filtered_events = [e for e in filtered_events if e.timestamp <= to_timestamp]
        
        return filtered_events
    
    async def replay(
        self,
        handler: callable,
        aggregate_id: Optional[str] = None,
        from_version: int = 0,
    ) -> None:
        """
        Replay events through a handler.
        
        Args:
            handler: Handler function to process events
            aggregate_id: Optional aggregate ID to replay
            from_version: Start version for replay
        """
        events = await self.get_events(aggregate_id=aggregate_id)
        
        for event in events[from_version:]:
            try:
                handler(event)
                logger.debug(f"Replayed event: {event.event_type}")
            except Exception as e:
                logger.error(f"Error replaying event {event.event_id}: {e}")
                raise
    
    async def create_snapshot(self, aggregate_id: str, state: Any) -> None:
        """
        Create a snapshot of aggregate state.
        
        Args:
            aggregate_id: Aggregate identifier
            state: Current aggregate state
        """
        self._snapshots[aggregate_id] = {
            "state": state,
            "timestamp": datetime.now(),
            "version": len([
                e for e in self._events
                if e.data.get("aggregate_id") == aggregate_id
            ])
        }
        logger.info(f"Created snapshot for aggregate: {aggregate_id}")
    
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get snapshot for an aggregate.
        
        Args:
            aggregate_id: Aggregate identifier
            
        Returns:
            Snapshot data or None
        """
        return self._snapshots.get(aggregate_id)
    
    def get_event_count(self) -> int:
        """Get total number of stored events."""
        return len(self._events)
    
    def clear(self) -> None:
        """Clear all events and snapshots."""
        self._events.clear()
        self._snapshots.clear()


class EventStream:
    """
    Represents a stream of events for an aggregate.
    """
    
    def __init__(self, aggregate_id: str, event_store: EventStore):
        """
        Initialize event stream.
        
        Args:
            aggregate_id: Aggregate identifier
            event_store: Event store instance
        """
        self.aggregate_id = aggregate_id
        self._event_store = event_store
        self._current_version = 0
    
    async def append_event(self, event: Event) -> None:
        """
        Append event to stream.
        
        Args:
            event: Event to append
        """
        # Add aggregate ID to event data
        event.data["aggregate_id"] = self.aggregate_id
        event.data["version"] = self._current_version
        
        await self._event_store.append(event)
        self._current_version += 1
    
    async def get_events(self, from_version: int = 0) -> List[Event]:
        """
        Get events for this stream.
        
        Args:
            from_version: Starting version
            
        Returns:
            List of events
        """
        all_events = await self._event_store.get_events(aggregate_id=self.aggregate_id)
        return [e for e in all_events if e.data.get("version", 0) >= from_version]
    
    async def rebuild_state(self, initial_state: Any, reducer: callable) -> Any:
        """
        Rebuild aggregate state from events.
        
        Args:
            initial_state: Initial state
            reducer: Reducer function to apply events
            
        Returns:
            Rebuilt state
        """
        events = await self.get_events()
        state = initial_state
        
        for event in events:
            state = reducer(state, event)
        
        return state
    
    @property
    def version(self) -> int:
        """Get current version."""
        return self._current_version
