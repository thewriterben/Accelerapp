"""
Streaming module for ESP32-CAM.
Provides MJPEG, RTSP, and WebRTC streaming capabilities.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
import logging
import uuid

logger = logging.getLogger(__name__)


class StreamingProtocol(Enum):
    """Supported streaming protocols."""

    MJPEG = "mjpeg"
    RTSP = "rtsp"
    WEBRTC = "webrtc"
    HTTP = "http"


@dataclass
class StreamConfig:
    """Streaming configuration."""

    protocol: StreamingProtocol = StreamingProtocol.MJPEG
    port: int = 81
    max_clients: int = 4
    frame_interval_ms: int = 100  # 10 FPS default
    quality: int = 12
    enable_audio: bool = False
    auth_required: bool = False


class StreamingManager:
    """
    Manages video streaming for ESP32-CAM.
    Supports multiple streaming protocols and clients.
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
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.frame_count = 0

        logger.info(f"StreamingManager initialized with {self.config.protocol.value}")

    def start_stream(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new stream.

        Args:
            stream_id: Optional stream identifier

        Returns:
            Stream information
        """
        if stream_id is None:
            stream_id = f"stream_{uuid.uuid4().hex[:8]}"

        stream_info = {
            "stream_id": stream_id,
            "protocol": self.config.protocol.value,
            "status": "active",
            "port": self.config.port,
            "urls": self._get_stream_urls(stream_id),
            "clients": 0,
        }

        self.active_streams[stream_id] = stream_info
        logger.info(f"Started stream: {stream_id}")

        return stream_info

    def stop_stream(self, stream_id: str) -> bool:
        """
        Stop an active stream.

        Args:
            stream_id: Stream identifier

        Returns:
            True if stream stopped successfully
        """
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            logger.info(f"Stopped stream: {stream_id}")
            return True
        return False

    def _get_stream_urls(self, stream_id: str) -> Dict[str, str]:
        """
        Get URLs for different streaming protocols.

        Args:
            stream_id: Stream identifier

        Returns:
            Dictionary of protocol URLs
        """
        base_host = "192.168.1.100"  # Would be actual IP in production
        port = self.config.port

        urls = {}
        if self.config.protocol == StreamingProtocol.MJPEG:
            urls["mjpeg"] = f"http://{base_host}:{port}/stream"
            urls["snapshot"] = f"http://{base_host}:{port}/capture"
        elif self.config.protocol == StreamingProtocol.RTSP:
            urls["rtsp"] = f"rtsp://{base_host}:{port}/{stream_id}"
        elif self.config.protocol == StreamingProtocol.WEBRTC:
            urls["webrtc"] = f"wss://{base_host}:{port}/webrtc/{stream_id}"
        elif self.config.protocol == StreamingProtocol.HTTP:
            urls["http"] = f"http://{base_host}:{port}/video/{stream_id}"

        return urls

    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a stream."""
        return self.active_streams.get(stream_id)

    def get_all_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get all active streams."""
        return self.active_streams.copy()

    def add_client(self, stream_id: str, client_info: Dict[str, Any]) -> bool:
        """Add a client to a stream."""
        if stream_id not in self.active_streams:
            return False

        client_id = f"client_{uuid.uuid4().hex[:8]}"
        self.clients[client_id] = {
            "stream_id": stream_id,
            **client_info,
        }
        self.active_streams[stream_id]["clients"] += 1
        return True

    def remove_client(self, client_id: str) -> bool:
        """Remove a client from its stream."""
        if client_id in self.clients:
            stream_id = self.clients[client_id]["stream_id"]
            if stream_id in self.active_streams:
                self.active_streams[stream_id]["clients"] -= 1
            del self.clients[client_id]
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get streaming statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "active_streams": len(self.active_streams),
            "total_clients": len(self.clients),
            "protocol": self.config.protocol.value,
            "frame_count": self.frame_count,
        }

    def generate_streaming_code(self) -> Dict[str, str]:
        """
        Generate ESP32 streaming code.

        Returns:
            Dictionary with code files
        """
        header = self._generate_streaming_header()
        implementation = self._generate_streaming_implementation()

        return {
            "mjpeg_stream.h": header,
            "mjpeg_stream.cpp": implementation,
        }

    def _generate_streaming_header(self) -> str:
        """Generate streaming header file."""
        return """
// MJPEG Streaming for ESP32-CAM
#ifndef MJPEG_STREAM_H
#define MJPEG_STREAM_H

#include <esp_camera.h>
#include <WebServer.h>

class MJPEGStream {
public:
    MJPEGStream(int port = 81);
    bool begin();
    void handleClient();
    void stop();
    
    int getClientCount();
    unsigned long getFrameCount();
    
private:
    WebServer* server;
    int port;
    int clientCount;
    unsigned long frameCount;
    
    void handleStream();
    void handleCapture();
};

#endif // MJPEG_STREAM_H
"""

    def _generate_streaming_implementation(self) -> str:
        """Generate streaming implementation file."""
        return f"""
// MJPEG Streaming Implementation
#include "mjpeg_stream.h"

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\\r\\n--" PART_BOUNDARY "\\r\\n";
static const char* STREAM_PART = "Content-Type: image/jpeg\\r\\nContent-Length: %u\\r\\n\\r\\n";

MJPEGStream::MJPEGStream(int port) : port(port), clientCount(0), frameCount(0) {{
    server = new WebServer(port);
}}

bool MJPEGStream::begin() {{
    server->on("/stream", HTTP_GET, [this]() {{ handleStream(); }});
    server->on("/capture", HTTP_GET, [this]() {{ handleCapture(); }});
    server->begin();
    return true;
}}

void MJPEGStream::handleClient() {{
    server->handleClient();
}}

void MJPEGStream::handleStream() {{
    WiFiClient client = server->client();
    
    String response = "HTTP/1.1 200 OK\\r\\n";
    response += "Content-Type: " + String(STREAM_CONTENT_TYPE) + "\\r\\n\\r\\n";
    server->sendContent(response);
    
    clientCount++;
    
    while (client.connected()) {{
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {{
            continue;
        }}
        
        String header = String(STREAM_BOUNDARY);
        char partHeader[64];
        sprintf(partHeader, STREAM_PART, fb->len);
        header += partHeader;
        
        server->sendContent(header);
        client.write(fb->buf, fb->len);
        
        esp_camera_fb_return(fb);
        frameCount++;
        
        delay({self.config.frame_interval_ms});
    }}
    
    clientCount--;
}}

void MJPEGStream::handleCapture() {{
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {{
        server->send(500, "text/plain", "Camera capture failed");
        return;
    }}
    
    server->sendHeader("Content-Type", "image/jpeg");
    server->sendHeader("Content-Length", String(fb->len));
    server->send_P(200, "image/jpeg", (const char*)fb->buf, fb->len);
    
    esp_camera_fb_return(fb);
}}

void MJPEGStream::stop() {{
    server->stop();
}}

int MJPEGStream::getClientCount() {{
    return clientCount;
}}

unsigned long MJPEGStream::getFrameCount() {{
    return frameCount;
}}
"""
