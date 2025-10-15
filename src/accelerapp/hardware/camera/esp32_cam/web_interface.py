"""
Web interface and RESTful API for ESP32-CAM control.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class APIConfig:
    """API configuration."""
    enable_api: bool = True
    enable_web_ui: bool = True
    
    # Server settings
    port: int = 80
    enable_cors: bool = True
    cors_origins: List[str] = None
    
    # API endpoints
    api_prefix: str = "/api"
    enable_swagger: bool = True
    
    # Rate limiting
    enable_rate_limit: bool = True
    requests_per_minute: int = 60
    
    # UI settings
    ui_theme: str = "light"
    enable_live_preview: bool = True
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


class WebInterface:
    """
    Web interface and API for ESP32-CAM.
    Provides RESTful API and web-based management UI.
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
        self.routes = {}
        self.request_count = 0
        
        self._register_default_routes()
        
        logger.info(f"WebInterface initialized on port {self.config.port}")
    
    def _register_default_routes(self):
        """Register default API routes."""
        # Camera control routes
        self.routes["/api/camera/status"] = {"method": HTTPMethod.GET, "handler": self._handle_status}
        self.routes["/api/camera/capture"] = {"method": HTTPMethod.GET, "handler": self._handle_capture}
        self.routes["/api/camera/config"] = {"method": HTTPMethod.GET, "handler": self._handle_get_config}
        self.routes["/api/camera/config"] = {"method": HTTPMethod.PUT, "handler": self._handle_set_config}
        
        # Streaming routes
        self.routes["/api/stream/start"] = {"method": HTTPMethod.POST, "handler": self._handle_start_stream}
        self.routes["/api/stream/stop"] = {"method": HTTPMethod.POST, "handler": self._handle_stop_stream}
        self.routes["/api/stream/status"] = {"method": HTTPMethod.GET, "handler": self._handle_stream_status}
        
        # Settings routes
        self.routes["/api/settings/quality"] = {"method": HTTPMethod.PUT, "handler": self._handle_set_quality}
        self.routes["/api/settings/brightness"] = {"method": HTTPMethod.PUT, "handler": self._handle_set_brightness}
        self.routes["/api/settings/flip"] = {"method": HTTPMethod.PUT, "handler": self._handle_set_flip}
        
        # UI routes
        self.routes["/"] = {"method": HTTPMethod.GET, "handler": self._handle_ui_home}
        self.routes["/ui/live"] = {"method": HTTPMethod.GET, "handler": self._handle_ui_live}
        self.routes["/ui/settings"] = {"method": HTTPMethod.GET, "handler": self._handle_ui_settings}
    
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
        self.request_count += 1
        
        # Find matching route
        route_key = path
        if route_key in self.routes:
            route = self.routes[route_key]
            
            if route["method"].value == method:
                try:
                    return route["handler"](params)
                except Exception as e:
                    logger.error(f"Request handler error: {e}")
                    return {
                        "status": "error",
                        "message": str(e),
                        "code": 500,
                    }
        
        # Route not found
        return {
            "status": "error",
            "message": "Not found",
            "code": 404,
        }
    
    # API Handlers
    
    def _handle_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /api/camera/status"""
        return {
            "status": "success",
            "data": self.camera.get_status(),
            "code": 200,
        }
    
    def _handle_capture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /api/camera/capture"""
        frame = self.camera.capture_frame()
        
        if frame:
            return {
                "status": "success",
                "message": "Frame captured",
                "size": len(frame),
                "code": 200,
            }
        
        return {
            "status": "error",
            "message": "Capture failed",
            "code": 500,
        }
    
    def _handle_get_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET /api/camera/config"""
        return {
            "status": "success",
            "data": self.camera.get_config(),
            "code": 200,
        }
    
    def _handle_set_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT /api/camera/config"""
        # Apply configuration changes
        updated = []
        
        if "jpeg_quality" in params:
            if self.camera.set_quality(params["jpeg_quality"]):
                updated.append("jpeg_quality")
        
        if "brightness" in params:
            if self.camera.set_brightness(params["brightness"]):
                updated.append("brightness")
        
        return {
            "status": "success",
            "updated": updated,
            "code": 200,
        }
    
    def _handle_start_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST /api/stream/start"""
        return {
            "status": "success",
            "message": "Stream started",
            "stream_url": "/stream",
            "code": 200,
        }
    
    def _handle_stop_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST /api/stream/stop"""
        return {
            "status": "success",
            "message": "Stream stopped",
            "code": 200,
        }
    
    def _handle_stream_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET /api/stream/status"""
        return {
            "status": "success",
            "data": {
                "active": False,
                "protocol": "mjpeg",
            },
            "code": 200,
        }
    
    def _handle_set_quality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT /api/settings/quality"""
        quality = params.get("quality", 12)
        
        if self.camera.set_quality(quality):
            return {
                "status": "success",
                "quality": quality,
                "code": 200,
            }
        
        return {
            "status": "error",
            "message": "Invalid quality value",
            "code": 400,
        }
    
    def _handle_set_brightness(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT /api/settings/brightness"""
        brightness = params.get("brightness", 0)
        
        if self.camera.set_brightness(brightness):
            return {
                "status": "success",
                "brightness": brightness,
                "code": 200,
            }
        
        return {
            "status": "error",
            "message": "Invalid brightness value",
            "code": 400,
        }
    
    def _handle_set_flip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT /api/settings/flip"""
        horizontal = params.get("horizontal", False)
        vertical = params.get("vertical", False)
        
        if self.camera.set_flip(horizontal, vertical):
            return {
                "status": "success",
                "horizontal": horizontal,
                "vertical": vertical,
                "code": 200,
            }
        
        return {
            "status": "error",
            "message": "Failed to set flip",
            "code": 500,
        }
    
    # UI Handlers
    
    def _handle_ui_home(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle / - Home page"""
        return {
            "status": "success",
            "html": self._generate_home_page(),
            "code": 200,
        }
    
    def _handle_ui_live(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /ui/live - Live view page"""
        return {
            "status": "success",
            "html": self._generate_live_page(),
            "code": 200,
        }
    
    def _handle_ui_settings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /ui/settings - Settings page"""
        return {
            "status": "success",
            "html": self._generate_settings_page(),
            "code": 200,
        }
    
    def _generate_home_page(self) -> str:
        """Generate home page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
        .card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM Control Panel</h1>
        <div class="card">
            <h2>Quick Actions</h2>
            <button class="button" onclick="location.href='/ui/live'">Live View</button>
            <button class="button" onclick="location.href='/ui/settings'">Settings</button>
            <button class="button" onclick="captureImage()">Capture Image</button>
        </div>
        <div class="card">
            <h2>Status</h2>
            <p id="status">Loading...</p>
        </div>
    </div>
    <script>
        async function updateStatus() {
            const response = await fetch('/api/camera/status');
            const data = await response.json();
            document.getElementById('status').innerHTML = 
                'Initialized: ' + data.data.initialized + '<br>' +
                'Variant: ' + data.data.variant + '<br>' +
                'Frame Count: ' + data.data.frame_count;
        }
        async function captureImage() {
            await fetch('/api/camera/capture');
            alert('Image captured!');
        }
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
"""
    
    def _generate_live_page(self) -> str:
        """Generate live view page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Live View</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { margin: 0; background: #000; }
        .container { text-align: center; padding: 20px; }
        #stream { max-width: 100%; border: 2px solid #fff; }
        .controls { margin: 20px; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <img id="stream" src="/stream" alt="Camera Stream">
        <div class="controls">
            <button class="button" onclick="location.href='/'">Home</button>
            <button class="button" onclick="location.href='/ui/settings'">Settings</button>
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_settings_page(self) -> str:
        """Generate settings page HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Settings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .setting { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Camera Settings</h1>
        <div class="setting">
            <label>JPEG Quality (0-63):</label>
            <input type="number" id="quality" min="0" max="63" value="12">
        </div>
        <div class="setting">
            <label>Brightness (-2 to 2):</label>
            <input type="number" id="brightness" min="-2" max="2" value="0">
        </div>
        <div class="setting">
            <label>Horizontal Flip:</label>
            <input type="checkbox" id="hflip">
        </div>
        <div class="setting">
            <label>Vertical Flip:</label>
            <input type="checkbox" id="vflip">
        </div>
        <button class="button" onclick="saveSettings()">Save Settings</button>
        <button class="button" onclick="location.href='/'">Back</button>
    </div>
    <script>
        async function saveSettings() {
            await fetch('/api/settings/quality', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({quality: parseInt(document.getElementById('quality').value)})
            });
            await fetch('/api/settings/brightness', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({brightness: parseInt(document.getElementById('brightness').value)})
            });
            await fetch('/api/settings/flip', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    horizontal: document.getElementById('hflip').checked,
                    vertical: document.getElementById('vflip').checked
                })
            });
            alert('Settings saved!');
        }
    </script>
</body>
</html>
"""
    
    def generate_api_documentation(self) -> str:
        """Generate API documentation."""
        return """
# ESP32-CAM API Documentation

## Camera Control

### GET /api/camera/status
Get camera status and statistics.

### GET /api/camera/capture
Capture a single frame.

### GET /api/camera/config
Get current camera configuration.

### PUT /api/camera/config
Update camera configuration.
Body: { "jpeg_quality": 12, "brightness": 0, ... }

## Streaming

### POST /api/stream/start
Start video streaming.

### POST /api/stream/stop
Stop video streaming.

### GET /api/stream/status
Get streaming status.

## Settings

### PUT /api/settings/quality
Set JPEG quality (0-63).
Body: { "quality": 12 }

### PUT /api/settings/brightness
Set brightness (-2 to 2).
Body: { "brightness": 0 }

### PUT /api/settings/flip
Set image flip settings.
Body: { "horizontal": false, "vertical": false }
"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get web interface statistics."""
        return {
            "request_count": self.request_count,
            "registered_routes": len(self.routes),
            "api_enabled": self.config.enable_api,
            "ui_enabled": self.config.enable_web_ui,
        }
