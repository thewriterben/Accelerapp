"""
Motion detection and QR code scanning for ESP32-CAM.
"""

from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MotionAlgorithm(Enum):
    """Motion detection algorithms."""
    FRAME_DIFF = "frame_diff"
    BACKGROUND_SUBTRACTION = "background_subtraction"
    OPTICAL_FLOW = "optical_flow"


class QRCodeType(Enum):
    """QR code types."""
    QR_CODE = "qr_code"
    MICRO_QR = "micro_qr"
    DATA_MATRIX = "data_matrix"
    AZTEC = "aztec"


@dataclass
class MotionConfig:
    """Motion detection configuration."""
    algorithm: MotionAlgorithm = MotionAlgorithm.FRAME_DIFF
    
    # Sensitivity settings
    threshold: int = 20  # Pixel difference threshold
    min_area: int = 500  # Minimum area for motion detection
    
    # Detection zones (list of rectangles)
    detection_zones: List[tuple] = field(default_factory=list)
    
    # Temporal filtering
    frame_skip: int = 2  # Process every Nth frame
    history_frames: int = 3  # Frames to keep for comparison
    
    # Event handling
    enable_events: bool = True
    cooldown_seconds: int = 5  # Min time between events
    
    # Recording
    record_on_motion: bool = False
    pre_record_seconds: int = 2
    post_record_seconds: int = 5


@dataclass
class MotionEvent:
    """Motion detection event."""
    timestamp: datetime
    confidence: float
    area: int
    bbox: tuple  # (x, y, width, height)
    frame_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MotionDetector:
    """
    Motion detection engine for ESP32-CAM.
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
        self.previous_frames = []
        self.motion_detected = False
        self.last_motion_time = None
        self.event_history = []
        self.event_callbacks = []
        
        logger.info(f"MotionDetector initialized with algorithm: {self.config.algorithm.value}")
    
    def detect_motion(self, frame: Optional[bytes] = None) -> bool:
        """
        Detect motion in current frame.
        
        Args:
            frame: Optional frame data, captures new frame if None
        
        Returns:
            True if motion detected
        """
        try:
            # Capture frame if not provided
            if frame is None and self.camera.initialized:
                frame = self.camera.capture_frame()
            
            if frame is None:
                logger.error("No frame available for motion detection")
                return False
            
            # Add to frame history
            self.previous_frames.append(frame)
            if len(self.previous_frames) > self.config.history_frames:
                self.previous_frames.pop(0)
            
            # Need at least 2 frames for comparison
            if len(self.previous_frames) < 2:
                return False
            
            # Detect motion based on algorithm
            motion_info = self._detect_motion_internal()
            
            if motion_info and motion_info["detected"]:
                self._handle_motion_event(motion_info)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Motion detection failed: {e}")
            return False
    
    def _detect_motion_internal(self) -> Optional[Dict[str, Any]]:
        """
        Internal motion detection logic.
        
        Returns:
            Motion information dictionary or None
        """
        if self.config.algorithm == MotionAlgorithm.FRAME_DIFF:
            return self._detect_frame_diff()
        elif self.config.algorithm == MotionAlgorithm.BACKGROUND_SUBTRACTION:
            return self._detect_background_subtraction()
        elif self.config.algorithm == MotionAlgorithm.OPTICAL_FLOW:
            return self._detect_optical_flow()
        
        return None
    
    def _detect_frame_diff(self) -> Optional[Dict[str, Any]]:
        """Frame difference algorithm."""
        # In production, this would:
        # 1. Convert frames to grayscale
        # 2. Calculate absolute difference
        # 3. Apply threshold
        # 4. Find contours
        # 5. Filter by area
        
        # Placeholder detection
        diff_pixels = 1500  # Simulated difference
        
        if diff_pixels > self.config.min_area:
            return {
                "detected": True,
                "confidence": min(diff_pixels / 10000, 1.0),
                "area": diff_pixels,
                "bbox": (10, 10, 100, 100),
            }
        
        return None
    
    def _detect_background_subtraction(self) -> Optional[Dict[str, Any]]:
        """Background subtraction algorithm."""
        # Placeholder
        return None
    
    def _detect_optical_flow(self) -> Optional[Dict[str, Any]]:
        """Optical flow algorithm."""
        # Placeholder
        return None
    
    def _handle_motion_event(self, motion_info: Dict[str, Any]):
        """Handle detected motion event."""
        now = datetime.now()
        
        # Check cooldown
        if self.last_motion_time:
            seconds_since = (now - self.last_motion_time).total_seconds()
            if seconds_since < self.config.cooldown_seconds:
                return
        
        self.last_motion_time = now
        self.motion_detected = True
        
        # Create event
        event = MotionEvent(
            timestamp=now,
            confidence=motion_info.get("confidence", 0.0),
            area=motion_info.get("area", 0),
            bbox=motion_info.get("bbox", (0, 0, 0, 0)),
        )
        
        self.event_history.append(event)
        
        # Keep only last 100 events
        if len(self.event_history) > 100:
            self.event_history = self.event_history[-100:]
        
        # Trigger callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Event callback failed: {e}")
        
        logger.info(f"Motion detected: confidence={event.confidence:.2f}, area={event.area}")
    
    def add_event_callback(self, callback: Callable):
        """Add callback for motion events."""
        self.event_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get motion detection statistics."""
        recent_events = self.event_history[-10:] if self.event_history else []
        
        return {
            "algorithm": self.config.algorithm.value,
            "motion_detected": self.motion_detected,
            "total_events": len(self.event_history),
            "last_motion": self.last_motion_time.isoformat() if self.last_motion_time else None,
            "recent_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "confidence": e.confidence,
                    "area": e.area,
                }
                for e in recent_events
            ],
        }
    
    def generate_motion_detection_code(self) -> Dict[str, str]:
        """Generate motion detection firmware code."""
        header = """
// Motion Detection for ESP32-CAM
#ifndef MOTION_DETECTION_H
#define MOTION_DETECTION_H

#include <esp_camera.h>

struct MotionResult {
    bool detected;
    float confidence;
    int area;
    int x, y, width, height;
};

class MotionDetector {
public:
    bool init(int threshold, int min_area);
    MotionResult detect(camera_fb_t *current_frame);
    
private:
    camera_fb_t *previous_frame;
    int threshold;
    int min_area;
};

#endif
"""
        
        implementation = f"""
// Motion Detection Implementation
#include "motion_detection.h"
#include <stdlib.h>

bool MotionDetector::init(int thresh, int min_a) {{
    threshold = thresh;
    min_area = min_a;
    previous_frame = nullptr;
    return true;
}}

MotionResult MotionDetector::detect(camera_fb_t *current_frame) {{
    MotionResult result = {{false, 0.0f, 0, 0, 0, 0, 0}};
    
    if (!previous_frame || !current_frame) {{
        previous_frame = current_frame;
        return result;
    }}
    
    // Calculate frame difference
    int diff_pixels = 0;
    int total_pixels = current_frame->width * current_frame->height;
    
    for (int i = 0; i < total_pixels; i++) {{
        int diff = abs(current_frame->buf[i] - previous_frame->buf[i]);
        if (diff > threshold) {{
            diff_pixels++;
        }}
    }}
    
    if (diff_pixels > min_area) {{
        result.detected = true;
        result.confidence = (float)diff_pixels / total_pixels;
        result.area = diff_pixels;
        // Bounding box calculation would go here
    }}
    
    previous_frame = current_frame;
    return result;
}}
"""
        
        return {
            "motion_detection.h": header,
            "motion_detection.cpp": implementation,
        }


