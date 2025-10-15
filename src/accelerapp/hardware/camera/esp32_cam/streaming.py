"""

    """Supported streaming protocols."""
    MJPEG = "mjpeg"
    RTSP = "rtsp"
    WEBRTC = "webrtc"



@dataclass
class StreamConfig:

        
        Args:
            camera: ESP32Camera instance
            config: Streaming configuration
        """
        self.camera = camera

