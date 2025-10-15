"""
Multi-protocol streaming support for ESP32-CAM.
Supports RTSP, MJPEG, and WebRTC streaming protocols.
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class StreamingProtocol(Enum):
    """Supported streaming protocols."""
    MJPEG = "mjpeg"
    RTSP = "rtsp"
    WEBRTC = "webrtc"
    HTTP = "http"


class StreamQuality(Enum):
    """Stream quality presets."""
    LOW = "low"          # 320x240, high compression
    MEDIUM = "medium"    # 640x480, medium compression
    HIGH = "high"        # 800x600, low compression
    ULTRA = "ultra"      # 1024x768+, minimal compression


@dataclass
class StreamConfig:
    """Streaming configuration."""
    protocol: StreamingProtocol = StreamingProtocol.MJPEG
    quality: StreamQuality = StreamQuality.MEDIUM
    
    # Network settings
    port: int = 8080
    max_clients: int = 5
    buffer_size: int = 32768
    
    # Performance settings
    fps_target: int = 15
    enable_adaptive_quality: bool = True
    bandwidth_limit_kbps: Optional[int] = None
    
    # RTSP specific
    rtsp_path: str = "/stream"
    rtsp_auth_required: bool = False
    rtsp_username: Optional[str] = None
    rtsp_password: Optional[str] = None
    
    # WebRTC specific
    webrtc_stun_server: Optional[str] = None
    webrtc_turn_server: Optional[str] = None
    webrtc_ice_servers: list = None
    
    # Bandwidth optimization
    enable_compression: bool = True
    dynamic_bitrate: bool = True
    
    def __post_init__(self):
        if self.webrtc_ice_servers is None:
            self.webrtc_ice_servers = []


class StreamingManager:
    """
    Manages camera streaming with multiple protocol support.
    """
    
    def __init__(self, camera, config: Optional[StreamConfig] = None):
        """
        Initialize streaming manager.
        
        Args:
            camera: ESP32Camera instance
            config: Streaming configuration
        """
        self.camera = camera
        self.config = config or StreamConfig()
        self.active_streams = {}
        self.client_count = 0
        self.bytes_sent = 0
        self.frames_sent = 0
        
        logger.info(f"StreamingManager initialized with protocol: {self.config.protocol.value}")
    
    def start_stream(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start streaming.
        
        Args:
            stream_id: Optional stream identifier
        
        Returns:
            Stream information including URLs
        """
        if not self.camera.initialized:
            logger.error("Camera not initialized")
            return {"status": "error", "message": "Camera not initialized"}
        
        stream_id = stream_id or f"stream_{len(self.active_streams)}"
        
        # Apply quality settings
        self._apply_quality_settings()
        
        # Generate stream URLs
        urls = self._generate_stream_urls()
        
        stream_info = {
            "stream_id": stream_id,
            "protocol": self.config.protocol.value,
            "quality": self.config.quality.value,
            "urls": urls,
            "status": "active",
            "port": self.config.port,
        }
        
        self.active_streams[stream_id] = stream_info
        logger.info(f"Stream started: {stream_id}")
        
        return stream_info
    
    def stop_stream(self, stream_id: str) -> bool:
        """
        Stop a specific stream.
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            True if successful
        """
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            logger.info(f"Stream stopped: {stream_id}")
            return True
        
        logger.warning(f"Stream not found: {stream_id}")
        return False
    
    def stop_all_streams(self):
        """Stop all active streams."""
        stream_ids = list(self.active_streams.keys())
        for stream_id in stream_ids:
            self.stop_stream(stream_id)
        
        logger.info("All streams stopped")
    
    def _apply_quality_settings(self):
        """Apply quality preset to camera."""
        quality_map = {
            StreamQuality.LOW: {"frame_size": "QVGA", "jpeg_quality": 25},
            StreamQuality.MEDIUM: {"frame_size": "VGA", "jpeg_quality": 12},
            StreamQuality.HIGH: {"frame_size": "SVGA", "jpeg_quality": 8},
            StreamQuality.ULTRA: {"frame_size": "XGA", "jpeg_quality": 5},
        }
        
        settings = quality_map.get(self.config.quality, quality_map[StreamQuality.MEDIUM])
        self.camera.set_quality(settings["jpeg_quality"])
        logger.debug(f"Applied quality settings: {settings}")
    
    def _generate_stream_urls(self) -> Dict[str, str]:
        """Generate stream URLs for different protocols."""
        base_url = f"http://camera-device:{self.config.port}"
        
        urls = {}
        
        if self.config.protocol == StreamingProtocol.MJPEG:
            urls["mjpeg"] = f"{base_url}/stream"
            urls["snapshot"] = f"{base_url}/capture"
        
        elif self.config.protocol == StreamingProtocol.RTSP:
            urls["rtsp"] = f"rtsp://camera-device:{self.config.port}{self.config.rtsp_path}"
        
        elif self.config.protocol == StreamingProtocol.WEBRTC:
            urls["webrtc"] = f"{base_url}/webrtc"
            urls["signaling"] = f"ws://camera-device:{self.config.port}/ws"
        
        elif self.config.protocol == StreamingProtocol.HTTP:
            urls["stream"] = f"{base_url}/stream"
            urls["control"] = f"{base_url}/control"
        
        return urls
    
    def get_stream_stats(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get streaming statistics.
        
        Args:
            stream_id: Optional stream ID, returns all if None
        
        Returns:
            Statistics dictionary
        """
        if stream_id and stream_id in self.active_streams:
            return {
                "stream_id": stream_id,
                "status": self.active_streams[stream_id]["status"],
                "clients": self.client_count,
                "frames_sent": self.frames_sent,
                "bytes_sent": self.bytes_sent,
            }
        
        return {
            "active_streams": len(self.active_streams),
            "total_clients": self.client_count,
            "total_frames": self.frames_sent,
            "total_bytes": self.bytes_sent,
            "streams": list(self.active_streams.keys()),
        }
    
    def generate_streaming_code(self) -> Dict[str, str]:
        """
        Generate firmware code for streaming.
        
        Returns:
            Dictionary with code files
        """
        if self.config.protocol == StreamingProtocol.MJPEG:
            return self._generate_mjpeg_code()
        elif self.config.protocol == StreamingProtocol.RTSP:
            return self._generate_rtsp_code()
        elif self.config.protocol == StreamingProtocol.WEBRTC:
            return self._generate_webrtc_code()
        else:
            return self._generate_http_code()
    
    def _generate_mjpeg_code(self) -> Dict[str, str]:
        """Generate MJPEG streaming code."""
        header = """
// MJPEG Streaming for ESP32-CAM
#ifndef MJPEG_STREAM_H
#define MJPEG_STREAM_H

#include <WiFi.h>
#include <WebServer.h>
#include <esp_camera.h>

class MJPEGStreamer {
public:
    void begin(int port);
    void handle();
    void sendFrame(camera_fb_t *fb);
private:
    WebServer server;
};

#endif
"""
        
        implementation = f"""
// MJPEG Streaming Implementation
#include "mjpeg_stream.h"

WebServer mjpegServer({self.config.port});

void handleStream() {{
    WiFiClient client = mjpegServer.client();
    
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
    client.println();
    
    while (client.connected()) {{
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {{
            continue;
        }}
        
        client.print("--frame\\r\\n");
        client.print("Content-Type: image/jpeg\\r\\n");
        client.printf("Content-Length: %d\\r\\n\\r\\n", fb->len);
        client.write(fb->buf, fb->len);
        client.print("\\r\\n");
        
        esp_camera_fb_return(fb);
        
        delay({1000 // self.config.fps_target});
    }}
}}

void MJPEGStreamer::begin(int port) {{
    mjpegServer.on("/stream", handleStream);
    mjpegServer.begin(port);
}}

void MJPEGStreamer::handle() {{
    mjpegServer.handleClient();
}}
"""
        
        return {
            "mjpeg_stream.h": header,
            "mjpeg_stream.cpp": implementation,
        }
    
    def _generate_rtsp_code(self) -> Dict[str, str]:
        """Generate RTSP streaming code."""
        header = f"""
// RTSP Streaming for ESP32-CAM
#ifndef RTSP_STREAM_H
#define RTSP_STREAM_H

#include <esp_camera.h>

class RTSPStreamer {{
public:
    void begin(const char* path, int port = {self.config.port});
    void handle();
    void sendFrame(camera_fb_t *fb);
private:
    const char* streamPath;
    int serverPort;
}};

#endif
"""
        
        implementation = """
// RTSP Streaming Implementation
// Requires additional RTSP server library
#include "rtsp_stream.h"

void RTSPStreamer::begin(const char* path, int port) {
    streamPath = path;
    serverPort = port;
    // Initialize RTSP server
}

void RTSPStreamer::handle() {
    // Handle RTSP requests
}

void RTSPStreamer::sendFrame(camera_fb_t *fb) {
    // Send frame via RTSP
}
"""
        
        return {
            "rtsp_stream.h": header,
            "rtsp_stream.cpp": implementation,
        }
    
    def _generate_webrtc_code(self) -> Dict[str, str]:
        """Generate WebRTC streaming code."""
        header = """
// WebRTC Streaming for ESP32-CAM
#ifndef WEBRTC_STREAM_H
#define WEBRTC_STREAM_H

#include <esp_camera.h>
#include <WebSocketsServer.h>

class WebRTCStreamer {
public:
    void begin(int port);
    void handle();
private:
    WebSocketsServer* wsServer;
};

#endif
"""
        
        implementation = f"""
// WebRTC Streaming Implementation
#include "webrtc_stream.h"

void WebRTCStreamer::begin(int port) {{
    wsServer = new WebSocketsServer(port);
    wsServer->begin();
}}

void WebRTCStreamer::handle() {{
    wsServer->loop();
}}
"""
        
        return {
            "webrtc_stream.h": header,
            "webrtc_stream.cpp": implementation,
        }
    
    def _generate_http_code(self) -> Dict[str, str]:
        """Generate HTTP streaming code."""
        return {
            "http_stream.h": "// HTTP streaming header",
            "http_stream.cpp": "// HTTP streaming implementation",
        }
