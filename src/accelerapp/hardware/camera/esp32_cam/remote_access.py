"""
Remote access capabilities for ESP32-CAM.
Provides secure remote camera access with WebRTC and cloud tunneling.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TunnelType(Enum):
    """Cloud tunnel types."""
    NGROK = "ngrok"
    CLOUDFLARE = "cloudflare"
    CUSTOM = "custom"
    NONE = "none"


class AuthMethod(Enum):
    """Authentication methods."""
    NONE = "none"
    BASIC = "basic"
    TOKEN = "token"
    OAUTH = "oauth"
    CERTIFICATE = "certificate"


@dataclass
class AuthConfig:
    """Authentication configuration."""
    method: AuthMethod = AuthMethod.TOKEN
    
    # Basic auth
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Token auth
    access_token: Optional[str] = None
    token_expiry_hours: int = 24
    
    # OAuth
    oauth_provider: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    
    # Certificate
    cert_path: Optional[str] = None
    key_path: Optional[str] = None
    
    # Access control
    allowed_ips: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60


@dataclass
class TunnelConfig:
    """Cloud tunnel configuration."""
    tunnel_type: TunnelType = TunnelType.NONE
    
    # Ngrok specific
    ngrok_auth_token: Optional[str] = None
    ngrok_region: str = "us"
    
    # Cloudflare specific
    cloudflare_token: Optional[str] = None
    cloudflare_tunnel_id: Optional[str] = None
    
    # Custom tunnel
    custom_endpoint: Optional[str] = None
    custom_port: int = 8080
    
    # Connection settings
    enable_tls: bool = True
    heartbeat_interval: int = 30
    reconnect_attempts: int = 5


class RemoteAccess:
    """
    Remote access manager for ESP32-CAM.
    Provides secure remote connectivity with authentication.
    """
    
    def __init__(
        self,
        camera,
        auth_config: Optional[AuthConfig] = None,
        tunnel_config: Optional[TunnelConfig] = None,
    ):
        """
        Initialize remote access.
        
        Args:
            camera: ESP32Camera instance
            auth_config: Authentication configuration
            tunnel_config: Tunnel configuration
        """
        self.camera = camera
        self.auth_config = auth_config or AuthConfig()
        self.tunnel_config = tunnel_config or TunnelConfig()
        
        self.tunnel_active = False
        self.public_url = None
        self.active_sessions = []
        self.access_log = []
        
        logger.info("RemoteAccess initialized")
    
    def start_tunnel(self) -> Dict[str, Any]:
        """
        Start cloud tunnel for remote access.
        
        Returns:
            Tunnel information including public URL
        """
        try:
            if self.tunnel_config.tunnel_type == TunnelType.NONE:
                logger.info("No tunnel configured")
                return {
                    "status": "disabled",
                    "message": "Tunnel not configured",
                }
            
            logger.info(f"Starting {self.tunnel_config.tunnel_type.value} tunnel...")
            
            # In production, this would start actual tunnel service
            self.public_url = self._generate_public_url()
            self.tunnel_active = True
            
            logger.info(f"Tunnel active at: {self.public_url}")
            
            return {
                "status": "active",
                "tunnel_type": self.tunnel_config.tunnel_type.value,
                "public_url": self.public_url,
                "secure": self.tunnel_config.enable_tls,
            }
            
        except Exception as e:
            logger.error(f"Failed to start tunnel: {e}")
            return {
                "status": "error",
                "message": str(e),
            }
    
    def stop_tunnel(self) -> bool:
        """Stop cloud tunnel."""
        if self.tunnel_active:
            logger.info("Stopping tunnel...")
            self.tunnel_active = False
            self.public_url = None
            return True
        
        return False
    
    def _generate_public_url(self) -> str:
        """Generate public URL based on tunnel type."""
        if self.tunnel_config.tunnel_type == TunnelType.NGROK:
            return f"https://random-id.ngrok.io"
        elif self.tunnel_config.tunnel_type == TunnelType.CLOUDFLARE:
            return f"https://random-id.trycloudflare.com"
        elif self.tunnel_config.tunnel_type == TunnelType.CUSTOM:
            return self.tunnel_config.custom_endpoint or "https://custom-tunnel.example.com"
        
        return "http://localhost:8080"
    
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate access request.
        
        Args:
            credentials: Authentication credentials
        
        Returns:
            Authentication result
        """
        try:
            if self.auth_config.method == AuthMethod.NONE:
                return {
                    "authenticated": True,
                    "method": "none",
                }
            
            elif self.auth_config.method == AuthMethod.BASIC:
                username = credentials.get("username")
                password = credentials.get("password")
                
                if username == self.auth_config.username and password == self.auth_config.password:
                    return {
                        "authenticated": True,
                        "method": "basic",
                        "username": username,
                    }
            
            elif self.auth_config.method == AuthMethod.TOKEN:
                token = credentials.get("token")
                
                if token == self.auth_config.access_token:
                    return {
                        "authenticated": True,
                        "method": "token",
                    }
            
            # Authentication failed
            self._log_access_attempt(credentials, False)
            
            return {
                "authenticated": False,
                "message": "Invalid credentials",
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "authenticated": False,
                "message": "Authentication error",
            }
    
    def create_session(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """
        Create authenticated session.
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
        
        Returns:
            Session information
        """
        # Check IP whitelist
        if self.auth_config.allowed_ips and ip_address not in self.auth_config.allowed_ips:
            logger.warning(f"IP not allowed: {ip_address}")
            return {
                "status": "denied",
                "message": "IP not allowed",
            }
        
        session = {
            "session_id": f"sess_{len(self.active_sessions)}",
            "user_id": user_id,
            "ip_address": ip_address,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }
        
        self.active_sessions.append(session)
        self._log_access_attempt({"user_id": user_id, "ip": ip_address}, True)
        
        logger.info(f"Session created: {session['session_id']}")
        
        return {
            "status": "success",
            "session": session,
        }
    
    def end_session(self, session_id: str) -> bool:
        """End an active session."""
        for i, session in enumerate(self.active_sessions):
            if session["session_id"] == session_id:
                self.active_sessions.pop(i)
                logger.info(f"Session ended: {session_id}")
                return True
        
        return False
    
    def _log_access_attempt(self, credentials: Dict[str, Any], success: bool):
        """Log access attempt."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "credentials": {k: v for k, v in credentials.items() if k != "password"},
        }
        
        self.access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get remote access status."""
        return {
            "tunnel_active": self.tunnel_active,
            "public_url": self.public_url,
            "active_sessions": len(self.active_sessions),
            "auth_method": self.auth_config.method.value,
            "tunnel_type": self.tunnel_config.tunnel_type.value,
        }
    
    def get_access_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent access log entries."""
        return self.access_log[-limit:] if self.access_log else []
    
    def generate_remote_access_code(self) -> Dict[str, str]:
        """Generate firmware code for remote access."""
        header = """
// Remote Access for ESP32-CAM
#ifndef REMOTE_ACCESS_H
#define REMOTE_ACCESS_H

#include <WiFiClient.h>

enum AuthMethod {
    AUTH_NONE,
    AUTH_BASIC,
    AUTH_TOKEN
};

class RemoteAccess {
public:
    bool init(AuthMethod method);
    bool startTunnel();
    bool authenticate(const char* credentials);
    void handleClient(WiFiClient& client);
    
private:
    AuthMethod authMethod;
    bool tunnelActive;
    char publicUrl[128];
};

#endif
"""
        
        implementation = f"""
// Remote Access Implementation
#include "remote_access.h"

bool RemoteAccess::init(AuthMethod method) {{
    authMethod = method;
    tunnelActive = false;
    return true;
}}

bool RemoteAccess::startTunnel() {{
    // Initialize tunnel service
    // This would integrate with ngrok, cloudflare, or custom tunnel
    
    tunnelActive = true;
    strcpy(publicUrl, "https://tunnel.example.com");
    
    return true;
}}

bool RemoteAccess::authenticate(const char* credentials) {{
    if (authMethod == AUTH_NONE) {{
        return true;
    }}
    
    // Validate credentials based on auth method
    // For TOKEN: check against stored token
    // For BASIC: parse and validate username/password
    
    return false;
}}

void RemoteAccess::handleClient(WiFiClient& client) {{
    // Handle authenticated client requests
    // Forward to camera stream or control endpoints
}}
"""
        
        return {
            "remote_access.h": header,
            "remote_access.cpp": implementation,
        }
    
    def generate_webrtc_config(self) -> Dict[str, Any]:
        """Generate WebRTC configuration."""
        return {
            "ice_servers": self.tunnel_config.cloudflare_token or [
                {"urls": "stun:stun.l.google.com:19302"},
            ],
            "enable_tls": self.tunnel_config.enable_tls,
            "signaling_url": f"{self.public_url}/ws" if self.public_url else None,
        }