class QRScanner:
    """
    QR code and barcode scanner for ESP32-CAM.
    """
    
    def __init__(self, camera):
        """
        Initialize QR scanner.
        
        Args:
            camera: ESP32Camera instance
        """
        self.camera = camera
        self.scan_count = 0
        self.last_scan_result = None
        self.scan_history = []
        
        logger.info("QRScanner initialized")
    
    def scan(self, frame: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Scan for QR codes in frame.
        
        Args:
            frame: Optional frame data
        
        Returns:
            Scan result dictionary or None
        """
        try:
            if frame is None and self.camera.initialized:
                frame = self.camera.capture_frame()
            
            if frame is None:
                return None
            
            # In production, this would use ESP32 QR decoder or quirc library
            result = self._decode_qr(frame)
            
            if result:
                self.scan_count += 1
                self.last_scan_result = result
                self.scan_history.append(result)
                
                # Keep only last 50 scans
                if len(self.scan_history) > 50:
                    self.scan_history = self.scan_history[-50:]
                
                logger.info(f"QR code detected: {result['data']}")
            
            return result
            
        except Exception as e:
            logger.error(f"QR scan failed: {e}")
            return None
    
    def _decode_qr(self, frame: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode QR code from frame.
        
        Args:
            frame: Frame data
        
        Returns:
            Decoded result or None
        """
        # Placeholder QR detection
        # In production, would use quirc or ESP32 QR library
        return {
            "type": "QR_CODE",
            "data": "https://example.com",
            "confidence": 0.95,
            "position": (50, 50, 100, 100),
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get QR scanner statistics."""
        return {
            "scan_count": self.scan_count,
            "last_scan": self.last_scan_result,
            "total_scans": len(self.scan_history),
        }
    
    def generate_qr_scanner_code(self) -> Dict[str, str]:
        """Generate QR scanning firmware code."""
        header = """
// QR Scanner for ESP32-CAM
#ifndef QR_SCANNER_H
#define QR_SCANNER_H

#include <esp_camera.h>

struct QRResult {
    bool found;
    char data[256];
    int x, y, width, height;
};

class QRScanner {
public:
    bool init();
    QRResult scan(camera_fb_t *frame);
};

#endif
"""
        
        implementation = """
// QR Scanner Implementation
// Requires quirc library or ESP32 QR decoder
#include "qr_scanner.h"

bool QRScanner::init() {
    // Initialize QR decoder
    return true;
}

QRResult QRScanner::scan(camera_fb_t *frame) {
    QRResult result = {false, "", 0, 0, 0, 0};
    
    // Decode QR code using quirc or ESP32 decoder
    // This would involve:
    // 1. Convert to grayscale if needed
    // 2. Run QR detector
    // 3. Decode data
    
    return result;
}
"""
        
        return {
            "qr_scanner.h": header,
            "qr_scanner.cpp": implementation,
        }
