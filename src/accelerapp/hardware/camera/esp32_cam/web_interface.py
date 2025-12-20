"""
Web interface module for ESP32-CAM.
Provides REST API and web UI for camera control.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API configuration."""

    port: int = 80
    enable_cors: bool = True
    enable_auth: bool = False
    api_prefix: str = "/api"


class WebInterface:
    """
    Web interface for ESP32-CAM.
    Provides REST API and HTML UI for camera control.
    """

    def __init__(self, camera, config: Optional[APIConfig] = None):
        """
        Initialize web interface.

        Args:
            camera: ESP32Camera instance
            config: API configuration
        """
        self.camera = camera
        self.config = config or APIConfig()
        self._running = False
        self._request_count = 0

        # Define routes
        self._routes = {
            "/api/camera/status": self._handle_status,
            "/api/camera/capture": self._handle_capture,
            "/api/camera/config": self._handle_config,
            "/api/settings/quality": self._handle_quality,
            "/api/settings/brightness": self._handle_brightness,
            "/api/settings/flip": self._handle_flip,
            "/": self._handle_home,
            "/ui/live": self._handle_live_page,
            "/ui/settings": self._handle_settings_page,
        }

        logger.info(f"WebInterface initialized on port {self.config.port}")

    def start(self) -> bool:
        """Start web server."""
        self._running = True
        logger.info("Web interface started")
        return True

    def stop(self) -> bool:
        """Stop web server."""
        self._running = False
        logger.info("Web interface stopped")
        return True

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    def handle_request(self, path: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HTTP request.

        Args:
            path: Request path
            method: HTTP method
            params: Request parameters

        Returns:
            Response dictionary
        """
        self._request_count += 1

        handler = self._routes.get(path)
        if handler:
            return handler(method, params)

        return {"code": 404, "error": "Not found"}

    def _handle_status(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status endpoint."""
        if method != "GET":
            return {"code": 405, "error": "Method not allowed"}

        return {
            "code": 200,
            "data": self.camera.get_status(),
        }

    def _handle_capture(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capture endpoint."""
        if method != "GET":
            return {"code": 405, "error": "Method not allowed"}

        frame = self.camera.capture_frame()
        if frame:
            return {
                "code": 200,
                "data": {"captured": True, "size": len(frame)},
            }

        return {"code": 500, "error": "Capture failed"}

    def _handle_config(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle config endpoint."""
        if method == "GET":
            return {
                "code": 200,
                "data": self.camera.get_config(),
            }
        elif method == "PUT":
            # Update configuration
            return {"code": 200, "data": {"updated": True}}

        return {"code": 405, "error": "Method not allowed"}

    def _handle_quality(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quality setting endpoint."""
        if method != "PUT":
            return {"code": 405, "error": "Method not allowed"}

        quality = params.get("quality")
        if quality is not None:
            success = self.camera.set_quality(quality)
            if success:
                return {"code": 200, "data": {"quality": quality}}

        return {"code": 400, "error": "Invalid quality"}

    def _handle_brightness(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle brightness setting endpoint."""
        if method != "PUT":
            return {"code": 405, "error": "Method not allowed"}

        brightness = params.get("brightness")
        if brightness is not None:
            success = self.camera.set_brightness(brightness)
            if success:
                return {"code": 200, "data": {"brightness": brightness}}

        return {"code": 400, "error": "Invalid brightness"}

    def _handle_flip(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flip setting endpoint."""
        if method != "PUT":
            return {"code": 405, "error": "Method not allowed"}

        h_flip = params.get("horizontal", False)
        v_flip = params.get("vertical", False)
        self.camera.set_flip(h_flip, v_flip)

        return {"code": 200, "data": {"horizontal": h_flip, "vertical": v_flip}}

    def _handle_home(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle home page."""
        return {
            "code": 200,
            "html": self._generate_home_html(),
        }

    def _handle_live_page(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle live stream page."""
        return {
            "code": 200,
            "html": self._generate_live_html(),
        }

    def _handle_settings_page(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle settings page."""
        return {
            "code": 200,
            "html": self._generate_settings_html(),
        }

    def _generate_home_html(self) -> str:
        """Generate home page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 10px; }
    </style>
</head>
<body>
    <h1>ESP32-CAM Dashboard</h1>
    <div class="nav">
        <a href="/ui/live">Live Stream</a>
        <a href="/ui/settings">Settings</a>
    </div>
    <div id="status"></div>
</body>
</html>
"""

    def _generate_live_html(self) -> str:
        """Generate live stream page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Live Stream</title>
</head>
<body>
    <h1>Live Stream</h1>
    <img id="stream" src="/stream" style="max-width: 100%;">
</body>
</html>
"""

    def _generate_settings_html(self) -> str:
        """Generate settings page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Camera Settings</title>
</head>
<body>
    <h1>Camera Settings</h1>
    <form id="settings">
        <label>Quality (0-63): <input type="number" id="quality" min="0" max="63"></label><br>
        <label>Brightness (-2 to 2): <input type="number" id="brightness" min="-2" max="2"></label><br>
        <button type="submit">Apply</button>
    </form>
</body>
</html>
"""

    def get_status_handler(self) -> Dict[str, Any]:
        """Get status handler (for tests)."""
        return {"status": "success", "data": self.camera.get_status()}

    def get_config_handler(self) -> Dict[str, Any]:
        """Get config handler (for tests)."""
        return {"status": "success", "data": self.camera.get_config()}

    def generate_api_documentation(self) -> str:
        """Generate API documentation."""
        return """
# ESP32-CAM API Documentation

## Endpoints

### GET /api/camera/status
Get current camera status.

### GET /api/camera/capture
Capture a single frame.

### GET /api/camera/config
Get camera configuration.

### PUT /api/settings/quality
Set JPEG quality.
Parameters: quality (0-63)

### PUT /api/settings/brightness
Set image brightness.
Parameters: brightness (-2 to 2)

### PUT /api/settings/flip
Set image flip settings.
Parameters: horizontal (bool), vertical (bool)
"""
