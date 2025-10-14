"""
Access control system for securing air-gapped deployments.
"""

from typing import Dict, Set, List
from enum import Enum


class Permission(Enum):
    """Permission levels."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


class AccessControl:
    """Manages user permissions and access control."""

    def __init__(self):
        """Initialize access control."""
        self.users: Dict[str, Set[Permission]] = {}
        self.roles: Dict[str, Set[Permission]] = {
            "viewer": {Permission.READ},
            "developer": {Permission.READ, Permission.WRITE},
            "admin": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.ADMIN},
        }

    def add_user(self, username: str, role: str = "viewer") -> None:
        """Add user with role."""
        if role in self.roles:
            self.users[username] = self.roles[role].copy()

    def has_permission(self, username: str, permission: Permission) -> bool:
        """Check if user has permission."""
        return permission in self.users.get(username, set())

    def grant_permission(self, username: str, permission: Permission) -> None:
        """Grant permission to user."""
        if username in self.users:
            self.users[username].add(permission)
