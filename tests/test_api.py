"""
Tests for API and rate limiting functionality.
"""

import pytest
import time
from accelerapp.api import RateLimiter, APIKeyManager
from accelerapp.api.rate_limiter import RateLimitRule


def test_rate_limiter_initialization():
    """Test rate limiter initialization."""
    limiter = RateLimiter()
    assert limiter.default_rule is not None
    assert limiter.default_rule.max_requests == 100


def test_rate_limiter_custom_rule():
    """Test rate limiter with custom rule."""
    rule = RateLimitRule(max_requests=10, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    assert limiter.default_rule.max_requests == 10
    assert limiter.default_rule.time_window == 60


def test_rate_limit_check_within_limit():
    """Test rate limit check within limits."""
    rule = RateLimitRule(max_requests=5, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    # First 5 requests should be allowed
    for i in range(5):
        allowed, info = limiter.check_limit("test_client")
        assert allowed is True
        assert info['allowed'] is True


def test_rate_limit_check_exceeded():
    """Test rate limit check when exceeded."""
    rule = RateLimitRule(max_requests=3, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    # First 3 requests allowed
    for i in range(3):
        allowed, _ = limiter.check_limit("test_client")
        assert allowed is True
    
    # 4th request should be denied
    allowed, info = limiter.check_limit("test_client")
    assert allowed is False
    assert info['allowed'] is False
    assert 'retry_after' in info


def test_rate_limit_reset():
    """Test rate limit reset."""
    rule = RateLimitRule(max_requests=2, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    # Use up limit
    limiter.check_limit("test_client")
    limiter.check_limit("test_client")
    
    # Reset
    limiter.reset_client("test_client")
    
    # Should be allowed again
    allowed, _ = limiter.check_limit("test_client")
    assert allowed is True


def test_rate_limit_multiple_clients():
    """Test rate limiting with multiple clients."""
    rule = RateLimitRule(max_requests=2, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    # Client 1
    limiter.check_limit("client1")
    limiter.check_limit("client1")
    allowed, _ = limiter.check_limit("client1")
    assert allowed is False
    
    # Client 2 should still be allowed
    allowed, _ = limiter.check_limit("client2")
    assert allowed is True


def test_rate_limit_per_client_rules():
    """Test per-client rate limit rules."""
    limiter = RateLimiter()
    
    # Set custom rule for specific client
    custom_rule = RateLimitRule(max_requests=2, time_window=60)
    limiter.set_rule("vip_client", custom_rule)
    
    # VIP client has lower limit
    limiter.check_limit("vip_client")
    limiter.check_limit("vip_client")
    allowed, _ = limiter.check_limit("vip_client")
    assert allowed is False
    
    # Regular client uses default
    for i in range(10):
        allowed, _ = limiter.check_limit("regular_client")
        if not allowed:
            break
    # Should allow more than 2 requests


def test_rate_limit_token_consumption():
    """Test consuming multiple tokens per request."""
    rule = RateLimitRule(max_requests=10, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    # Consume 5 tokens
    allowed, info = limiter.check_limit("test_client", tokens=5)
    assert allowed is True
    assert info['remaining'] == 5
    
    # Consume 5 more
    allowed, info = limiter.check_limit("test_client", tokens=5)
    assert allowed is True
    assert info['remaining'] == 0
    
    # Should be denied
    allowed, _ = limiter.check_limit("test_client", tokens=1)
    assert allowed is False


def test_rate_limit_get_client_info():
    """Test getting client info."""
    rule = RateLimitRule(max_requests=5, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    limiter.check_limit("test_client")
    limiter.check_limit("test_client")
    
    info = limiter.get_client_info("test_client")
    assert info['client_id'] == "test_client"
    assert info['used'] == 2
    assert info['remaining'] == 3
    assert info['limit'] == 5


def test_api_key_manager_initialization():
    """Test API key manager initialization."""
    manager = APIKeyManager()
    assert manager.keys is not None


def test_api_key_generation():
    """Test API key generation."""
    manager = APIKeyManager()
    
    key = manager.generate_key("test_client", permissions=['read', 'write'])
    
    assert key.startswith("acc_")
    assert len(key) > 10


def test_api_key_validation():
    """Test API key validation."""
    manager = APIKeyManager()
    
    key = manager.generate_key("test_client")
    
    # Valid key
    valid, client_id = manager.validate_key(key)
    assert valid is True
    assert client_id == "test_client"
    
    # Invalid key
    valid, client_id = manager.validate_key("invalid_key")
    assert valid is False
    assert client_id is None


def test_api_key_revocation():
    """Test API key revocation."""
    manager = APIKeyManager()
    
    key = manager.generate_key("test_client")
    
    # Key is valid
    valid, _ = manager.validate_key(key)
    assert valid is True
    
    # Revoke key
    revoked = manager.revoke_key(key)
    assert revoked is True
    
    # Key is no longer valid
    valid, _ = manager.validate_key(key)
    assert valid is False


def test_api_key_usage_tracking():
    """Test API key usage tracking."""
    manager = APIKeyManager()
    
    key = manager.generate_key("test_client")
    
    # Use key multiple times
    for i in range(5):
        manager.validate_key(key)
    
    # Check usage count
    info = manager.get_key_info(key)
    assert info['usage_count'] == 5
    assert info['last_used'] is not None


def test_api_key_permissions():
    """Test API key permissions."""
    manager = APIKeyManager()
    
    key = manager.generate_key("test_client", permissions=['read'])
    
    info = manager.get_key_info(key)
    assert 'read' in info['permissions']
    assert 'write' not in info['permissions']


def test_api_key_list():
    """Test listing API keys."""
    manager = APIKeyManager()
    
    key1 = manager.generate_key("client1")
    key2 = manager.generate_key("client2")
    key3 = manager.generate_key("client1")  # Another key for client1
    
    # List all keys
    all_keys = manager.list_keys()
    assert len(all_keys) == 3
    
    # List keys for specific client
    client1_keys = manager.list_keys(client_id="client1")
    assert len(client1_keys) == 2


def test_rate_limit_cleanup():
    """Test cleanup of old client data."""
    rule = RateLimitRule(max_requests=5, time_window=1)  # 1 second window
    limiter = RateLimiter(default_rule=rule)
    
    limiter.check_limit("old_client")
    limiter.check_limit("new_client")
    
    # Wait for old client to expire
    time.sleep(2)
    
    # Make new request from new client
    limiter.check_limit("new_client")
    
    # Cleanup old clients
    limiter.cleanup_old_clients(max_age_seconds=1)
    
    # Old client should be removed
    assert "old_client" not in limiter.client_buckets or len(limiter.client_buckets["old_client"]) == 0
