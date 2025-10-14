"""
Web Application Firewall (WAF) for protecting external endpoints.
Implements request filtering, rate limiting, and threat detection.
"""

from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re


class ThreatLevel(Enum):
    """Threat severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleType(Enum):
    """WAF rule types."""
    
    RATE_LIMIT = "rate_limit"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    MALFORMED_REQUEST = "malformed_request"
    IP_BLACKLIST = "ip_blacklist"
    GEO_BLOCKING = "geo_blocking"
    CUSTOM = "custom"


@dataclass
class WAFRule:
    """WAF protection rule."""
    
    rule_id: str
    name: str
    rule_type: RuleType
    enabled: bool = True
    action: str = "block"  # block, log, challenge
    priority: int = 100
    pattern: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatDetection:
    """Detected security threat."""
    
    detection_id: str
    rule_id: str
    threat_level: ThreatLevel
    source_ip: str
    endpoint: str
    request_method: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10


class WebApplicationFirewall:
    """
    Web Application Firewall for protecting external endpoints.
    Provides request filtering, rate limiting, and threat detection.
    """
    
    def __init__(self):
        """Initialize WAF."""
        self.rules: Dict[str, WAFRule] = {}
        self.detections: List[ThreatDetection] = []
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        self.request_history: Dict[str, List[datetime]] = {}
        self.blocked_ips: Set[str] = set()
        self.whitelisted_ips: Set[str] = set()
        self.enabled = True
        
        # Initialize default rules
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialize default WAF rules."""
        # SQL Injection protection
        self.add_rule(
            "sql-injection",
            "SQL Injection Protection",
            RuleType.SQL_INJECTION,
            pattern=r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|--|;|')",
            priority=10
        )
        
        # XSS protection
        self.add_rule(
            "xss-protection",
            "Cross-Site Scripting Protection",
            RuleType.XSS,
            pattern=r"(<script|javascript:|onerror=|onload=)",
            priority=10
        )
        
        # Path traversal protection
        self.add_rule(
            "path-traversal",
            "Path Traversal Protection",
            RuleType.PATH_TRAVERSAL,
            pattern=r"(\.\./|\.\.\\|%2e%2e)",
            priority=10
        )
    
    def add_rule(
        self,
        rule_id: str,
        name: str,
        rule_type: RuleType,
        action: str = "block",
        priority: int = 100,
        pattern: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WAFRule:
        """
        Add WAF rule.
        
        Args:
            rule_id: Rule identifier
            name: Rule name
            rule_type: Rule type
            action: Action to take (block, log, challenge)
            priority: Rule priority
            pattern: Regex pattern for matching
            metadata: Additional metadata
            
        Returns:
            WAFRule
        """
        rule = WAFRule(
            rule_id=rule_id,
            name=name,
            rule_type=rule_type,
            action=action,
            priority=priority,
            pattern=pattern,
            metadata=metadata or {}
        )
        self.rules[rule_id] = rule
        return rule
    
    def inspect_request(
        self,
        source_ip: str,
        endpoint: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Inspect incoming request for threats.
        
        Args:
            source_ip: Client IP address
            endpoint: Request endpoint
            method: HTTP method
            headers: Request headers
            body: Request body
            query_params: Query parameters
            
        Returns:
            Inspection result with allowed status and threat details
        """
        if not self.enabled:
            return {"allowed": True, "reason": "WAF disabled"}
        
        # Check whitelist
        if source_ip in self.whitelisted_ips:
            return {"allowed": True, "reason": "IP whitelisted"}
        
        # Check blacklist
        if source_ip in self.blocked_ips:
            self._record_detection(
                "ip-blacklist", ThreatLevel.HIGH, source_ip,
                endpoint, method, "IP is blacklisted"
            )
            return {
                "allowed": False,
                "reason": "IP blacklisted",
                "threat_level": ThreatLevel.HIGH.value
            }
        
        # Check rate limits
        rate_limit_result = self._check_rate_limit(source_ip)
        if not rate_limit_result["allowed"]:
            self._record_detection(
                "rate-limit", ThreatLevel.MEDIUM, source_ip,
                endpoint, method, "Rate limit exceeded"
            )
            return rate_limit_result
        
        # Check rules
        rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority
        )
        
        for rule in rules:
            threat = self._check_rule(
                rule, source_ip, endpoint, method,
                headers or {}, body, query_params or {}
            )
            if threat:
                return threat
        
        return {"allowed": True, "reason": "Request passed all checks"}
    
    def _check_rule(
        self,
        rule: WAFRule,
        source_ip: str,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[str],
        query_params: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Check if request matches rule pattern."""
        if not rule.pattern:
            return None
        
        # Combine all request data for pattern matching
        request_data = f"{endpoint} {method}"
        if body:
            request_data += f" {body}"
        for key, value in query_params.items():
            request_data += f" {key}={value}"
        
        # Check pattern
        if re.search(rule.pattern, request_data, re.IGNORECASE):
            threat_level = self._determine_threat_level(rule.rule_type)
            self._record_detection(
                rule.rule_id, threat_level, source_ip,
                endpoint, method, f"Matched rule: {rule.name}"
            )
            
            if rule.action == "block":
                return {
                    "allowed": False,
                    "reason": f"Blocked by rule: {rule.name}",
                    "rule_id": rule.rule_id,
                    "threat_level": threat_level.value
                }
            elif rule.action == "log":
                # Log but allow
                return None
        
        return None
    
    def _determine_threat_level(self, rule_type: RuleType) -> ThreatLevel:
        """Determine threat level based on rule type."""
        high_severity = [
            RuleType.SQL_INJECTION,
            RuleType.XSS,
            RuleType.PATH_TRAVERSAL
        ]
        if rule_type in high_severity:
            return ThreatLevel.HIGH
        return ThreatLevel.MEDIUM
    
    def _check_rate_limit(self, source_ip: str) -> Dict[str, Any]:
        """Check if IP exceeds rate limits."""
        config = self.rate_limits.get(source_ip)
        if not config:
            # Use default config
            config = RateLimitConfig()
            self.rate_limits[source_ip] = config
        
        now = datetime.utcnow()
        
        # Initialize request history
        if source_ip not in self.request_history:
            self.request_history[source_ip] = []
        
        # Clean old entries
        history = self.request_history[source_ip]
        history = [
            ts for ts in history
            if now - ts < timedelta(days=1)
        ]
        self.request_history[source_ip] = history
        
        # Check limits
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        requests_last_minute = sum(1 for ts in history if ts > minute_ago)
        requests_last_hour = sum(1 for ts in history if ts > hour_ago)
        requests_last_day = sum(1 for ts in history if ts > day_ago)
        
        if requests_last_minute >= config.requests_per_minute:
            return {
                "allowed": False,
                "reason": "Rate limit exceeded (per minute)",
                "limit": config.requests_per_minute,
                "current": requests_last_minute
            }
        
        if requests_last_hour >= config.requests_per_hour:
            return {
                "allowed": False,
                "reason": "Rate limit exceeded (per hour)",
                "limit": config.requests_per_hour,
                "current": requests_last_hour
            }
        
        if requests_last_day >= config.requests_per_day:
            return {
                "allowed": False,
                "reason": "Rate limit exceeded (per day)",
                "limit": config.requests_per_day,
                "current": requests_last_day
            }
        
        # Record request
        history.append(now)
        
        return {"allowed": True}
    
    def _record_detection(
        self,
        rule_id: str,
        threat_level: ThreatLevel,
        source_ip: str,
        endpoint: str,
        method: str,
        details: str
    ):
        """Record threat detection."""
        detection = ThreatDetection(
            detection_id=f"detection-{len(self.detections) + 1}",
            rule_id=rule_id,
            threat_level=threat_level,
            source_ip=source_ip,
            endpoint=endpoint,
            request_method=method,
            timestamp=datetime.utcnow().isoformat(),
            details={"message": details}
        )
        self.detections.append(detection)
    
    def block_ip(self, ip: str):
        """Block IP address."""
        self.blocked_ips.add(ip)
    
    def unblock_ip(self, ip: str):
        """Unblock IP address."""
        self.blocked_ips.discard(ip)
    
    def whitelist_ip(self, ip: str):
        """Add IP to whitelist."""
        self.whitelisted_ips.add(ip)
    
    def remove_from_whitelist(self, ip: str):
        """Remove IP from whitelist."""
        self.whitelisted_ips.discard(ip)
    
    def set_rate_limit(
        self,
        ip: str,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        """
        Set custom rate limit for IP.
        
        Args:
            ip: IP address
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
            requests_per_day: Requests per day limit
        """
        self.rate_limits[ip] = RateLimitConfig(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day
        )
    
    def get_detections(
        self,
        threat_level: Optional[ThreatLevel] = None,
        limit: int = 100
    ) -> List[ThreatDetection]:
        """
        Get threat detections.
        
        Args:
            threat_level: Filter by threat level
            limit: Maximum detections to return
            
        Returns:
            List of ThreatDetection
        """
        detections = self.detections
        
        if threat_level:
            detections = [d for d in detections if d.threat_level == threat_level]
        
        return detections[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get WAF statistics.
        
        Returns:
            Statistics dictionary
        """
        total_rules = len(self.rules)
        enabled_rules = sum(1 for r in self.rules.values() if r.enabled)
        total_detections = len(self.detections)
        
        detections_by_level = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        for detection in self.detections:
            detections_by_level[detection.threat_level.value] += 1
        
        return {
            "enabled": self.enabled,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "total_detections": total_detections,
            "detections_by_level": detections_by_level,
            "blocked_ips": len(self.blocked_ips),
            "whitelisted_ips": len(self.whitelisted_ips)
        }
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate WAF security report.
        
        Returns:
            Security report
        """
        stats = self.get_statistics()
        
        high_threats = [
            d for d in self.detections
            if d.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]
        
        top_attacking_ips = {}
        for detection in self.detections:
            ip = detection.source_ip
            top_attacking_ips[ip] = top_attacking_ips.get(ip, 0) + 1
        
        top_ips = sorted(
            top_attacking_ips.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "summary": stats,
            "high_severity_threats": len(high_threats),
            "top_attacking_ips": [
                {"ip": ip, "attempts": count}
                for ip, count in top_ips
            ],
            "recommendations": self._generate_recommendations(high_threats, top_ips)
        }
    
    def _generate_recommendations(
        self,
        high_threats: List[ThreatDetection],
        top_ips: List[tuple]
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if high_threats:
            recommendations.append(
                f"Review {len(high_threats)} high-severity threats immediately"
            )
        
        if top_ips and top_ips[0][1] > 10:
            recommendations.append(
                f"Consider blocking IP {top_ips[0][0]} with {top_ips[0][1]} attack attempts"
            )
        
        if not high_threats:
            recommendations.append("No high-severity threats detected")
            recommendations.append("Continue monitoring for suspicious activity")
        
        return recommendations
