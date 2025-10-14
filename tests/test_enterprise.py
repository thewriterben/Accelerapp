"""
Tests for enterprise features.
"""

import pytest
import tempfile
from pathlib import Path

from accelerapp.enterprise import (
    SSOManager,
    RBACManager,
    TenantManager,
    EnterpriseAuditLogger,
    DataGovernor,
    BIDashboard,
)
from accelerapp.enterprise.governance.data_governor import DataClassification


class TestSSOManager:
    """Test SSO manager."""
    
    def test_register_provider(self):
        """Test registering SSO provider."""
        sso = SSOManager()
        
        provider = sso.register_provider(
            "saml_provider",
            "saml",
            "Corporate SAML",
            {"idp_url": "https://idp.example.com"}
        )
        
        assert provider.provider_id == "saml_provider"
        assert provider.provider_type == "saml"
    
    def test_authenticate_saml(self):
        """Test SAML authentication."""
        sso = SSOManager()
        
        sso.register_provider(
            "saml_provider",
            "saml",
            "Test SAML",
            {}
        )
        
        session = sso.authenticate_saml("saml_provider", "test_response")
        assert session is not None
        assert session.provider_id == "saml_provider"
    
    def test_validate_session(self):
        """Test session validation."""
        sso = SSOManager()
        
        sso.register_provider("test", "saml", "Test", {})
        session = sso.authenticate_saml("test", "response")
        
        assert sso.validate_session(session.session_id) is not None
    
    def test_logout(self):
        """Test logout."""
        sso = SSOManager()
        
        sso.register_provider("test", "saml", "Test", {})
        session = sso.authenticate_saml("test", "response")
        
        assert sso.logout(session.session_id)
        assert sso.validate_session(session.session_id) is None


class TestRBACManager:
    """Test RBAC manager."""
    
    def test_create_permission(self):
        """Test creating permission."""
        rbac = RBACManager()
        
        permission = rbac.create_permission(
            "test_perm",
            "test_resource",
            "read",
            "Test permission"
        )
        
        assert permission.permission_id == "test_perm"
    
    def test_create_role(self):
        """Test creating role."""
        rbac = RBACManager()
        
        role = rbac.create_role(
            "test_role",
            "Test Role",
            "Description",
            ["read_devices"]
        )
        
        assert role.role_id == "test_role"
        assert "read_devices" in role.permissions
    
    def test_assign_role(self):
        """Test assigning role to user."""
        rbac = RBACManager()
        
        assert rbac.assign_role("user1", "developer")
        assert len(rbac.get_user_roles("user1")) == 1
    
    def test_check_permission(self):
        """Test checking permission."""
        rbac = RBACManager()
        
        rbac.assign_role("user1", "developer")
        assert rbac.check_permission("user1", "read_devices")
        assert not rbac.check_permission("user1", "manage_users")
    
    def test_check_resource_access(self):
        """Test checking resource access."""
        rbac = RBACManager()
        
        rbac.assign_role("user1", "developer")
        assert rbac.check_resource_access("user1", "devices", "read")
        assert not rbac.check_resource_access("user1", "users", "manage")


