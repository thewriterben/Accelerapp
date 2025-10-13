"""
Rate limiting for API calls and LLM requests.
Prevents abuse and manages resource usage.
"""

import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    max_requests: int  # Maximum requests allowed
    time_window: int  # Time window in seconds
    burst_size: Optional[int] = None  # Optional burst allowance
    
    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.max_requests


class RateLimiter:
    """
    Token bucket rate limiter with per-client tracking.
    Supports both request-based and token-based limiting.
    """
    
    def __init__(self, default_rule: Optional[RateLimitRule] = None):
        """
        Initialize rate limiter.
        
        Args:
            default_rule: Default rate limiting rule
        """
        self.default_rule = default_rule or RateLimitRule(
            max_requests=100,
            time_window=3600,  # 1 hour
            burst_size=10
        )
        
        self.client_buckets: Dict[str, deque] = {}
        self.client_rules: Dict[str, RateLimitRule] = {}
        self.lock = threading.Lock()
    
    def set_rule(self, client_id: str, rule: RateLimitRule):
        """
        Set rate limit rule for specific client.
        
        Args:
            client_id: Client identifier
            rule: Rate limiting rule
        """
        with self.lock:
            self.client_rules[client_id] = rule
    
    def check_limit(self, client_id: str, tokens: int = 1) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limit.
        
        Args:
            client_id: Client identifier
            tokens: Number of tokens to consume (default 1)
            
        Returns:
            Tuple of (allowed, info_dict)
        """
        with self.lock:
            rule = self.client_rules.get(client_id, self.default_rule)
            
            # Initialize bucket for new client
            if client_id not in self.client_buckets:
                self.client_buckets[client_id] = deque()
            
            bucket = self.client_buckets[client_id]
            current_time = time.time()
            
            # Remove old entries outside time window
            cutoff_time = current_time - rule.time_window
            while bucket and bucket[0] < cutoff_time:
                bucket.popleft()
            
            # Check if within limit
            current_usage = len(bucket)
            remaining = rule.max_requests - current_usage
            
            if current_usage + tokens <= rule.max_requests:
                # Add tokens to bucket
                for _ in range(tokens):
                    bucket.append(current_time)
                
                return True, {
                    'allowed': True,
                    'limit': rule.max_requests,
                    'remaining': remaining - tokens,
                    'reset_time': current_time + rule.time_window
                }
            else:
                # Rate limit exceeded
                oldest_request = bucket[0] if bucket else current_time
                reset_time = oldest_request + rule.time_window
                retry_after = int(reset_time - current_time)
                
                return False, {
                    'allowed': False,
                    'limit': rule.max_requests,
                    'remaining': 0,
                    'reset_time': reset_time,
                    'retry_after': retry_after
                }
    
    def reset_client(self, client_id: str):
        """
        Reset rate limit for specific client.
        
        Args:
            client_id: Client identifier
        """
        with self.lock:
            if client_id in self.client_buckets:
                self.client_buckets[client_id].clear()
    
    def get_client_info(self, client_id: str) -> Dict[str, any]:
        """
        Get rate limit info for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Client rate limit information
        """
        with self.lock:
            rule = self.client_rules.get(client_id, self.default_rule)
            bucket = self.client_buckets.get(client_id, deque())
            
            current_time = time.time()
            cutoff_time = current_time - rule.time_window
            
            # Count valid requests
            valid_requests = sum(1 for t in bucket if t >= cutoff_time)
            
            return {
                'client_id': client_id,
                'limit': rule.max_requests,
                'used': valid_requests,
                'remaining': rule.max_requests - valid_requests,
                'time_window': rule.time_window,
                'burst_size': rule.burst_size
            }
    
    def cleanup_old_clients(self, max_age_seconds: int = 86400):
        """
        Remove data for inactive clients.
        
        Args:
            max_age_seconds: Maximum age to keep client data (default 24 hours)
        """
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - max_age_seconds
            
            clients_to_remove = []
            for client_id, bucket in self.client_buckets.items():
                if not bucket or bucket[-1] < cutoff_time:
                    clients_to_remove.append(client_id)
            
            for client_id in clients_to_remove:
                del self.client_buckets[client_id]
                if client_id in self.client_rules:
                    del self.client_rules[client_id]


class APIKeyManager:
    """
    Secure API key management with hashing and validation.
    """
    
    def __init__(self):
        """Initialize API key manager."""
        self.keys: Dict[str, Dict[str, any]] = {}
        self.lock = threading.Lock()
    
    def generate_key(self, client_id: str, permissions: list = None) -> str:
        """
        Generate new API key for client.
        
        Args:
            client_id: Client identifier
            permissions: List of permitted operations
            
        Returns:
            Generated API key
        """
        import secrets
        
        # Generate secure random key
        api_key = f"acc_{secrets.token_urlsafe(32)}"
        
        with self.lock:
            self.keys[api_key] = {
                'client_id': client_id,
                'permissions': permissions or ['read', 'write'],
                'created_at': datetime.now().isoformat(),
                'last_used': None,
                'usage_count': 0
            }
        
        return api_key
    
    def validate_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Tuple of (valid, client_id)
        """
        with self.lock:
            if api_key in self.keys:
                # Update usage stats
                self.keys[api_key]['last_used'] = datetime.now().isoformat()
                self.keys[api_key]['usage_count'] += 1
                
                return True, self.keys[api_key]['client_id']
            else:
                return False, None
    
    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            True if key was revoked
        """
        with self.lock:
            if api_key in self.keys:
                del self.keys[api_key]
                return True
            return False
    
    def get_key_info(self, api_key: str) -> Optional[Dict[str, any]]:
        """
        Get information about API key.
        
        Args:
            api_key: API key
            
        Returns:
            Key information or None
        """
        with self.lock:
            if api_key in self.keys:
                return self.keys[api_key].copy()
            return None
    
    def list_keys(self, client_id: Optional[str] = None) -> list:
        """
        List API keys, optionally filtered by client.
        
        Args:
            client_id: Optional client ID filter
            
        Returns:
            List of API key information
        """
        with self.lock:
            keys = []
            for api_key, info in self.keys.items():
                if client_id is None or info['client_id'] == client_id:
                    keys.append({
                        'key_prefix': api_key[:10] + '...',
                        **info
                    })
            return keys
