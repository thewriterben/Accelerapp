"""
Digital twin lifecycle management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .twin_state import TwinState


class DigitalTwinManager:
    """
    Manages digital twins lifecycle and synchronization with physical hardware.
    """
    
    def __init__(self):
        """Initialize digital twin manager."""
        self.twins: Dict[str, TwinState] = {}
        self.physical_devices: Dict[str, Any] = {}
    
    def create_twin(self, device_id: str, device_info: Optional[Dict[str, Any]] = None) -> TwinState:
        """
        Create a new digital twin for a device.
        
        Args:
            device_id: Unique device identifier
            device_info: Optional device information
            
        Returns:
            Created TwinState instance
        """
        if device_id in self.twins:
            return self.twins[device_id]
        
        twin = TwinState(device_id)
        if device_info:
            for key, value in device_info.items():
                twin.update_metadata(key, value)
        
        self.twins[device_id] = twin
        return twin
    
    def get_twin(self, device_id: str) -> Optional[TwinState]:
        """
        Get digital twin by device ID.
        
        Args:
            device_id: Device identifier
            
        Returns:
            TwinState instance or None
        """
        return self.twins.get(device_id)
    
    def delete_twin(self, device_id: str) -> bool:
        """
        Delete a digital twin.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if deleted, False if not found
        """
        if device_id in self.twins:
            del self.twins[device_id]
            return True
        return False
    
    def list_twins(self) -> List[str]:
        """
        List all digital twin device IDs.
        
        Returns:
            List of device IDs
        """
        return list(self.twins.keys())
    
    def sync_from_hardware(self, device_id: str, hardware_state: Dict[str, Any]) -> bool:
        """
        Synchronize digital twin state from physical hardware.
        
        Args:
            device_id: Device identifier
            hardware_state: Current hardware state
            
        Returns:
            True if synchronized successfully
        """
        twin = self.get_twin(device_id)
        if not twin:
            return False
        
        # Update pin states
        if "pin_states" in hardware_state:
            for pin, value in hardware_state["pin_states"].items():
                twin.update_pin_state(int(pin), value)
        
        # Update analog values
        if "analog_values" in hardware_state:
            for pin, value in hardware_state["analog_values"].items():
                twin.update_analog_value(int(pin), value)
        
        # Update metadata
        if "metadata" in hardware_state:
            for key, value in hardware_state["metadata"].items():
                twin.update_metadata(key, value)
        
        # Update connection status
        if "connected" in hardware_state:
            twin.set_connection_status(hardware_state["connected"])
        
        return True
    
    def sync_to_hardware(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state to sync to physical hardware.
        
        Args:
            device_id: Device identifier
            
        Returns:
            State dictionary to apply to hardware, or None
        """
        twin = self.get_twin(device_id)
        if not twin:
            return None
        
        return twin.get_current_state()
    
    def register_physical_device(self, device_id: str, device_interface: Any) -> None:
        """
        Register a physical device for automatic synchronization.
        
        Args:
            device_id: Device identifier
            device_interface: Hardware interface object
        """
        self.physical_devices[device_id] = device_interface
        
        # Create twin if it doesn't exist
        if device_id not in self.twins:
            self.create_twin(device_id)
    
    def unregister_physical_device(self, device_id: str) -> bool:
        """
        Unregister a physical device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if unregistered, False if not found
        """
        if device_id in self.physical_devices:
            del self.physical_devices[device_id]
            return True
        return False
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current state of all digital twins.
        
        Returns:
            Dictionary mapping device IDs to their states
        """
        return {
            device_id: twin.get_current_state()
            for device_id, twin in self.twins.items()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the digital twin system.
        
        Returns:
            Health status dictionary
        """
        return {
            "total_twins": len(self.twins),
            "connected_twins": sum(
                1 for twin in self.twins.values()
                if twin.current_state.get("connected", False)
            ),
            "physical_devices": len(self.physical_devices),
            "timestamp": datetime.utcnow().isoformat(),
        }