class TestTenantManager:
    """Test tenant manager."""
    
    def test_create_tenant(self):
        """Test creating tenant."""
        tm = TenantManager()
        
        tenant = tm.create_tenant("Test Org")
        assert tenant.name == "Test Org"
        assert tenant.status == "active"
    
    def test_get_tenant(self):
        """Test getting tenant."""
        tm = TenantManager()
        
        tenant = tm.create_tenant("Test Org")
        retrieved = tm.get_tenant(tenant.tenant_id)
        
        assert retrieved is not None
        assert retrieved.tenant_id == tenant.tenant_id
    
    def test_suspend_tenant(self):
        """Test suspending tenant."""
        tm = TenantManager()
        
        tenant = tm.create_tenant("Test Org")
        assert tm.suspend_tenant(tenant.tenant_id)
        
        retrieved = tm.get_tenant(tenant.tenant_id)
        assert retrieved.status == "suspended"
    
    def test_create_resource(self):
        """Test creating tenant resource."""
        tm = TenantManager()
        
        tenant = tm.create_tenant("Test Org")
        resource = tm.create_resource(
            tenant.tenant_id,
            "device",
            {"name": "Test Device"}
        )
        
        assert resource is not None
        assert resource.tenant_id == tenant.tenant_id
    
    def test_get_tenant_usage(self):
        """Test getting tenant usage."""
        tm = TenantManager()
        
        tenant = tm.create_tenant("Test Org")
        tm.create_resource(tenant.tenant_id, "device", {})
        
        usage = tm.get_tenant_usage(tenant.tenant_id)
        assert usage["total_resources"] == 1


class TestEnterpriseAuditLogger:
    """Test enterprise audit logger."""
    
    def test_log_event(self):
        """Test logging audit event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EnterpriseAuditLogger(Path(tmpdir))
            
            event = logger.log_event(
                "tenant1",
                "user1",
                "create",
                "device",
                "device123",
                "success"
            )
            
            assert event.tenant_id == "tenant1"
            assert event.user_id == "user1"
    
    def test_query_events(self):
        """Test querying audit events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EnterpriseAuditLogger(Path(tmpdir))
            
            logger.log_event("tenant1", "user1", "create", "device", "dev1", "success")
            logger.log_event("tenant1", "user2", "update", "device", "dev1", "success")
            
            events = logger.query_events(tenant_id="tenant1")
            assert len(events) == 2
    
    def test_get_user_activity(self):
        """Test getting user activity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EnterpriseAuditLogger(Path(tmpdir))
            
            logger.log_event("tenant1", "user1", "create", "device", "dev1", "success")
            logger.log_event("tenant1", "user1", "update", "device", "dev1", "success")
            
            activity = logger.get_user_activity("user1")
            assert len(activity) == 2


class TestDataGovernor:
    """Test data governor."""
    
    def test_create_policy(self):
        """Test creating data policy."""
        governor = DataGovernor()
        
        policy = governor.create_policy(
            "test_policy",
            "Test Policy",
            DataClassification.CONFIDENTIAL,
            180,
            True,
            False
        )
        
        assert policy.policy_id == "test_policy"
        assert policy.encryption_required
    
    def test_classify_data(self):
        """Test data classification."""
        governor = DataGovernor()
        
        classification = governor.classify_data("user_data", contains_pii=True)
        assert classification == DataClassification.RESTRICTED
    
    def test_check_compliance(self):
        """Test compliance checking."""
        governor = DataGovernor()
        
        result = governor.check_compliance(
            DataClassification.CONFIDENTIAL,
            encryption_enabled=True,
            anonymization_enabled=False
        )
        
        assert result["compliant"]


class TestBIDashboard:
    """Test BI dashboard."""
    
    def test_record_metric(self):
        """Test recording metric."""
        dashboard = BIDashboard()
        
        dashboard.record_metric("api_calls", 100)
        dashboard.record_metric("api_calls", 150)
        
        summary = dashboard.get_metric_summary("api_calls")
        assert summary["count"] == 2
    
    def test_get_dashboard_overview(self):
        """Test getting dashboard overview."""
        dashboard = BIDashboard()
        
        dashboard.record_metric("metric1", 100)
        dashboard.record_metric("metric2", 200)
        
        overview = dashboard.get_dashboard_overview()
        assert overview["total_metrics"] == 2
    
    def test_compare_metrics(self):
        """Test comparing metrics."""
        dashboard = BIDashboard()
        
        dashboard.record_metric("metric1", 100)
        dashboard.record_metric("metric2", 200)
        
        comparison = dashboard.compare_metrics(["metric1", "metric2"])
        assert len(comparison["metrics"]) == 2
