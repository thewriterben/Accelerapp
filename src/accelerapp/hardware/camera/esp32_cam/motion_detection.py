"""
Motion detection implementation for ESP32-CAM.
Provides motion detection, event triggering, and recording capabilities.
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import threading


class MotionSensitivity(Enum):
    """Motion detection sensitivity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class MotionEvent:
    """Motion detection event data."""
    event_id: str
    timestamp: str
    device_id: str
    confidence: float  # 0.0 to 1.0
    area_percentage: float  # Percentage of frame with motion
    duration_ms: int
    frame_count: int
    metadata: Dict[str, Any]


class MotionDetector:
    """
    Motion detection system for ESP32-CAM.
    Detects motion in video stream and triggers events.
    """
    
    def __init__(self, camera, sensitivity: MotionSensitivity = MotionSensitivity.MEDIUM):
        """
        Initialize motion detector.
        
        Args:
            camera: ESP32Camera instance
            sensitivity: Detection sensitivity level
        """
        self.camera = camera
        self.sensitivity = sensitivity
        self._enabled = False
        self._recording = False
        self._event_count = 0
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
        
        # Detection parameters
        self._threshold = self._get_threshold(sensitivity)
        self._min_area = 0.05  # 5% of frame
        self._cooldown_ms = 1000
    
    def _get_threshold(self, sensitivity: MotionSensitivity) -> float:
        """Get detection threshold based on sensitivity."""
        thresholds = {
            MotionSensitivity.LOW: 0.8,
            MotionSensitivity.MEDIUM: 0.6,
            MotionSensitivity.HIGH: 0.4,
            MotionSensitivity.VERY_HIGH: 0.2,
        }
        return thresholds.get(sensitivity, 0.6)
    
    def enable(self) -> bool:
        """
        Enable motion detection.
        
        Returns:
            True if enabled successfully
        """
        if not self.camera._initialized:
            if not self.camera.initialize():
                return False
        
        self._enabled = True
        return True
    
    def disable(self) -> bool:
        """
        Disable motion detection.
        
        Returns:
            True if disabled successfully
        """
        self._enabled = False
        return True
    
    def is_enabled(self) -> bool:
        """Check if motion detection is enabled."""
        return self._enabled
    
    def set_sensitivity(self, sensitivity: MotionSensitivity) -> bool:
        """
        Change detection sensitivity.
        
        Args:
            sensitivity: New sensitivity level
            
        Returns:
            True if successful
        """
        self.sensitivity = sensitivity
        self._threshold = self._get_threshold(sensitivity)
        return True
    
    def register_callback(self, callback: Callable[[MotionEvent], None]) -> None:
        """
        Register callback for motion events.
        
        Args:
            callback: Function to call on motion detection
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> bool:
        """
        Unregister motion event callback.
        
        Args:
            callback: Callback function to remove
            
        Returns:
            True if callback was removed
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
                return True
        return False
    
    def start_recording_on_motion(self) -> bool:
        """
        Enable automatic recording when motion is detected.
        
        Returns:
            True if enabled successfully
        """
        self._recording = True
        return True
    
    def stop_recording_on_motion(self) -> bool:
        """
        Disable automatic recording on motion.
        
        Returns:
            True if disabled successfully
        """
        self._recording = False
        return True
    
    def _trigger_event(self, event: MotionEvent) -> None:
        """Trigger motion event callbacks."""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(event)
                except Exception:
                    pass  # Ignore callback errors
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get motion detector status.
        
        Returns:
            Status dictionary
        """
        return {
            "enabled": self._enabled,
            "recording_on_motion": self._recording,
            "sensitivity": self.sensitivity.value,
            "threshold": self._threshold,
            "min_area": self._min_area,
            "event_count": self._event_count,
            "callbacks_registered": len(self._callbacks),
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get motion detection configuration.
        
        Returns:
            Configuration dictionary
        """
        return {
            "sensitivity": self.sensitivity.value,
            "threshold": self._threshold,
            "min_area_percentage": self._min_area * 100,
            "cooldown_ms": self._cooldown_ms,
        }
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """
        Update motion detection configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful
        """
        if "sensitivity" in config:
            try:
                sensitivity = MotionSensitivity(config["sensitivity"])
                self.set_sensitivity(sensitivity)
            except ValueError:
                return False
        
        if "min_area_percentage" in config:
            self._min_area = config["min_area_percentage"] / 100.0
        
        if "cooldown_ms" in config:
            self._cooldown_ms = config["cooldown_ms"]
        
        return True
