# Operational Procedures

**Version**: 1.0.0  
**Last Updated**: 2025-10-14

This document provides standard operating procedures for Accelerapp operations teams.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Incident Response](#incident-response)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring and Alerting](#monitoring-and-alerting)
5. [Backup and Recovery](#backup-and-recovery)
6. [Security Operations](#security-operations)
7. [Performance Management](#performance-management)
8. [Cost Management](#cost-management)
9. [Team Communication](#team-communication)
10. [Runbooks](#runbooks)

---

## Daily Operations

### Daily Checklist

**Every Morning (9:00 AM)**

- [ ] Review overnight alerts and incidents
- [ ] Check system health dashboard
- [ ] Review application logs for errors
- [ ] Verify backup completion
- [ ] Check resource utilization (CPU, memory, disk)
- [ ] Review performance metrics
- [ ] Check cost dashboard for anomalies

### Health Check Procedure

```bash
#!/bin/bash
# daily-health-check.sh

echo "=== Accelerapp Daily Health Check ==="
echo "Date: $(date)"
echo ""

# 1. Check service status
echo "1. Service Status:"
kubectl get pods -n accelerapp
echo ""

# 2. Check resource usage
echo "2. Resource Usage:"
kubectl top nodes
kubectl top pods -n accelerapp
echo ""

# 3. Check recent errors
echo "3. Recent Errors (last hour):"
kubectl logs --since=1h -n accelerapp -l app=accelerapp | grep ERROR | tail -20
echo ""

# 4. Check database connections
echo "4. Database Status:"
kubectl exec -n accelerapp deploy/accelerapp -- python -c "
from accelerapp.database import check_connection
print('Database:', 'OK' if check_connection() else 'FAIL')
"
echo ""

# 5. Check disk space
echo "5. Disk Space:"
df -h | grep -E '(Filesystem|/dev/)'
echo ""

# 6. Summary
echo "=== Health Check Complete ==="
```

### Log Review Procedure

```python
#!/usr/bin/env python3
# review-logs.py

from accelerapp.monitoring import LogAnalyzer

analyzer = LogAnalyzer()

# Analyze logs from last 24 hours
results = analyzer.analyze_logs(hours=24)

print("Log Analysis Summary:")
print(f"  Total Errors: {results['error_count']}")
print(f"  Total Warnings: {results['warning_count']}")
print(f"  Critical Issues: {results['critical_count']}")

# Show top errors
print("\nTop 5 Errors:")
for i, error in enumerate(results['top_errors'][:5], 1):
    print(f"  {i}. {error['message']} (count: {error['count']})")

# Show anomalies
if results['anomalies']:
    print("\nAnomalies Detected:")
    for anomaly in results['anomalies']:
        print(f"  - {anomaly['description']}")
```

---

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **P1 - Critical** | Complete service outage | 15 minutes | Service down |
| **P2 - High** | Major feature unavailable | 1 hour | API errors |
| **P3 - Medium** | Minor feature issue | 4 hours | Slow response |
| **P4 - Low** | Cosmetic issue | 24 hours | UI glitch |

### P1 Critical Incident Response

**Immediate Actions (0-15 minutes)**

1. **Acknowledge** the incident
   ```bash
   # Update status page
   ./scripts/update-status.sh "Investigating service disruption"
   ```

2. **Assess** the situation
   ```bash
   # Quick health check
   kubectl get pods -n accelerapp
   kubectl get services -n accelerapp
   kubectl describe pod <failing-pod> -n accelerapp
   ```

3. **Notify** stakeholders
   ```bash
   # Send notifications
   ./scripts/notify-incident.sh --severity=P1 --message="Service disruption"
   ```

4. **Start** war room (if needed)
   - Create Zoom/Slack channel
   - Page on-call engineers
   - Assign incident commander

**Investigation (15-60 minutes)**

1. **Check logs**
   ```bash
   # Application logs
   kubectl logs -f deployment/accelerapp -n accelerapp --tail=100
   
   # Error logs only
   kubectl logs deployment/accelerapp -n accelerapp | grep ERROR
   ```

2. **Check metrics**
   - Open Grafana dashboard
   - Review CPU, memory, network
   - Check error rates
   - Review request latency

3. **Check recent changes**
   ```bash
   # Check recent deployments
   kubectl rollout history deployment/accelerapp -n accelerapp
   
   # Check config changes
   git log --since="2 hours ago" --oneline
   ```

**Resolution**

1. **Apply fix**
   - Rollback deployment if needed
   - Apply hotfix
   - Scale resources

2. **Verify fix**
   ```bash
   # Run health checks
   ./scripts/health-check.sh
   
   # Test critical endpoints
   curl https://api.accelerapp.io/health
   ```

3. **Update status**
   ```bash
   # Mark as resolved
   ./scripts/update-status.sh "Issue resolved"
   ```

**Post-Incident (24-48 hours)**

1. **Write post-mortem**
   - Timeline of events
   - Root cause analysis
   - Impact assessment
   - Action items

2. **Update runbooks**
   - Document new procedures
   - Update troubleshooting guide

3. **Implement preventions**
   - Add monitoring
   - Add tests
   - Update alerts

### Incident Communication Template

```markdown
# Incident Report: [INCIDENT-ID]

## Summary
[Brief description of the incident]

## Timeline
- **[HH:MM]** - Incident detected
- **[HH:MM]** - Investigation started
- **[HH:MM]** - Root cause identified
- **[HH:MM]** - Fix applied
- **[HH:MM]** - Service restored

## Impact
- **Duration**: [X hours Y minutes]
- **Users Affected**: [number/percentage]
- **Services Affected**: [list services]
- **Revenue Impact**: $[amount] (if applicable)

## Root Cause
[Detailed explanation of what caused the incident]

## Resolution
[How the incident was resolved]

## Action Items
1. [ ] [Action item 1] - Owner: [Name] - Due: [Date]
2. [ ] [Action item 2] - Owner: [Name] - Due: [Date]

## Lessons Learned
- [Key takeaway 1]
- [Key takeaway 2]
```

---

## Deployment Procedures

### Production Deployment Checklist

**Pre-Deployment (2 days before)**

- [ ] Review and approve all changes
- [ ] Run full test suite
- [ ] Perform security scan
- [ ] Review performance benchmarks
- [ ] Prepare rollback plan
- [ ] Schedule deployment window
- [ ] Notify stakeholders

**Day of Deployment**

- [ ] Create deployment branch
- [ ] Tag release version
- [ ] Create backup
- [ ] Put application in maintenance mode (if needed)
- [ ] Run deployment
- [ ] Perform smoke tests
- [ ] Monitor for 1 hour
- [ ] Update documentation

### Deployment Command

```bash
#!/bin/bash
# deploy-production.sh

set -e  # Exit on error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "=== Deploying Accelerapp v$VERSION to Production ==="

# 1. Backup current state
echo "1. Creating backup..."
./scripts/backup.sh

# 2. Update image
echo "2. Updating container image..."
kubectl set image deployment/accelerapp \
    accelerapp=accelerapp:$VERSION \
    -n accelerapp

# 3. Wait for rollout
echo "3. Waiting for rollout to complete..."
kubectl rollout status deployment/accelerapp -n accelerapp --timeout=10m

# 4. Run health checks
echo "4. Running health checks..."
./scripts/health-check.sh

# 5. Run smoke tests
echo "5. Running smoke tests..."
./scripts/smoke-tests.sh

echo "=== Deployment Complete ==="
echo "Version $VERSION is now live in production"
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback-production.sh

echo "=== Rolling back production deployment ==="

# Get current revision
CURRENT=$(kubectl rollout history deployment/accelerapp -n accelerapp | tail -1 | awk '{print $1}')
echo "Current revision: $CURRENT"

# Rollback to previous
echo "Rolling back to previous revision..."
kubectl rollout undo deployment/accelerapp -n accelerapp

# Wait for rollback
kubectl rollout status deployment/accelerapp -n accelerapp --timeout=5m

# Verify
echo "Running health checks..."
./scripts/health-check.sh

echo "=== Rollback Complete ==="
```

---

## Monitoring and Alerting

### Alert Response Procedures

#### High Error Rate Alert

**Trigger**: Error rate > 5% for 5 minutes

**Response**:
1. Check application logs for error patterns
2. Review recent deployments
3. Check external dependencies
4. Scale if needed
5. Create incident if unresolved in 15 minutes

```bash
# Investigate high error rate
./scripts/analyze-errors.sh --last=15m
```

#### High Latency Alert

**Trigger**: P95 latency > 500ms for 5 minutes

**Response**:
1. Check database query performance
2. Review resource utilization
3. Check for slow external API calls
4. Profile application performance
5. Scale horizontally if needed

```python
# Profile slow endpoints
from accelerapp.production.optimization import PerformanceProfiler

profiler = PerformanceProfiler()
# Profile identified slow endpoint
result = profiler.profile_function(slow_function)
print(result.recommendations)
```

#### High Memory Usage Alert

**Trigger**: Memory > 90% for 10 minutes

**Response**:
1. Identify memory-intensive processes
2. Check for memory leaks
3. Restart affected pods if needed
4. Increase memory limits if appropriate
5. Investigate root cause

```bash
# Check memory usage
kubectl top pods -n accelerapp --sort-by=memory

# Restart high-memory pod
kubectl rollout restart deployment/accelerapp -n accelerapp
```

### On-Call Rotation

**Primary On-Call Engineer**
- Respond to P1/P2 incidents
- Monitor alerts 24/7
- Escalate if needed

**Secondary On-Call Engineer**
- Backup for primary
- Respond if primary unavailable
- Take over for complex incidents

**On-Call Schedule**
- Weekly rotation
- Handoff Friday 5 PM
- Handoff meeting required

---

## Backup and Recovery

### Backup Procedures

**Daily Automated Backup**

```bash
#!/bin/bash
# daily-backup.sh

DATE=$(date +%Y%m%d)

# 1. Database backup
echo "Backing up database..."
kubectl exec -n accelerapp deploy/postgres -- \
    pg_dump -U postgres accelerapp | \
    gzip > /backups/db-$DATE.sql.gz

# 2. Configuration backup
echo "Backing up configuration..."
kubectl get configmap -n accelerapp -o yaml > /backups/config-$DATE.yaml
kubectl get secret -n accelerapp -o yaml > /backups/secrets-$DATE.yaml

# 3. Upload to S3
echo "Uploading to S3..."
aws s3 sync /backups/ s3://accelerapp-backups/$(date +%Y/%m)/

# 4. Clean old backups (keep 30 days)
echo "Cleaning old backups..."
find /backups/ -type f -mtime +30 -delete

echo "Backup complete: $DATE"
```

### Recovery Procedures

**Database Recovery**

```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

echo "=== Restoring Database ==="
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "This will overwrite the current database. Continue? (yes/no) " -r
if [[ ! $REPLY =~ ^yes$ ]]; then
    exit 1
fi

# 1. Download backup from S3
aws s3 cp s3://accelerapp-backups/$BACKUP_FILE /tmp/restore.sql.gz

# 2. Decompress
gunzip /tmp/restore.sql.gz

# 3. Stop application
kubectl scale deployment accelerapp --replicas=0 -n accelerapp

# 4. Restore database
kubectl exec -i -n accelerapp deploy/postgres -- \
    psql -U postgres accelerapp < /tmp/restore.sql

# 5. Restart application
kubectl scale deployment accelerapp --replicas=3 -n accelerapp

# 6. Verify
./scripts/health-check.sh

echo "=== Restore Complete ==="
```

---

## Security Operations

### Security Checklist

**Daily**
- [ ] Review security alerts
- [ ] Check failed login attempts
- [ ] Review audit logs

**Weekly**
- [ ] Run vulnerability scan
- [ ] Review access permissions
- [ ] Check SSL certificate expiry

**Monthly**
- [ ] Update dependencies
- [ ] Security patch review
- [ ] Access audit

### Vulnerability Response

**Procedure**:

1. **Assess Severity**
   ```python
   from accelerapp.production.security import VulnerabilityScanner
   
   scanner = VulnerabilityScanner()
   scan_result = scanner.scan_dependencies(get_dependencies())
   
   critical = [v for v in scan_result.vulnerabilities if v.severity == "critical"]
   ```

2. **Create Incident** (if critical)

3. **Apply Patches**
   ```bash
   # Update affected packages
   pip install --upgrade <package>
   
   # Test
   pytest tests/
   
   # Deploy
   ./scripts/deploy-production.sh <version>
   ```

4. **Verify Fix**
   ```python
   # Re-scan
   new_scan = scanner.scan_dependencies(get_dependencies())
   assert len([v for v in new_scan.vulnerabilities if v.severity == "critical"]) == 0
   ```

---

## Performance Management

### Weekly Performance Review

```python
#!/usr/bin/env python3
# weekly-performance-review.py

from accelerapp.production import PerformanceBenchmark
from accelerapp.production.optimization import PerformanceProfiler

# Run benchmarks
benchmark = PerformanceBenchmark()
results = benchmark.run_all_benchmarks(iterations=1000)

# Get statistics
stats = benchmark.get_statistics()

print("Weekly Performance Report")
print("=" * 50)
print(f"Average Duration: {stats['avg_duration_ms']:.2f}ms")
print(f"Average Ops/Sec: {stats['avg_operations_per_second']:.0f}")

# Check for regressions
profiler = PerformanceProfiler()
regressions = profiler.detect_regressions(threshold_percent=10.0)

if regressions:
    print("\n⚠️  Performance Regressions Detected:")
    for reg in regressions:
        print(f"  - {reg['function']}: {reg['degradation_percent']:.1f}% slower")
```

---

## Cost Management

### Weekly Cost Review

```python
#!/usr/bin/env python3
# weekly-cost-review.py

from accelerapp.production.optimization import CostMonitor

monitor = track_all_resources()

# Generate report
report = monitor.generate_cost_report("weekly")

print("Weekly Cost Report")
print("=" * 50)
print(f"Total Cost: ${report.total_cost:.2f}")
print(f"Potential Savings: ${report.estimated_savings:.2f}")

# Show top opportunities
opportunities = sorted(
    report.optimization_opportunities,
    key=lambda x: x.get("potential_savings", 0),
    reverse=True
)[:5]

print("\nTop Cost Optimization Opportunities:")
for i, opp in enumerate(opportunities, 1):
    print(f"{i}. {opp['type']}: ${opp.get('potential_savings', 0):.2f}")
```

---

## Team Communication

### Communication Channels

- **Slack #accelerapp-ops**: Daily operations
- **Slack #accelerapp-incidents**: Incident response
- **Slack #accelerapp-deploys**: Deployment notifications
- **PagerDuty**: Critical alerts
- **Weekly Ops Meeting**: Thursdays 2 PM

### Status Updates

**During Incidents**:
- Update every 30 minutes
- Use status page
- Post in #accelerapp-incidents

**For Deployments**:
- Announce 24 hours before
- Post start/completion
- Summarize changes

---

## Runbooks

### Runbook: Service Won't Start

**Symptoms**: Pods in CrashLoopBackOff

**Investigation**:
```bash
# Check pod status
kubectl get pods -n accelerapp

# Check logs
kubectl logs <pod-name> -n accelerapp

# Check events
kubectl describe pod <pod-name> -n accelerapp
```

**Common Causes**:
1. Configuration error
2. Missing secrets
3. Database connection failure
4. Resource limits too low

**Resolution**:
```bash
# Fix configuration
kubectl edit configmap accelerapp-config -n accelerapp

# Apply changes
kubectl rollout restart deployment/accelerapp -n accelerapp
```

### Runbook: High Database CPU

**Symptoms**: Database CPU > 80%

**Investigation**:
```sql
-- Find slow queries
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start desc;
```

**Resolution**:
1. Kill long-running queries if needed
2. Add indexes for slow queries
3. Optimize queries
4. Consider read replicas
5. Upgrade database instance

---

## Appendix

### Contact Information

- **Operations Lead**: ops-lead@company.com
- **Security Team**: security@company.com
- **Platform Team**: platform@company.com
- **On-Call Phone**: +1-555-ON-CALL

### Useful Commands

```bash
# View all pods
kubectl get pods -n accelerapp

# Get logs
kubectl logs -f deployment/accelerapp -n accelerapp

# Execute command in pod
kubectl exec -it <pod-name> -n accelerapp -- /bin/bash

# Scale deployment
kubectl scale deployment accelerapp --replicas=5 -n accelerapp

# Port forward
kubectl port-forward svc/accelerapp 8000:8000 -n accelerapp

# Check resource usage
kubectl top nodes
kubectl top pods -n accelerapp
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Next Review**: 2025-11-14
