"""
Authentication and authorization for cloud services.
"""

from typing import Dict, Any, Optional, List
import hashlib
import secrets
from datetime import datetime, timedelta


class AuthenticationManager:
    """
    Manages authentication and authorization for cloud services.
    Provides token-based authentication system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication manager.
        
        Args:
            config: Authentication configuration
        """
        self.config = config or {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.token_expiry_hours = self.config.get('token_expiry_hours', 24)
    
    def create_user(
        self,
        username: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> bool:
        """
        Create a new user.
        
        Args:
            username: User identifier
            password: User password
            roles: List of user roles
            
        Returns:
            True if user created successfully
        """
        if username in self.users:
            return False
        
        password_hash = self._hash_password(password)
        
        self.users[username] = {
            'username': username,
            'password_hash': password_hash,
            'roles': roles or ['user'],
            'created_at': datetime.utcnow().isoformat(),
            'active': True,
        }
        
        return True
    
    def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[str]:
        """
        Authenticate a user and return access token.
        
        Args:
            username: User identifier
            password: User password
            
        Returns:
            Access token if authentication successful, None otherwise
        """
        user = self.users.get(username)
        
        if not user or not user['active']:
            return None
        
        password_hash = self._hash_password(password)
        if password_hash != user['password_hash']:
            return None
        
        # Generate token
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        
        self.tokens[token] = {
            'username': username,
            'roles': user['roles'],
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expiry.isoformat(),
        }
        
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an access token.
        
        Args:
            token: Access token
            
        Returns:
            Token info if valid, None otherwise
        """
        token_info = self.tokens.get(token)
        
        if not token_info:
            return None
        
        expiry = datetime.fromisoformat(token_info['expires_at'])
        if datetime.utcnow() > expiry:
            # Token expired
            del self.tokens[token]
            return None
        
        return token_info
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            token: Access token to revoke
            
        Returns:
            True if revoked successfully
        """
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def check_permission(
        self,
        token: str,
        required_role: str
    ) -> bool:
        """
        Check if token has required permission.
        
        Args:
            token: Access token
            required_role: Required role
            
        Returns:
            True if permission granted
        """
        token_info = self.validate_token(token)
        
        if not token_info:
            return False
        
        return required_role in token_info['roles']
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def deactivate_user(self, username: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            username: User identifier
            
        Returns:
            True if deactivated successfully
        """
        if username in self.users:
            self.users[username]['active'] = False
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information (without password hash).
        
        Args:
            username: User identifier
            
        Returns:
            User info dictionary or None
        """
        user = self.users.get(username)
        if user:
            return {
                'username': user['username'],
                'roles': user['roles'],
                'created_at': user['created_at'],
                'active': user['active'],
            }
        return None
