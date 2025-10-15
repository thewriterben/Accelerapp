"""
MJPEG streaming protocol implementation.
"""

from typing import Dict, Any, Optional


class MJPEGProtocol:
    """
    MJPEG (Motion JPEG) streaming protocol.
    Simple HTTP-based video streaming using sequential JPEG frames.
    """
    
    def __init__(self, camera):
        """
        Initialize MJPEG protocol handler.
        
        Args:
            camera: ESP32Camera instance
        """
        self.camera = camera
        self._streaming = False
        self._frame_count = 0
    
    def start_stream(self, port: int = 81) -> bool:
        """
        Start MJPEG streaming.
        
        Args:
            port: HTTP port for streaming
            
        Returns:
            True if stream started successfully
        """
        if not self.camera._initialized:
            if not self.camera.initialize():
                return False
        
        self._streaming = True
        return True
    
    def stop_stream(self) -> bool:
        """
        Stop MJPEG streaming.
        
        Returns:
            True if stream stopped successfully
        """
        self._streaming = False
        return True
    
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._streaming
    
    def get_stream_header(self) -> Dict[str, str]:
        """
        Get HTTP headers for MJPEG stream.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Content-Type": "multipart/x-mixed-replace; boundary=frame",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    
    def format_frame(self, frame_data: bytes) -> bytes:
        """
        Format frame data for MJPEG stream.
        
        Args:
            frame_data: JPEG frame data
            
        Returns:
            Formatted frame with MJPEG boundaries
        """
        header = b"--frame\r\n"
        header += b"Content-Type: image/jpeg\r\n"
        header += f"Content-Length: {len(frame_data)}\r\n\r\n".encode()
        
        self._frame_count += 1
        return header + frame_data + b"\r\n"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get protocol status.
        
        Returns:
            Status dictionary
        """
        return {
            "protocol": "MJPEG",
            "streaming": self._streaming,
            "frames_sent": self._frame_count,
            "default_port": 81,
        }
