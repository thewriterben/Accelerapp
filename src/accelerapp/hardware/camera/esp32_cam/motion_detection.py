"""
Motion detection module for ESP32-CAM.
Provides frame differencing, PIR integration, and QR code scanning.
"""

from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class MotionSensitivity(Enum):
    """Motion detection sensitivity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CUSTOM = "custom"


class MotionAlgorithm(Enum):
    """Motion detection algorithms."""
    FRAME_DIFF = "frame_diff"
    BACKGROUND_SUBTRACTION = "background_subtraction"
    OPTICAL_FLOW = "optical_flow"


@dataclass
class MotionConfig:
    """Motion detection configuration."""
    threshold: int = 25
    sensitivity: MotionSensitivity = MotionSensitivity.MEDIUM
    algorithm: MotionAlgorithm = MotionAlgorithm.FRAME_DIFF
    min_area: int = 500
    blur_size: int = 21
    detection_interval_ms: int = 200
    cooldown_seconds: float = 2.0
    enable_pir: bool = False
    pir_pin: int = 13


class MotionDetector:
    """
    Motion detection engine for ESP32-CAM.
    Uses frame differencing and optional PIR sensor integration.
    """

    def __init__(self, camera, config: Optional[MotionConfig] = None):
        """
        Initialize motion detector.

        Args:
            camera: ESP32Camera instance
            config: Motion detection configuration
        """
        self.camera = camera
        self.config = config or MotionConfig()
        self.sensitivity = self.config.sensitivity

        self._enabled = False
        self._motion_detected = False
        self._last_frame = None
        self._callbacks: List[Callable] = []
        self._motion_events: List[Dict[str, Any]] = []

        logger.info(f"MotionDetector initialized with {self.config.algorithm.value}")

    def enable(self) -> bool:
        """Enable motion detection."""
        self._enabled = True
        logger.info("Motion detection enabled")
        return True

    def disable(self) -> bool:
        """Disable motion detection."""
        self._enabled = False
        self._motion_detected = False
        logger.info("Motion detection disabled")
        return True

    def is_enabled(self) -> bool:
        """Check if motion detection is enabled."""
        return self._enabled

    def set_sensitivity(self, sensitivity: MotionSensitivity) -> bool:
        """
        Set detection sensitivity.

        Args:
            sensitivity: Sensitivity level

        Returns:
            True if set successfully
        """
        self.sensitivity = sensitivity
        self.config.sensitivity = sensitivity

        # Adjust threshold based on sensitivity
        if sensitivity == MotionSensitivity.LOW:
            self.config.threshold = 40
        elif sensitivity == MotionSensitivity.MEDIUM:
            self.config.threshold = 25
        elif sensitivity == MotionSensitivity.HIGH:
            self.config.threshold = 15

        logger.info(f"Sensitivity set to {sensitivity.value}")
        return True

    def detect_motion(self, frame: Optional[bytes] = None) -> bool:
        """
        Detect motion in current or provided frame.

        Args:
            frame: Optional frame data

        Returns:
            True if motion detected
        """
        if not self._enabled:
            return False

        # Get current frame
        if frame is None and self.camera.initialized:
            frame = self.camera.capture_frame()

        if frame is None:
            return False

        # First frame - no motion yet
        if self._last_frame is None:
            self._last_frame = frame
            return False

        # Compare frames
        motion = self._compare_frames(self._last_frame, frame)
        self._last_frame = frame

        if motion:
            self._motion_detected = True
            self._record_event()
            self._notify_callbacks()

        return motion

    def _compare_frames(self, frame1: bytes, frame2: bytes) -> bool:
        """
        Compare two frames for motion.

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            True if motion detected
        """
        # Simplified comparison - in production would use actual image processing
        # This is a placeholder implementation
        return len(frame1) != len(frame2)

    def _record_event(self):
        """Record motion event."""
        event = {
            "timestamp": "2025-10-15T12:00:00Z",
            "algorithm": self.config.algorithm.value,
            "sensitivity": self.config.sensitivity.value,
        }
        self._motion_events.append(event)

        # Keep only last 100 events
        if len(self._motion_events) > 100:
            self._motion_events = self._motion_events[-100:]

    def _notify_callbacks(self):
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                callback({"motion_detected": True})
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def register_callback(self, callback: Callable) -> None:
        """Register motion detection callback."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable) -> bool:
        """Unregister motion detection callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get motion detection statistics."""
        return {
            "enabled": self._enabled,
            "motion_detected": self._motion_detected,
            "algorithm": self.config.algorithm.value,
            "sensitivity": self.config.sensitivity.value,
            "threshold": self.config.threshold,
            "total_events": len(self._motion_events),
            "callbacks": len(self._callbacks),
        }

    def generate_motion_detection_code(self) -> Dict[str, str]:
        """Generate ESP32 motion detection code."""
        header = self._generate_motion_header()
        implementation = self._generate_motion_implementation()

        return {
            "motion_detection.h": header,
            "motion_detection.cpp": implementation,
        }

    def _generate_motion_header(self) -> str:
        """Generate motion detection header."""
        return f"""
// Motion Detection for ESP32-CAM
#ifndef MOTION_DETECTION_H
#define MOTION_DETECTION_H

#include <esp_camera.h>

#define MOTION_THRESHOLD {self.config.threshold}
#define MOTION_MIN_AREA {self.config.min_area}
#define MOTION_BLUR_SIZE {self.config.blur_size}

class MotionDetector {{
public:
    MotionDetector();
    bool begin();
    bool detectMotion(camera_fb_t* frame);
    void setThreshold(int threshold);
    void setSensitivity(int sensitivity);
    int getMotionLevel();
    
private:
    uint8_t* previousFrame;
    int frameWidth;
    int frameHeight;
    int threshold;
    int motionLevel;
    
    int compareFrames(uint8_t* frame1, uint8_t* frame2);
}};

#endif // MOTION_DETECTION_H
"""

    def _generate_motion_implementation(self) -> str:
        """Generate motion detection implementation."""
        return """
// Motion Detection Implementation
#include "motion_detection.h"
#include <stdlib.h>

MotionDetector::MotionDetector() 
    : previousFrame(nullptr), frameWidth(0), frameHeight(0), 
      threshold(MOTION_THRESHOLD), motionLevel(0) {}

bool MotionDetector::begin() {
    return true;
}

bool MotionDetector::detectMotion(camera_fb_t* frame) {
    if (!frame || frame->format != PIXFORMAT_GRAYSCALE) {
        return false;
    }
    
    if (previousFrame == nullptr) {
        frameWidth = frame->width;
        frameHeight = frame->height;
        previousFrame = (uint8_t*)malloc(frame->len);
        memcpy(previousFrame, frame->buf, frame->len);
        return false;
    }
    
    motionLevel = compareFrames(previousFrame, frame->buf);
    memcpy(previousFrame, frame->buf, frame->len);
    
    return motionLevel > threshold;
}

void MotionDetector::setThreshold(int newThreshold) {
    threshold = newThreshold;
}

void MotionDetector::setSensitivity(int sensitivity) {
    // Map sensitivity 1-10 to threshold
    threshold = 50 - (sensitivity * 4);
    if (threshold < 5) threshold = 5;
}

int MotionDetector::getMotionLevel() {
    return motionLevel;
}

int MotionDetector::compareFrames(uint8_t* frame1, uint8_t* frame2) {
    int diffSum = 0;
    int numPixels = frameWidth * frameHeight;
    
    for (int i = 0; i < numPixels; i++) {
        int diff = abs(frame1[i] - frame2[i]);
        if (diff > threshold) {
            diffSum += diff;
        }
    }
    
    return diffSum / numPixels;
}
"""


