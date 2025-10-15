"""
Digital twin integration for ESP32-CAM.
Provides real-time state synchronization and telemetry reporting.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class CameraDigitalTwin:
    """
    Digital twin interface for ESP32-CAM devices.
    Integrates with the existing digital twin platform.
    """
    
    def __init__(self, camera, twin_id: Optional[str] = None):
        """
        Initialize camera digital twin.
        
        Args:
            camera: ESP32Camera instance
            twin_id: Optional twin identifier (defaults to device_id)
        """
        self.camera = camera
        self.twin_id = twin_id or camera.config.device_id
        self._state_history: list = []
        self._max_history = 1000
    
    def sync_state(self) -> Dict[str, Any]:
        """
        Synchronize camera state to digital twin.
        
        Returns:
            Current state dictionary
        """
        state = {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "camera_status": self.camera.get_status(),
            "camera_config": self.camera.get_config(),
        }
        
        # Store in history
        self._state_history.append(state)
        if len(self._state_history) > self._max_history:
            self._state_history.pop(0)
        
        return state
    
    def get_telemetry(self) -> Dict[str, Any]:
        """
        Get real-time telemetry data.
        
        Returns:
            Telemetry dictionary
        """
        status = self.camera.get_status()
        
        return {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "initialized": status["initialized"],
                "streaming": status["streaming"],
                "captures": status["stats"]["captures"],
                "streams": status["stats"]["streams"],
                "errors": status["stats"]["errors"],
                "uptime": status["stats"]["uptime"],
            },
            "health": self._calculate_health(),
        }
    
    def _calculate_health(self) -> str:
        """Calculate camera health status."""
        status = self.camera.get_status()
        
        if not status["initialized"]:
            return "offline"
        
        error_rate = status["stats"]["errors"] / max(status["stats"]["captures"], 1)
        if error_rate > 0.1:
            return "degraded"
        
        return "healthy"
    
    def get_state_history(self, limit: int = 100) -> list:
        """
        Get historical state snapshots.
        
        Args:
            limit: Maximum number of snapshots to return
            
        Returns:
            List of historical states
        """
        return self._state_history[-limit:]
    
    def predict_maintenance(self) -> Dict[str, Any]:
        """
        Predict maintenance needs based on usage patterns.
        
        Returns:
            Maintenance prediction dictionary
        """
        status = self.camera.get_status()
        stats = status["stats"]
        
        # Simple predictive logic
        total_operations = stats["captures"] + stats["streams"]
        maintenance_threshold = 10000
        
        usage_percentage = (total_operations / maintenance_threshold) * 100
        
        return {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "usage_percentage": min(usage_percentage, 100),
            "estimated_operations_remaining": max(0, maintenance_threshold - total_operations),
            "maintenance_recommended": usage_percentage >= 80,
            "health_status": self._calculate_health(),
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """
        Get performance analytics.
        
        Returns:
            Analytics dictionary
        """
        status = self.camera.get_status()
        
        return {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "performance": {
                "total_captures": status["stats"]["captures"],
                "total_streams": status["stats"]["streams"],
                "error_count": status["stats"]["errors"],
                "uptime_seconds": status["stats"]["uptime"],
            },
            "configuration": {
                "resolution": status["resolution"],
                "format": status["format"],
                "board_type": status["board_type"],
                "camera_model": status["camera_model"],
            },
        }
    
    def export_twin_data(self) -> Dict[str, Any]:
        """
        Export complete twin data for backup or migration.
        
        Returns:
            Complete twin data dictionary
        """
        return {
            "twin_id": self.twin_id,
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "current_state": self.sync_state(),
            "telemetry": self.get_telemetry(),
            "analytics": self.get_analytics(),
            "maintenance": self.predict_maintenance(),
            "history_count": len(self._state_history),
        }
