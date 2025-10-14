"""
Digital twin state management and synchronization.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class StateSnapshot:
    """Represents a snapshot of hardware state at a point in time."""
    
    timestamp: datetime
    device_id: str
    pin_states: Dict[int, bool] = field(default_factory=dict)
    analog_values: Dict[int, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "device_id": self.device_id,
            "pin_states": self.pin_states,
            "analog_values": self.analog_values,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """Create snapshot from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            device_id=data["device_id"],
            pin_states=data.get("pin_states", {}),
            analog_values=data.get("analog_values", {}),
            metadata=data.get("metadata", {}),
        )


class TwinState:
    """
    Manages real-time state synchronization for digital twins.
    Tracks hardware state and provides live updates.
    """
    
    def __init__(self, device_id: str):
        """
        Initialize twin state.
        
        Args:
            device_id: Unique identifier for the device
        """
        self.device_id = device_id
        self.current_state: Dict[str, Any] = {
            "connected": False,
            "pin_states": {},
            "analog_values": {},
            "metadata": {},
        }
        self.state_history: List[StateSnapshot] = []
        self.max_history = 1000
        self.subscribers: List[Any] = []
    
    def update_pin_state(self, pin: int, value: bool) -> None:
        """
        Update digital pin state.
        
        Args:
            pin: Pin number
            value: Digital value
        """
        self.current_state["pin_states"][pin] = value
        self._notify_subscribers("pin_update", {"pin": pin, "value": value})
        self._save_snapshot()
    
    def update_analog_value(self, pin: int, value: int) -> None:
        """
        Update analog pin value.
        
        Args:
            pin: Pin number
            value: Analog value
        """
        self.current_state["analog_values"][pin] = value
        self._notify_subscribers("analog_update", {"pin": pin, "value": value})
        self._save_snapshot()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update device metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.current_state["metadata"][key] = value
        self._notify_subscribers("metadata_update", {"key": key, "value": value})
    
    def set_connection_status(self, connected: bool) -> None:
        """
        Set device connection status.
        
        Args:
            connected: Connection status
        """
        self.current_state["connected"] = connected
        self._notify_subscribers("connection_status", {"connected": connected})
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current device state.
        
        Returns:
            Current state dictionary
        """
        return self.current_state.copy()
    
    def get_snapshot(self) -> StateSnapshot:
        """
        Get current state as snapshot.
        
        Returns:
            StateSnapshot object
        """
        return StateSnapshot(
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            pin_states=self.current_state["pin_states"].copy(),
            analog_values=self.current_state["analog_values"].copy(),
            metadata=self.current_state["metadata"].copy(),
        )
    
    def get_history(self, limit: Optional[int] = None) -> List[StateSnapshot]:
        """
        Get state history.
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            List of state snapshots
        """
        if limit:
            return self.state_history[-limit:]
        return self.state_history.copy()
    
    def subscribe(self, callback: Any) -> None:
        """
        Subscribe to state updates.
        
        Args:
            callback: Callback function for updates
        """
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Any) -> None:
        """
        Unsubscribe from state updates.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _notify_subscribers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all subscribers of state change."""
        for callback in self.subscribers:
            try:
                callback(event_type, data)
            except Exception:
                pass  # Continue notifying other subscribers
    
    def _save_snapshot(self) -> None:
        """Save current state as snapshot in history."""
        snapshot = self.get_snapshot()
        self.state_history.append(snapshot)
        
        # Limit history size
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]
    
    def export_state(self) -> str:
        """
        Export current state as JSON.
        
        Returns:
            JSON string of current state
        """
        return json.dumps(self.current_state, indent=2)
    
    def import_state(self, state_json: str) -> None:
        """
        Import state from JSON.
        
        Args:
            state_json: JSON string of state
        """
        imported_state = json.loads(state_json)
        
        # Update pin states with integer keys
        if "pin_states" in imported_state:
            self.current_state["pin_states"] = {
                int(k): v for k, v in imported_state["pin_states"].items()
            }
        
        # Update analog values with integer keys
        if "analog_values" in imported_state:
            self.current_state["analog_values"] = {
                int(k): v for k, v in imported_state["analog_values"].items()
            }
        
        # Update other fields
        for key in ["connected", "metadata"]:
            if key in imported_state:
                self.current_state[key] = imported_state[key]
        
        self._save_snapshot()
