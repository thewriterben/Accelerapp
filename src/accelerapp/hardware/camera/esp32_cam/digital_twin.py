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
            twin_id: Optional twin identifier (defaults to twin_id from config)
        """
        self.camera = camera
        self.twin_id = twin_id or getattr(camera.config, "twin_id", None) or "default"
        self._state_history: list = []
        self._max_history = 1000
        self._error_count = 0
        self._stream_count = 0
        self._start_time = datetime.utcnow()

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
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "initialized": status.get("initialized", False),
                "streaming": False,  # Default since not always available
                "captures": status.get("frame_count", 0),
                "streams": self._stream_count,
                "errors": self._error_count,
                "uptime": uptime,
            },
            "health": self._calculate_health(),
        }

    def _calculate_health(self) -> str:
        """Calculate camera health status."""
        status = self.camera.get_status()

        if not status.get("initialized", False):
            return "offline"

        captures = status.get("frame_count", 1)
        error_rate = self._error_count / max(captures, 1)
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
        captures = status.get("frame_count", 0)

        # Simple predictive logic
        total_operations = captures + self._stream_count
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
        config = self.camera.get_config()
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        return {
            "twin_id": self.twin_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "performance": {
                "total_captures": status.get("frame_count", 0),
                "total_streams": self._stream_count,
                "error_count": self._error_count,
                "uptime_seconds": uptime,
            },
            "configuration": {
                "resolution": status.get("frame_size", "VGA"),
                "format": config.get("pixel_format", "JPEG"),
                "board_type": status.get("variant", "ai_thinker"),
                "camera_model": status.get("sensor", "OV2640"),
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
