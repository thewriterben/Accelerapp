"""
Multi-Tenancy Manager.
Provides isolated environments for different organizations.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import secrets


@dataclass
class Tenant:
    """Represents a tenant (organization)."""
    
    tenant_id: str
    name: str
    created_at: str
    status: str  # active, suspended, deleted
    config: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantResource:
    """Represents a resource belonging to a tenant."""
    
    resource_id: str
    tenant_id: str
    resource_type: str
    data: Dict[str, Any]
    created_at: str


class TenantManager:
    """
    Manages multi-tenant environments.
    Provides isolation and resource management for different organizations.
    """
    
    def __init__(self):
        """Initialize tenant manager."""
        self.tenants: Dict[str, Tenant] = {}
        self.resources: Dict[str, List[TenantResource]] = {}  # tenant_id -> resources
        self.default_limits = {
            "max_devices": 100,
            "max_users": 50,
            "max_storage_gb": 100,
            "max_api_calls_per_hour": 10000
        }
    
    def create_tenant(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, int]] = None
    ) -> Tenant:
        """
        Create a new tenant.
        
        Args:
            name: Tenant name
            config: Tenant-specific configuration
            resource_limits: Resource limits for this tenant
            
        Returns:
            Created Tenant instance
        """
        tenant_id = secrets.token_urlsafe(16)
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            created_at=datetime.utcnow().isoformat(),
            status="active",
            config=config or {},
            resource_limits=resource_limits or self.default_limits.copy(),
            metadata={}
        )
        
        self.tenants[tenant_id] = tenant
        self.resources[tenant_id] = []
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get a tenant by ID.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant instance or None
        """
        return self.tenants.get(tenant_id)
    
    def update_tenant(
        self,
        tenant_id: str,
        config: Optional[Dict[str, Any]] = None,
        resource_limits: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update tenant configuration.
        
        Args:
            tenant_id: Tenant identifier
            config: Updated configuration
            resource_limits: Updated resource limits
            metadata: Updated metadata
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        if config is not None:
            tenant.config.update(config)
        if resource_limits is not None:
            tenant.resource_limits.update(resource_limits)
        if metadata is not None:
            tenant.metadata.update(metadata)
        
        return True
    
    def suspend_tenant(self, tenant_id: str) -> bool:
        """
        Suspend a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = "suspended"
        return True
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """
        Activate a suspended tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = "active"
        return True
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Soft delete a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            True if successful, False otherwise
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = "deleted"
        return True
    
    def create_resource(
        self,
        tenant_id: str,
        resource_type: str,
        data: Dict[str, Any]
    ) -> Optional[TenantResource]:
        """
        Create a resource for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource
            data: Resource data
            
        Returns:
            TenantResource instance or None
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant or tenant.status != "active":
            return None
        
        # Check resource limits
        if not self._check_resource_limit(tenant_id, resource_type):
            return None
        
        resource_id = secrets.token_urlsafe(16)
        resource = TenantResource(
            resource_id=resource_id,
            tenant_id=tenant_id,
            resource_type=resource_type,
            data=data,
            created_at=datetime.utcnow().isoformat()
        )
        
        if tenant_id not in self.resources:
            self.resources[tenant_id] = []
        
        self.resources[tenant_id].append(resource)
        return resource
    
    def get_tenant_resources(
        self,
        tenant_id: str,
        resource_type: Optional[str] = None
    ) -> List[TenantResource]:
        """
        Get resources belonging to a tenant.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Optional resource type filter
            
        Returns:
            List of TenantResource instances
        """
        resources = self.resources.get(tenant_id, [])
        
        if resource_type:
            resources = [r for r in resources if r.resource_type == resource_type]
        
        return resources
    
    def delete_resource(self, tenant_id: str, resource_id: str) -> bool:
        """
        Delete a tenant resource.
        
        Args:
            tenant_id: Tenant identifier
            resource_id: Resource identifier
            
        Returns:
            True if successful, False otherwise
        """
        if tenant_id not in self.resources:
            return False
        
        resources = self.resources[tenant_id]
        for i, resource in enumerate(resources):
            if resource.resource_id == resource_id:
                del resources[i]
                return True
        
        return False
    
    def _check_resource_limit(self, tenant_id: str, resource_type: str) -> bool:
        """Check if tenant can create more resources of this type."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        # Count existing resources of this type
        current_count = sum(
            1 for r in self.resources.get(tenant_id, [])
            if r.resource_type == resource_type
        )
        
        # Check against limit (if defined)
        limit_key = f"max_{resource_type}"
        if limit_key in tenant.resource_limits:
            return current_count < tenant.resource_limits[limit_key]
        
        return True
    
    def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get resource usage statistics for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Dictionary with usage statistics
        """
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
        
        resources = self.resources.get(tenant_id, [])
        
        # Count resources by type
        resource_counts = {}
        for resource in resources:
            resource_counts[resource.resource_type] = \
                resource_counts.get(resource.resource_type, 0) + 1
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "status": tenant.status,
            "total_resources": len(resources),
            "resources_by_type": resource_counts,
            "limits": tenant.resource_limits
        }
    
    def list_tenants(self, status: Optional[str] = None) -> List[Tenant]:
        """
        List tenants, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of Tenant instances
        """
        tenants = list(self.tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        return tenants
