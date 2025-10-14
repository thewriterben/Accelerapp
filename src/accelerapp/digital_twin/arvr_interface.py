"""
AR/VR interface integration for immersive hardware control.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ARVRInterface:
    """
    Provides AR/VR interface support for immersive hardware visualization and control.
    """
    
    def __init__(self, twin_manager, visualizer):
        """
        Initialize AR/VR interface.
        
        Args:
            twin_manager: DigitalTwinManager instance
            visualizer: TwinVisualizer instance
        """
        self.twin_manager = twin_manager
        self.visualizer = visualizer
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, device_id: str, interface_type: str = "vr") -> Dict[str, Any]:
        """
        Create an AR/VR session for a device.
        
        Args:
            session_id: Unique session identifier
            device_id: Device to visualize
            interface_type: Type of interface (ar/vr)
            
        Returns:
            Session information
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return {"error": "Twin not found"}
        
        session = {
            "session_id": session_id,
            "device_id": device_id,
            "interface_type": interface_type,
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
        }
        
        self.active_sessions[session_id] = session
        return session
    
    def get_3d_model(self, device_id: str) -> Dict[str, Any]:
        """
        Get 3D model representation of device for AR/VR.
        
        Args:
            device_id: Device identifier
            
        Returns:
            3D model data
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return {"error": "Twin not found"}
        
        state = twin.get_current_state()
        
        # Generate simplified 3D model data structure
        # In production, this would interface with actual 3D modeling libraries
        model = {
            "device_id": device_id,
            "model_type": "hardware_board",
            "components": [],
            "connections": [],
        }
        
        # Add pin components
        for pin, value in state.get("pin_states", {}).items():
            model["components"].append({
                "type": "digital_pin",
                "id": f"pin_{pin}",
                "position": {"x": pin * 10, "y": 0, "z": 0},
                "state": "high" if value else "low",
                "color": "#00FF00" if value else "#FF0000",
            })
        
        # Add analog components
        for pin, value in state.get("analog_values", {}).items():
            model["components"].append({
                "type": "analog_pin",
                "id": f"analog_{pin}",
                "position": {"x": pin * 10, "y": 20, "z": 0},
                "value": value,
                "color": f"#{int(value/1024*255):02x}00FF",
            })
        
        return model
    
    def get_realtime_stream(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time state stream for AR/VR session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Real-time state data or None
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        device_id = session["device_id"]
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return None
        
        return {
            "session_id": session_id,
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "state": twin.get_current_state(),
            "model_updates": self.get_3d_model(device_id),
        }
    
    def send_control_command(self, session_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send control command from AR/VR interface to device.
        
        Args:
            session_id: Session identifier
            command: Control command
            
        Returns:
            Command result
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "success": False}
        
        device_id = session["device_id"]
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return {"error": "Twin not found", "success": False}
        
        # Process command
        command_type = command.get("type")
        
        if command_type == "digital_write":
            pin = command.get("pin")
            value = command.get("value")
            if pin is not None and value is not None:
                twin.update_pin_state(pin, value)
                return {"success": True, "command": "digital_write", "pin": pin, "value": value}
        
        elif command_type == "analog_write":
            pin = command.get("pin")
            value = command.get("value")
            if pin is not None and value is not None:
                twin.update_analog_value(pin, value)
                return {"success": True, "command": "analog_write", "pin": pin, "value": value}
        
        return {"error": "Invalid command", "success": False}
    
    def get_haptic_feedback(self, device_id: str) -> Dict[str, Any]:
        """
        Generate haptic feedback data for AR/VR controllers.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Haptic feedback configuration
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return {"error": "Twin not found"}
        
        state = twin.get_current_state()
        
        # Generate haptic patterns based on device state
        # Higher activity = stronger feedback
        pin_count = len(state.get("pin_states", {}))
        analog_count = len(state.get("analog_values", {}))
        
        intensity = min(1.0, (pin_count + analog_count) / 20.0)
        
        return {
            "device_id": device_id,
            "haptic_enabled": True,
            "intensity": intensity,
            "pattern": "pulse" if state.get("connected") else "none",
            "frequency": 50,  # Hz
        }
    
    def get_spatial_audio(self, device_id: str) -> Dict[str, Any]:
        """
        Generate spatial audio configuration for AR/VR.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Spatial audio configuration
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return {"error": "Twin not found"}
        
        state = twin.get_current_state()
        
        return {
            "device_id": device_id,
            "audio_enabled": True,
            "connected_sound": "beep" if state.get("connected") else "none",
            "pin_change_sound": "click",
            "volume": 0.5,
            "spatial_position": {"x": 0, "y": 0, "z": -1},
        }
    
    def close_session(self, session_id: str) -> bool:
        """
        Close an AR/VR session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if closed successfully
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["active"] = False
            return True
        return False
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active AR/VR sessions.
        
        Returns:
            List of active sessions
        """
        return [
            session for session in self.active_sessions.values()
            if session.get("active", False)
        ]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get AR/VR session statistics.
        
        Returns:
            Session statistics
        """
        active_count = sum(1 for s in self.active_sessions.values() if s.get("active", False))
        
        interface_types = {}
        for session in self.active_sessions.values():
            if session.get("active", False):
                itype = session.get("interface_type", "unknown")
                interface_types[itype] = interface_types.get(itype, 0) + 1
        
        return {
            "total_sessions": len(self.active_sessions),
            "active_sessions": active_count,
            "interface_types": interface_types,
            "timestamp": datetime.utcnow().isoformat(),
        }
