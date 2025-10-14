# Phase 5: Security & Compliance Features

## Quick Reference Guide

This document provides a quick reference for using Phase 5 security and compliance features.

---

## Table of Contents

1. [Network Policy Enforcement](#network-policy-enforcement)
2. [Web Application Firewall](#web-application-firewall)
3. [Backup & Recovery](#backup--recovery)
4. [Security Auditing](#security-auditing)
5. [Orchestrator](#orchestrator)

---

## Network Policy Enforcement

### Basic Usage

```python
from accelerapp.production.security import (
    NetworkPolicyEnforcer,
    PolicyType,
    PolicyAction
)

# Initialize
enforcer = NetworkPolicyEnforcer()

# Create policy
policy = enforcer.create_policy(
    "my-policy",
    "My Policy",
    "default",
    PolicyType.INGRESS
)

# Add rule
enforcer.add_rule(
    "my-policy",
    "allow-https",
    action=PolicyAction.ALLOW,
    ports=[443],
    protocols=["https"]
)

# Check connection
result = enforcer.check_connection(
    "app-1", "app-2", 443, "https"
)
```

### Key Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `create_policy()` | Create network policy | policy_id, name, namespace, type |
| `add_rule()` | Add rule to policy | policy_id, rule_id, action, ports, protocols |
| `check_connection()` | Check if allowed | source, dest, port, protocol |
| `enable_policy()` | Enable policy | policy_id |
| `disable_policy()` | Disable policy | policy_id |
| `get_statistics()` | Get stats | - |
| `export_policy()` | Export to K8s | policy_id |

### Policy Actions

- `PolicyAction.ALLOW` - Allow connection
- `PolicyAction.DENY` - Deny connection
- `PolicyAction.LOG` - Log but allow

### Policy Types

- `PolicyType.INGRESS` - Incoming traffic
- `PolicyType.EGRESS` - Outgoing traffic
- `PolicyType.BOTH` - Both directions

---

## Web Application Firewall

### Basic Usage

```python
from accelerapp.production.security import WebApplicationFirewall

# Initialize
waf = WebApplicationFirewall()

# Inspect request
result = waf.inspect_request(
    source_ip="192.168.1.100",
    endpoint="/api/users",
    method="GET",
    headers={"User-Agent": "..."},
    body=None
)

if not result["allowed"]:
    print(f"Blocked: {result['reason']}")
```

### Key Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `inspect_request()` | Check request | source_ip, endpoint, method, headers, body |
| `add_rule()` | Add WAF rule | rule_id, name, type, pattern |
| `block_ip()` | Block IP | ip |
| `unblock_ip()` | Unblock IP | ip |
| `whitelist_ip()` | Whitelist IP | ip |
| `set_rate_limit()` | Set rate limit | ip, per_minute, per_hour, per_day |
| `get_detections()` | Get threats | threat_level, limit |
| `generate_security_report()` | Get report | - |

### Built-in Protection

- **SQL Injection**: Blocks SQL keywords and patterns
- **XSS**: Blocks script tags and JavaScript
- **Path Traversal**: Blocks directory traversal attempts
- **Rate Limiting**: Per-minute/hour/day limits
- **IP Blacklist**: Block malicious IPs
- **Custom Rules**: Regex-based custom protection

### Rate Limiting

```python
waf.set_rate_limit(
    "192.168.1.100",
    requests_per_minute=60,
    requests_per_hour=1000,
    requests_per_day=10000
)
```

---

## Backup & Recovery

### Basic Usage

```python
from accelerapp.production.security import (
    BackupRecoverySystem,
    BackupType
)

# Initialize
system = BackupRecoverySystem()

# Create config
config = system.create_backup_config(
    "daily-backup",
    "Daily Backup",
    BackupType.FULL,
    "0 2 * * *",  # Cron schedule
    target_paths=["/data"],
    retention_days=30
)

# Start backup
record = system.start_backup("daily-backup")

# Complete backup
system.complete_backup(
    record.backup_id,
    size_bytes=1024*1024*100,
    files_count=1000,
    checksum="sha256:...",
    success=True
)
```

### Key Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `create_backup_config()` | Create config | config_id, name, type, schedule, paths |
| `start_backup()` | Start backup | config_id |
| `complete_backup()` | Mark complete | backup_id, size, files, checksum, success |
| `create_recovery_plan()` | Create DR plan | plan_id, name, steps, rto, rpo |
| `start_recovery()` | Start recovery | backup_id, plan_id |
| `complete_recovery()` | Mark complete | operation_id, restored, failed, success |
| `verify_backup()` | Verify integrity | backup_id |
| `cleanup_old_backups()` | Remove old | - |
| `generate_compliance_report()` | Get report | - |

### Backup Types

- `BackupType.FULL` - Complete backup
- `BackupType.INCREMENTAL` - Changes since last
- `BackupType.DIFFERENTIAL` - Changes since full

### Recovery Plans

```python
plan = system.create_recovery_plan(
    "dr-plan",
    "Disaster Recovery",
    "Complete system recovery",
    steps=[
        {"step": "1", "action": "Stop services"},
        {"step": "2", "action": "Restore data"},
        {"step": "3", "action": "Start services"}
    ],
    rto_minutes=240,  # Recovery Time Objective
    rpo_minutes=60    # Recovery Point Objective
)
```

---

## Security Auditing

### Basic Usage

```python
from accelerapp.production.security import (
    SecurityAuditSystem,
    AuditEventType,
    ComplianceStandard
)

# Initialize
audit = SecurityAuditSystem()

# Log event
event = audit.log_event(
    AuditEventType.ACCESS,
    actor="user@example.com",
    action="read",
    resource="/api/data",
    result="success"
)

# Run compliance scan
result = audit.run_compliance_scan(
    ComplianceStandard.SOC2
)
```

### Key Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `log_event()` | Log audit event | type, actor, action, resource, result |
| `get_events()` | Get events | type, actor, start_time, end_time |
| `run_compliance_check()` | Run check | check_id |
| `run_compliance_scan()` | Run full scan | standard |
| `generate_audit_report()` | Get report | start_time, end_time |
| `export_audit_trail()` | Export trail | start_time, end_time, format |
| `get_security_violations()` | Get violations | limit |
| `get_failed_authentications()` | Get failures | actor, limit |

### Audit Event Types

- `ACCESS` - Resource access
- `AUTHENTICATION` - Login attempts
- `AUTHORIZATION` - Permission checks
- `DATA_ACCESS` - Data operations
- `CONFIGURATION_CHANGE` - Config changes
- `SECURITY_VIOLATION` - Security events
- `POLICY_CHANGE` - Policy updates
- `SYSTEM_EVENT` - System operations

### Compliance Standards

- `SOC2` - Service Organization Control 2
- `ISO27001` - Information Security Management
- `HIPAA` - Health Insurance Portability
- `PCI_DSS` - Payment Card Industry
- `GDPR` - General Data Protection Regulation

---

## Orchestrator

### Basic Usage

```python
from accelerapp.production.security import Phase5SecurityOrchestrator

# Initialize - sets up all components
orchestrator = Phase5SecurityOrchestrator()

# Use integrated features
result = orchestrator.enforce_network_policies(
    "app-1", "app-2", 443, "https"
)

result = orchestrator.protect_endpoint(
    "192.168.1.100", "/api/users", "GET"
)

result = orchestrator.backup_system(
    "daily-backup", "admin"
)

# Get security dashboard
dashboard = orchestrator.get_security_dashboard()

# Get security posture
posture = orchestrator.get_security_posture()

# Generate compliance report
report = orchestrator.generate_compliance_report()
```

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `enforce_network_policies()` | Check network access | Allow/deny result |
| `protect_endpoint()` | Check with WAF | Allow/deny result |
| `backup_system()` | Execute backup | Backup result |
| `recover_system()` | Execute recovery | Recovery result |
| `scan_vulnerabilities()` | Scan for vulns | Scan result |
| `run_compliance_check()` | Check compliance | Compliance result |
| `get_security_dashboard()` | Get dashboard | All stats |
| `get_security_posture()` | Get posture | Score & status |
| `generate_compliance_report()` | Full report | Comprehensive report |

### Security Dashboard

```python
dashboard = orchestrator.get_security_dashboard()

print(f"Network Policies: {dashboard['network_policies']}")
print(f"WAF: {dashboard['waf']}")
print(f"Backups: {dashboard['backups']}")
print(f"Audit: {dashboard['audit']}")
print(f"Vulnerabilities: {dashboard['vulnerabilities']}")
```

### Security Posture

```python
posture = orchestrator.get_security_posture()

print(f"Score: {posture['overall_score']}/100")
print(f"Status: {posture['status']}")  # excellent, good, fair, poor
print(f"Components: {posture['component_scores']}")
print(f"Recommendations: {posture['recommendations']}")
```

---

## Configuration Files

### Network Policy YAML

```yaml
network_policies:
  - id: production-ingress
    name: Production Ingress
    namespace: production
    type: ingress
    priority: 10
    rules:
      - id: allow-https
        action: allow
        ports: [443]
        protocols: [https]
```

### Backup Configuration YAML

```yaml
backup:
  configs:
    - id: daily-full
      name: Daily Full Backup
      type: full
      schedule: "0 2 * * *"
      paths:
        - /data
        - /config
      retention_days: 30
      compression: true
      encryption: true
```

### WAF Configuration YAML

```yaml
waf:
  enabled: true
  default_rules:
    - sql_injection
    - xss
    - path_traversal
  rate_limits:
    default:
      per_minute: 60
      per_hour: 1000
      per_day: 10000
  custom_rules:
    - id: block-pattern
      name: Block Pattern
      pattern: "malicious_pattern"
      action: block
```

---

## Best Practices

### Network Policies

1. Use default-deny policies
2. Define explicit allow rules
3. Use labels for dynamic matching
4. Review violations regularly
5. Export to Kubernetes format

### WAF

1. Enable all default rules
2. Monitor detections regularly
3. Whitelist trusted IPs
4. Set appropriate rate limits
5. Add custom rules as needed

### Backups

1. Schedule regular backups
2. Test recovery procedures
3. Verify backup integrity
4. Clean up old backups
5. Document recovery plans

### Security Audit

1. Log all security events
2. Run regular compliance scans
3. Review violations immediately
4. Export audit trails
5. Generate periodic reports

---

## Troubleshooting

### Network Policy Issues

```python
# Check policy status
stats = enforcer.get_statistics()
print(f"Active policies: {stats['enabled_policies']}")

# Check violations
violations = enforcer.get_violations()
for v in violations:
    print(f"Violation: {v.source} -> {v.destination}")

# Enable policy
enforcer.enable_policy("policy-id")
```

### WAF Issues

```python
# Check WAF status
stats = waf.get_statistics()
print(f"WAF enabled: {stats['enabled']}")

# Check detections
detections = waf.get_detections()
for d in detections:
    print(f"Threat: {d.threat_level} from {d.source_ip}")

# Whitelist IP
waf.whitelist_ip("trusted-ip")
```

### Backup Issues

```python
# Check backup status
status = system.get_backup_status("config-id")
print(f"Last backup: {status['last_backup']}")

# Verify backup
result = system.verify_backup("backup-id")
print(f"Valid: {result['valid']}")

# Cleanup old backups
system.cleanup_old_backups()
```

---

## Examples

See `examples/phase5_security_demo.py` for complete working examples.

---

## Support

- **Documentation**: PHASE5_IMPLEMENTATION.md
- **Tests**: tests/test_phase5_security.py
- **Issues**: https://github.com/thewriterben/Accelerapp/issues