class QRScanner:
    """QR and barcode scanner for ESP32-CAM."""

    def __init__(self, camera):
        """
        Initialize QR scanner.

        Args:
            camera: ESP32Camera instance
        """
        self.camera = camera
        self.scan_count = 0
        self._last_scan = None

    def scan(self, frame: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Scan for QR codes in frame.

        Args:
            frame: Optional frame data

        Returns:
            Scan result or None
        """
        if frame is None and self.camera.initialized:
            frame = self.camera.capture_frame()

        if frame is None:
            return None

        # Placeholder implementation
        # In production, would use actual QR detection library
        self.scan_count += 1

        result = {
            "type": "QR",
            "data": "https://example.com",
            "timestamp": "2025-10-15T12:00:00Z",
        }
        self._last_scan = result

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get scanner statistics."""
        return {
            "scan_count": self.scan_count,
            "last_scan": self._last_scan,
        }

    def generate_qr_scanner_code(self) -> Dict[str, str]:
        """Generate QR scanner code for ESP32."""
        header = """
// QR Scanner for ESP32-CAM
#ifndef QR_SCANNER_H
#define QR_SCANNER_H

#include <esp_camera.h>

struct QRResult {
    bool found;
    char data[256];
    char type[32];
};

class QRScanner {
public:
    QRScanner();
    bool begin();
    QRResult scan(camera_fb_t* frame);
    int getScanCount();
    
private:
    int scanCount;
};

#endif // QR_SCANNER_H
"""
        implementation = """
// QR Scanner Implementation
#include "qr_scanner.h"
#include <string.h>

QRScanner::QRScanner() : scanCount(0) {}

bool QRScanner::begin() {
    return true;
}

QRResult QRScanner::scan(camera_fb_t* frame) {
    QRResult result;
    result.found = false;
    
    if (!frame) {
        return result;
    }
    
    // Placeholder - would integrate with quirc or other QR library
    scanCount++;
    
    return result;
}

int QRScanner::getScanCount() {
    return scanCount;
}
"""
        return {
            "qr_scanner.h": header,
            "qr_scanner.cpp": implementation,
        }
