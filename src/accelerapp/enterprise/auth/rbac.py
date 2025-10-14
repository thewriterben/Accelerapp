"""
Role-Based Access Control (RBAC) Manager.
Implements fine-grained permissions and role management.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass


@dataclass
class Permission:
    """Represents a permission."""
    
    permission_id: str
    resource: str
    action: str  # create, read, update, delete, execute
    description: str


@dataclass
class Role:
    """Represents a role with permissions."""
    
    role_id: str
    name: str
    description: str
    permissions: Set[str]  # Set of permission IDs
    inherits_from: Optional[List[str]] = None  # Parent roles


class RBACManager:
    """
    Manages Role-Based Access Control.
    Provides fine-grained permission management and role hierarchy.
    """
    
    def __init__(self):
        """Initialize RBAC manager."""
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}  # user_id -> set of role_ids
        self._initialize_default_permissions()
        self._initialize_default_roles()
    
    def _initialize_default_permissions(self) -> None:
        """Initialize default permissions."""
        default_permissions = [
            ("read_devices", "devices", "read", "Read device information"),
            ("write_devices", "devices", "write", "Create/update devices"),
            ("delete_devices", "devices", "delete", "Delete devices"),
            ("execute_generation", "generation", "execute", "Execute code generation"),
            ("read_logs", "logs", "read", "Read system logs"),
            ("manage_users", "users", "manage", "Manage user accounts"),
            ("manage_roles", "roles", "manage", "Manage roles and permissions"),
            ("read_analytics", "analytics", "read", "View analytics dashboards"),
            ("manage_settings", "settings", "manage", "Manage system settings"),
        ]
        
        for perm_id, resource, action, desc in default_permissions:
            self.create_permission(perm_id, resource, action, desc)
    
    def _initialize_default_roles(self) -> None:
        """Initialize default roles."""
        # Admin role - full access
        self.create_role(
            "admin",
            "Administrator",
            "Full system access",
            list(self.permissions.keys())
        )
        
        # Developer role - code generation and device management
        self.create_role(
            "developer",
            "Developer",
            "Code generation and device management",
            ["read_devices", "write_devices", "execute_generation", "read_logs"]
        )
        
        # Viewer role - read-only access
        self.create_role(
            "viewer",
            "Viewer",
            "Read-only access",
            ["read_devices", "read_logs", "read_analytics"]
        )
    
    def create_permission(
        self,
        permission_id: str,
        resource: str,
        action: str,
        description: str
    ) -> Permission:
        """
        Create a new permission.
        
        Args:
            permission_id: Unique permission identifier
            resource: Resource type
            action: Action allowed on resource
            description: Permission description
            
        Returns:
            Created Permission instance
        """
        permission = Permission(
            permission_id=permission_id,
            resource=resource,
            action=action,
            description=description
        )
        
        self.permissions[permission_id] = permission
        return permission
    
    def create_role(
        self,
        role_id: str,
        name: str,
        description: str,
        permissions: List[str],
        inherits_from: Optional[List[str]] = None
    ) -> Role:
        """
        Create a new role.
        
        Args:
            role_id: Unique role identifier
            name: Role name
            description: Role description
            permissions: List of permission IDs
            inherits_from: Optional parent role IDs
            
        Returns:
            Created Role instance
        """
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=set(permissions),
            inherits_from=inherits_from or []
        )
        
        self.roles[role_id] = role
        return role
    
    def assign_role(self, user_id: str, role_id: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            True if successful, False otherwise
        """
        if role_id not in self.roles:
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_id)
        return True
    
    def revoke_role(self, user_id: str, role_id: str) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            True if successful, False otherwise
        """
        if user_id in self.user_roles and role_id in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_id)
            return True
        return False
    
    def check_permission(
        self,
        user_id: str,
        permission_id: str
    ) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User identifier
            permission_id: Permission identifier
            
        Returns:
            True if user has permission, False otherwise
        """
        if user_id not in self.user_roles:
            return False
        
        # Get all permissions from user's roles (including inherited)
        user_permissions = self._get_user_permissions(user_id)
        return permission_id in user_permissions
    
    def check_resource_access(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user can perform action on resource.
        
        Args:
            user_id: User identifier
            resource: Resource type
            action: Action to perform
            
        Returns:
            True if user has access, False otherwise
        """
        user_permissions = self._get_user_permissions(user_id)
        
        # Find matching permissions
        for perm_id in user_permissions:
            permission = self.permissions.get(perm_id)
            if permission and permission.resource == resource and permission.action == action:
                return True
        
        return False
    
    def _get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user including inherited."""
        if user_id not in self.user_roles:
            return set()
        
        all_permissions = set()
        
        for role_id in self.user_roles[user_id]:
            role = self.roles.get(role_id)
            if role:
                all_permissions.update(role.permissions)
                
                # Add inherited permissions
                if role.inherits_from:
                    for parent_role_id in role.inherits_from:
                        parent_role = self.roles.get(parent_role_id)
                        if parent_role:
                            all_permissions.update(parent_role.permissions)
        
        return all_permissions
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of Role instances
        """
        if user_id not in self.user_roles:
            return []
        
        return [
            self.roles[role_id]
            for role_id in self.user_roles[user_id]
            if role_id in self.roles
        ]
    
    def list_permissions(self, resource: Optional[str] = None) -> List[Permission]:
        """
        List permissions, optionally filtered by resource.
        
        Args:
            resource: Optional resource filter
            
        Returns:
            List of Permission instances
        """
        permissions = list(self.permissions.values())
        if resource:
            permissions = [p for p in permissions if p.resource == resource]
        return permissions
    
    def list_roles(self) -> List[Role]:
        """
        List all roles.
        
        Returns:
            List of Role instances
        """
        return list(self.roles.values())
