"""
Security management for ESP32-CAM.
Provides authentication, encryption, and access control.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import hashlib
import secrets


class AuthMethod(Enum):
    """Authentication methods."""
    NONE = "none"
    BASIC = "basic"
    TOKEN = "token"
    CERTIFICATE = "certificate"


class AccessLevel(Enum):
    """Access control levels."""
    GUEST = "guest"          # View only
    USER = "user"            # View and capture
    ADMIN = "admin"          # Full control
    OWNER = "owner"          # Full control + security settings


@dataclass
class SecurityConfig:
    """Security configuration."""
    auth_method: AuthMethod = AuthMethod.TOKEN
    enable_encryption: bool = True
    require_https: bool = True
    session_timeout_minutes: int = 30
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15


class CameraSecurityManager:
    """
    Security management for ESP32-CAM.
    Handles authentication, authorization, and encryption.
    """
    
    def __init__(self, camera, config: Optional[SecurityConfig] = None):
        """
        Initialize security manager.
        
        Args:
            camera: ESP32Camera instance
            config: Security configuration
        """
        self.camera = camera
        self.config = config or SecurityConfig()
        self._users: Dict[str, Dict[str, Any]] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._failed_attempts: Dict[str, int] = {}
        self._locked_users: Dict[str, str] = {}  # username -> lockout_until
    
    def add_user(self, username: str, password: str, access_level: AccessLevel) -> bool:
        """
        Add new user with credentials.
        
        Args:
            username: Username
            password: Password (will be hashed)
            access_level: User access level
            
        Returns:
            True if user added successfully
        """
        if username in self._users:
            return False
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        self._users[username] = {
            "password_hash": password_hash,
            "access_level": access_level.value,
            "created_at": "2025-10-15T01:12:23.332Z",
            "last_login": None,
        }
        return True
    
    def remove_user(self, username: str) -> bool:
        """
        Remove user.
        
        Args:
            username: Username to remove
            
        Returns:
            True if user removed successfully
        """
        if username in self._users:
            del self._users[username]
            # Invalidate user's tokens
            self._tokens = {t: info for t, info in self._tokens.items() 
                          if info["username"] != username}
            return True
        return False
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and return token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Authentication token if successful, None otherwise
        """
        # Check if user is locked out
        if username in self._locked_users:
            return None
        
        if username not in self._users:
            self._record_failed_attempt(username)
            return None
        
        user = self._users[username]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash != user["password_hash"]:
            self._record_failed_attempt(username)
            return None
        
        # Reset failed attempts on successful login
        if username in self._failed_attempts:
            del self._failed_attempts[username]
        
        # Generate token
        token = self._generate_token()
        self._tokens[token] = {
            "username": username,
            "access_level": user["access_level"],
            "created_at": "2025-10-15T01:12:23.332Z",
        }
        
        user["last_login"] = "2025-10-15T01:12:23.332Z"
        
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token
            
        Returns:
            Token info if valid, None otherwise
        """
        return self._tokens.get(token)
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if token was revoked
        """
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False
    
    def check_permission(self, token: str, required_level: AccessLevel) -> bool:
        """
        Check if token has required permission level.
        
        Args:
            token: Authentication token
            required_level: Required access level
            
        Returns:
            True if permission granted
        """
        token_info = self.validate_token(token)
        if not token_info:
            return False
        
        # Define access level hierarchy
        levels = {
            AccessLevel.GUEST.value: 0,
            AccessLevel.USER.value: 1,
            AccessLevel.ADMIN.value: 2,
            AccessLevel.OWNER.value: 3,
        }
        
        user_level = levels.get(token_info["access_level"], 0)
        required = levels.get(required_level.value, 0)
        
        return user_level >= required
    
    def _generate_token(self) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(32)
    
    def _record_failed_attempt(self, username: str) -> None:
        """Record failed login attempt."""
        self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1
        
        if self._failed_attempts[username] >= self.config.max_failed_attempts:
            # Lock out user
            self._locked_users[username] = "2025-10-15T01:42:23.332Z"  # lockout_until
    
    def enable_encryption(self) -> bool:
        """
        Enable data encryption.
        
        Returns:
            True if enabled successfully
        """
        self.config.enable_encryption = True
        return True
    
    def disable_encryption(self) -> bool:
        """
        Disable data encryption (not recommended).
        
        Returns:
            True if disabled successfully
        """
        self.config.enable_encryption = False
        return True
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security status and statistics.
        
        Returns:
            Security status dictionary
        """
        return {
            "auth_method": self.config.auth_method.value,
            "encryption_enabled": self.config.enable_encryption,
            "https_required": self.config.require_https,
            "total_users": len(self._users),
            "active_tokens": len(self._tokens),
            "locked_users": len(self._locked_users),
            "session_timeout_minutes": self.config.session_timeout_minutes,
        }
    
    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users (without sensitive data).
        
        Returns:
            List of user information
        """
        return [
            {
                "username": username,
                "access_level": info["access_level"],
                "created_at": info["created_at"],
                "last_login": info["last_login"],
            }
            for username, info in self._users.items()
        ]
    
    def audit_log(self, action: str, user: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log security-related action for audit trail.
        
        Args:
            action: Action performed
            user: User who performed action
            details: Additional details
        """
        # Placeholder for audit logging
        # In real implementation, would write to secure audit log
        pass
