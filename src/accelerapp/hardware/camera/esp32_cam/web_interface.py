"""
Web interface for ESP32-CAM management.
Provides RESTful API and web-based control panel.
"""

from typing import Dict, Any, Optional
import json


class CameraWebInterface:
    """
    Web-based interface for camera control and monitoring.
    Provides REST API endpoints for camera management.
    """
    
    def __init__(self, camera, port: int = 80):
        """
        Initialize web interface.
        
        Args:
            camera: ESP32Camera instance
            port: HTTP server port
        """
        self.camera = camera
        self.port = port
        self._running = False
        self._endpoints = self._register_endpoints()
    
    def _register_endpoints(self) -> Dict[str, Any]:
        """Register API endpoints."""
        return {
            "/api/status": self.get_status_handler,
            "/api/config": self.get_config_handler,
            "/api/capture": self.capture_handler,
            "/api/stream/start": self.start_stream_handler,
            "/api/stream/stop": self.stop_stream_handler,
            "/api/settings": self.settings_handler,
        }
    
    def start(self) -> bool:
        """
        Start web interface server.
        
        Returns:
            True if server started successfully
        """
        self._running = True
        return True
    
    def stop(self) -> bool:
        """
        Stop web interface server.
        
        Returns:
            True if server stopped successfully
        """
        self._running = False
        return True
    
    def is_running(self) -> bool:
        """Check if web interface is running."""
        return self._running
    
    def get_status_handler(self) -> Dict[str, Any]:
        """Handle GET /api/status request."""
        return {
            "status": "success",
            "data": self.camera.get_status(),
        }
    
    def get_config_handler(self) -> Dict[str, Any]:
        """Handle GET /api/config request."""
        return {
            "status": "success",
            "data": self.camera.get_config(),
        }
    
    def capture_handler(self) -> Dict[str, Any]:
        """Handle POST /api/capture request."""
        result = self.camera.capture_image()
        if result:
            return {
                "status": "success",
                "data": result,
            }
        return {
            "status": "error",
            "message": "Failed to capture image",
        }
    
    def start_stream_handler(self) -> Dict[str, Any]:
        """Handle POST /api/stream/start request."""
        if self.camera.start_streaming():
            return {
                "status": "success",
                "message": "Streaming started",
            }
        return {
            "status": "error",
            "message": "Failed to start streaming",
        }
    
    def stop_stream_handler(self) -> Dict[str, Any]:
        """Handle POST /api/stream/stop request."""
        if self.camera.stop_streaming():
            return {
                "status": "success",
                "message": "Streaming stopped",
            }
        return {
            "status": "error",
            "message": "Failed to stop streaming",
        }
    
    def settings_handler(self, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle GET/POST /api/settings request.
        
        Args:
            settings: Optional settings to update (for POST)
            
        Returns:
            Response dictionary
        """
        if settings:
            # Update settings
            if "resolution" in settings:
                from .core import CameraResolution
                try:
                    res = CameraResolution(settings["resolution"])
                    self.camera.set_resolution(res)
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Invalid resolution",
                    }
            
            if "quality" in settings:
                self.camera.set_quality(settings["quality"])
            
            if "brightness" in settings:
                self.camera.set_brightness(settings["brightness"])
            
            return {
                "status": "success",
                "message": "Settings updated",
                "data": self.camera.get_config(),
            }
        
        # Return current settings
        return {
            "status": "success",
            "data": self.camera.get_config(),
        }
    
    def get_interface_url(self) -> str:
        """
        Get web interface URL.
        
        Returns:
            Interface URL string
        """
        return f"http://localhost:{self.port}"
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API endpoint information.
        
        Returns:
            API info dictionary
        """
        return {
            "base_url": self.get_interface_url(),
            "endpoints": list(self._endpoints.keys()),
            "version": "1.0.0",
            "running": self._running,
        }
