"""
Digital twin visualization and monitoring.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class TwinVisualizer:
    """
    Provides visualization and monitoring capabilities for digital twins.
    """
    
    def __init__(self, twin_manager):
        """
        Initialize visualizer.
        
        Args:
            twin_manager: DigitalTwinManager instance
        """
        self.twin_manager = twin_manager
    
    def get_device_dashboard(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate dashboard data for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Dashboard data dictionary or None
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return None
        
        state = twin.get_current_state()
        
        return {
            "device_id": device_id,
            "connection_status": state.get("connected", False),
            "pin_states": state.get("pin_states", {}),
            "analog_values": state.get("analog_values", {}),
            "metadata": state.get("metadata", {}),
            "last_update": datetime.utcnow().isoformat(),
        }
    
    def get_overview_dashboard(self) -> Dict[str, Any]:
        """
        Generate overview dashboard for all devices.
        
        Returns:
            Overview dashboard data
        """
        all_states = self.twin_manager.get_all_states()
        
        return {
            "total_devices": len(all_states),
            "connected_devices": sum(
                1 for state in all_states.values()
                if state.get("connected", False)
            ),
            "devices": [
                {
                    "device_id": device_id,
                    "connected": state.get("connected", False),
                    "pin_count": len(state.get("pin_states", {})),
                    "analog_count": len(state.get("analog_values", {})),
                }
                for device_id, state in all_states.items()
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_state_timeline(self, device_id: str, duration_minutes: int = 60) -> Optional[Dict[str, Any]]:
        """
        Get state timeline for a device.
        
        Args:
            device_id: Device identifier
            duration_minutes: Duration to retrieve in minutes
            
        Returns:
            Timeline data or None
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return None
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        history = twin.get_history()
        
        # Filter history by time
        filtered_history = [
            snapshot for snapshot in history
            if snapshot.timestamp >= cutoff_time
        ]
        
        return {
            "device_id": device_id,
            "duration_minutes": duration_minutes,
            "snapshots": [snapshot.to_dict() for snapshot in filtered_history],
            "total_snapshots": len(filtered_history),
        }
    
    def get_pin_activity(self, device_id: str, pin: int) -> Optional[Dict[str, Any]]:
        """
        Get activity data for a specific pin.
        
        Args:
            device_id: Device identifier
            pin: Pin number
            
        Returns:
            Pin activity data or None
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return None
        
        history = twin.get_history()
        
        # Extract pin activity
        activity = []
        for snapshot in history:
            if pin in snapshot.pin_states:
                activity.append({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "value": snapshot.pin_states[pin],
                })
            elif pin in snapshot.analog_values:
                activity.append({
                    "timestamp": snapshot.timestamp.isoformat(),
                    "value": snapshot.analog_values[pin],
                })
        
        return {
            "device_id": device_id,
            "pin": pin,
            "activity": activity,
            "total_events": len(activity),
        }
    
    def generate_status_report(self, device_id: str) -> Optional[str]:
        """
        Generate a text status report for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Text report or None
        """
        twin = self.twin_manager.get_twin(device_id)
        if not twin:
            return None
        
        state = twin.get_current_state()
        
        lines = [
            f"Digital Twin Status Report",
            f"=" * 50,
            f"Device ID: {device_id}",
            f"Connected: {state.get('connected', False)}",
            f"",
            f"Digital Pin States:",
        ]
        
        pin_states = state.get("pin_states", {})
        if pin_states:
            for pin, value in sorted(pin_states.items()):
                lines.append(f"  Pin {pin}: {'HIGH' if value else 'LOW'}")
        else:
            lines.append("  No digital pins configured")
        
        lines.append("")
        lines.append("Analog Values:")
        
        analog_values = state.get("analog_values", {})
        if analog_values:
            for pin, value in sorted(analog_values.items()):
                lines.append(f"  Pin {pin}: {value}")
        else:
            lines.append("  No analog pins configured")
        
        lines.append("")
        lines.append("Metadata:")
        
        metadata = state.get("metadata", {})
        if metadata:
            for key, value in sorted(metadata.items()):
                lines.append(f"  {key}: {value}")
        else:
            lines.append("  No metadata")
        
        lines.append("")
        lines.append(f"Report generated: {datetime.utcnow().isoformat()}")
        
        return "\n".join(lines)
    
    def get_realtime_feed(self, device_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get real-time feed of device states.
        
        Args:
            device_ids: Optional list of device IDs to filter
            
        Returns:
            List of device state snapshots
        """
        if device_ids:
            twins = {
                device_id: self.twin_manager.get_twin(device_id)
                for device_id in device_ids
                if self.twin_manager.get_twin(device_id)
            }
        else:
            twins = self.twin_manager.twins
        
        feed = []
        for device_id, twin in twins.items():
            snapshot = twin.get_snapshot()
            feed.append({
                "device_id": device_id,
                "timestamp": snapshot.timestamp.isoformat(),
                "state": snapshot.to_dict(),
            })
        
        return feed
