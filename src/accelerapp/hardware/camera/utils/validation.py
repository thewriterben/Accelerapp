"""
Configuration validation utilities for ESP32-CAM.
"""

from typing import Dict, Any, List


class ConfigValidator:
    """
    Validator for camera configuration.
    """
    
    @staticmethod
    def validate_camera_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate camera configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if "device_id" not in config:
            errors.append("Missing required field: device_id")
        
        # Validate resolution
        if "resolution" in config:
            valid_resolutions = ["320x240", "640x480", "800x600", "1024x768", 
                                "1280x720", "1280x1024", "1600x1200"]
            if config["resolution"] not in valid_resolutions:
                errors.append(f"Invalid resolution: {config['resolution']}")
        
        # Validate JPEG quality
        if "jpeg_quality" in config:
            quality = config["jpeg_quality"]
            if not isinstance(quality, int) or not (0 <= quality <= 63):
                errors.append("JPEG quality must be integer between 0 and 63")
        
        # Validate brightness
        if "brightness" in config:
            brightness = config["brightness"]
            if not isinstance(brightness, int) or not (-2 <= brightness <= 2):
                errors.append("Brightness must be integer between -2 and 2")
        
        # Validate frame rate
        if "frame_rate" in config:
            fps = config["frame_rate"]
            if not isinstance(fps, int) or not (1 <= fps <= 60):
                errors.append("Frame rate must be integer between 1 and 60")
        
        return errors
    
    @staticmethod
    def validate_streaming_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate streaming configuration.
        
        Args:
            config: Streaming configuration
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate protocol
        if "protocol" in config:
            valid_protocols = ["mjpeg", "rtsp", "webrtc", "websocket"]
            if config["protocol"] not in valid_protocols:
                errors.append(f"Invalid protocol: {config['protocol']}")
        
        # Validate port
        if "port" in config:
            port = config["port"]
            if not isinstance(port, int) or not (1 <= port <= 65535):
                errors.append("Port must be integer between 1 and 65535")
        
        # Validate max clients
        if "max_clients" in config:
            clients = config["max_clients"]
            if not isinstance(clients, int) or clients < 1:
                errors.append("max_clients must be positive integer")
        
        return errors
    
    @staticmethod
    def validate_security_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate security configuration.
        
        Args:
            config: Security configuration
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate auth method
        if "auth_method" in config:
            valid_methods = ["none", "basic", "token", "certificate"]
            if config["auth_method"] not in valid_methods:
                errors.append(f"Invalid auth_method: {config['auth_method']}")
        
        # Validate session timeout
        if "session_timeout_minutes" in config:
            timeout = config["session_timeout_minutes"]
            if not isinstance(timeout, int) or timeout < 1:
                errors.append("session_timeout_minutes must be positive integer")
        
        return errors
