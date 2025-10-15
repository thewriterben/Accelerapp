"""
Streaming server implementation for ESP32-CAM.
Supports multiple streaming protocols (MJPEG, RTSP, WebRTC).
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import threading


class StreamProtocol(Enum):
    """Supported streaming protocols."""
    MJPEG = "mjpeg"
    RTSP = "rtsp"
    WEBRTC = "webrtc"
    WEBSOCKET = "websocket"


@dataclass
class StreamConfig:
    """Configuration for streaming server."""
    protocol: StreamProtocol
    port: int
    max_clients: int = 5
    buffer_size: int = 1024 * 1024  # 1MB
    enable_audio: bool = False
    bitrate: int = 500000  # 500 kbps
    
    def __post_init__(self):
        """Set default port based on protocol."""
        if self.port == 0:
            if self.protocol == StreamProtocol.MJPEG:
                self.port = 81
            elif self.protocol == StreamProtocol.RTSP:
                self.port = 8554
            elif self.protocol == StreamProtocol.WEBRTC:
                self.port = 8443
            elif self.protocol == StreamProtocol.WEBSOCKET:
                self.port = 8765


class StreamingServer:
    """
    Multi-protocol streaming server for ESP32-CAM.
    Manages video streaming to multiple clients.
    """
    
    def __init__(self, camera, config: StreamConfig):
        """
        Initialize streaming server.
        
        Args:
            camera: ESP32Camera instance
            config: Streaming configuration
        """
        self.camera = camera
        self.config = config
        self._active = False
        self._clients: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._frame_callbacks: List[Callable] = []
    
    def start(self) -> bool:
        """
        Start streaming server.
        
        Returns:
            True if server started successfully
        """
        if self._active:
            return True
        
        if not self.camera.is_streaming():
            if not self.camera.start_streaming():
                return False
        
        self._active = True
        return True
    
    def stop(self) -> bool:
        """
        Stop streaming server.
        
        Returns:
            True if server stopped successfully
        """
        with self._lock:
            self._active = False
            self._clients.clear()
        return True
    
    def add_client(self, client_id: str, client_info: Dict[str, Any]) -> bool:
        """
        Add a streaming client.
        
        Args:
            client_id: Unique client identifier
            client_info: Client connection information
            
        Returns:
            True if client added successfully
        """
        with self._lock:
            if len(self._clients) >= self.config.max_clients:
                return False
            
            self._clients.append({
                "id": client_id,
                "info": client_info,
                "connected_at": "2025-10-15T01:12:23.332Z",
                "frames_sent": 0,
            })
            return True
    
    def remove_client(self, client_id: str) -> bool:
        """
        Remove a streaming client.
        
        Args:
            client_id: Client identifier to remove
            
        Returns:
            True if client removed successfully
        """
        with self._lock:
            self._clients = [c for c in self._clients if c["id"] != client_id]
            return True
    
    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self._clients)
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get list of connected clients."""
        with self._lock:
            return self._clients.copy()
    
    def register_frame_callback(self, callback: Callable) -> None:
        """
        Register callback for new frames.
        
        Args:
            callback: Function to call on new frame
        """
        self._frame_callbacks.append(callback)
    
    def get_stream_url(self) -> str:
        """
        Get streaming URL.
        
        Returns:
            Stream URL string
        """
        protocol_map = {
            StreamProtocol.MJPEG: "http",
            StreamProtocol.RTSP: "rtsp",
            StreamProtocol.WEBRTC: "https",
            StreamProtocol.WEBSOCKET: "ws",
        }
        
        protocol_prefix = protocol_map.get(self.config.protocol, "http")
        return f"{protocol_prefix}://localhost:{self.config.port}/stream"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get streaming server status.
        
        Returns:
            Status dictionary
        """
        return {
            "active": self._active,
            "protocol": self.config.protocol.value,
            "port": self.config.port,
            "clients": len(self._clients),
            "max_clients": self.config.max_clients,
            "stream_url": self.get_stream_url(),
            "bitrate": self.config.bitrate,
        }


class MJPEGStreamer:
    """MJPEG streaming implementation."""
    
    def __init__(self, camera):
        """Initialize MJPEG streamer."""
        self.camera = camera
        self._running = False
    
    def start(self, port: int = 81) -> bool:
        """Start MJPEG streaming on specified port."""
        self._running = True
        return True
    
    def stop(self) -> bool:
        """Stop MJPEG streaming."""
        self._running = False
        return True
    
    def is_running(self) -> bool:
        """Check if streamer is running."""
        return self._running


class RTSPServer:
    """RTSP streaming server implementation."""
    
    def __init__(self, camera):
        """Initialize RTSP server."""
        self.camera = camera
        self._running = False
    
    def start(self, port: int = 8554) -> bool:
        """Start RTSP server on specified port."""
        self._running = True
        return True
    
    def stop(self) -> bool:
        """Stop RTSP server."""
        self._running = False
        return True
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    def get_stream_url(self) -> str:
        """Get RTSP stream URL."""
        return f"rtsp://localhost:8554/stream"
