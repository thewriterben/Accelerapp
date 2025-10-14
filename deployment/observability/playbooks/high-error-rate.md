# Incident Response Playbook: High Error Rate

## Alert Details
**Alert Name:** HighErrorRate  
**Severity:** Critical  
**Threshold:** Error rate > 5% for 5 minutes  

## Description
This alert fires when the application error rate exceeds 5% of total requests over a 5-minute period.

## Immediate Actions

### 1. Verify the Alert (1-2 minutes)
- [ ] Check Grafana dashboard for error rate trend
- [ ] Verify the alert is not a false positive
- [ ] Check the time range of the issue

**Grafana Query:**
```promql
rate(accelerapp_errors_total[5m])
```

### 2. Assess Impact (2-3 minutes)
- [ ] Check affected services/endpoints
- [ ] Identify error types from logs
- [ ] Determine number of affected users
- [ ] Check if error rate is increasing or stable

**Kibana Query:**
```
level:ERROR AND app:accelerapp AND @timestamp:[now-15m TO now]
```

### 3. Check System Health (2-3 minutes)
- [ ] Verify Accelerapp service is running
- [ ] Check LLM service (Ollama) availability
- [ ] Review CPU and memory usage
- [ ] Check disk space availability

**Health Check:**
```bash
kubectl get pods -n accelerapp
kubectl logs -n accelerapp <pod-name> --tail=100
```

## Investigation Steps

### 4. Identify Root Cause (5-10 minutes)

#### A. Check Application Logs
```bash
# Kubernetes
kubectl logs -n accelerapp deployment/accelerapp --tail=500 | grep ERROR

# Docker
docker logs accelerapp-main --tail=500 | grep ERROR
```

#### B. Check Jaeger for Failed Traces
- Open Jaeger UI: http://jaeger-query:16686
- Filter by: `error=true`
- Look for common patterns in failed traces

#### C. Check Recent Deployments
```bash
kubectl rollout history deployment/accelerapp -n accelerapp
```

#### D. Common Issues to Check:
- [ ] LLM service connection failures
- [ ] Database/cache connection issues
- [ ] External API failures
- [ ] Memory/resource exhaustion
- [ ] Configuration errors
- [ ] Code generation failures

### 5. Determine Severity

**Critical:** Error rate > 10% or core functionality broken
- Impact: High number of users affected
- Action: Page on-call engineer
- SLA: Respond within 15 minutes

**High:** Error rate 5-10% or non-critical features broken
- Impact: Some users affected
- Action: Notify team in Slack
- SLA: Respond within 30 minutes

## Resolution Steps

### For LLM Service Issues
```bash
# Check Ollama status
kubectl get pods -n accelerapp -l app=ollama

# Restart Ollama if needed
kubectl rollout restart deployment/ollama -n accelerapp
```

### For Application Issues
```bash
# Check for crashloop
kubectl get pods -n accelerapp

# View recent events
kubectl describe pod <pod-name> -n accelerapp

# Restart application
kubectl rollout restart deployment/accelerapp -n accelerapp
```

### For Resource Issues
```bash
# Check resource usage
kubectl top pods -n accelerapp

# Scale up if needed
kubectl scale deployment/accelerapp --replicas=3 -n accelerapp
```

### For Configuration Issues
```bash
# Check config map
kubectl get configmap accelerapp-config -n accelerapp -o yaml

# Update config if needed
kubectl edit configmap accelerapp-config -n accelerapp
kubectl rollout restart deployment/accelerapp -n accelerapp
```

## Rollback Procedure

If recent deployment caused the issue:
```bash
# Get rollout history
kubectl rollout history deployment/accelerapp -n accelerapp

# Rollback to previous version
kubectl rollout undo deployment/accelerapp -n accelerapp

# Or rollback to specific revision
kubectl rollout undo deployment/accelerapp --to-revision=<revision> -n accelerapp
```

## Communication

### Internal Communication
- Post incident status in #accelerapp-incidents Slack channel
- Update incident ticket with findings
- Notify team of resolution

### External Communication (if needed)
- Update status page: https://status.accelerapp.example.com
- Notify affected users via email
- Post incident report after resolution

## Post-Incident

### 1. Verify Resolution
- [ ] Confirm error rate returned to normal (<1%)
- [ ] Monitor for 15 minutes to ensure stability
- [ ] Check no new alerts are firing

### 2. Documentation
- [ ] Update incident ticket with root cause
- [ ] Document resolution steps taken
- [ ] Note any configuration changes made

### 3. Follow-up Actions
- [ ] Schedule post-mortem meeting (within 24 hours)
- [ ] Create tasks for preventing recurrence
- [ ] Update monitoring if needed
- [ ] Review and update this playbook if necessary

## Escalation Path

1. **L1 - On-call Engineer** (0-15 min)
2. **L2 - Senior Engineer** (15-30 min)
3. **L3 - Engineering Manager** (30+ min)
4. **L4 - CTO** (if customer impact is severe)

## Related Playbooks
- [Service Down](./service-down.md)
- [High Memory Usage](./high-memory-usage.md)
- [Slow Response Time](./slow-response-time.md)

## Useful Links
- [Grafana Dashboard](http://grafana:3000)
- [Kibana Logs](http://kibana:5601)
- [Jaeger Traces](http://jaeger-query:16686)
- [Prometheus Alerts](http://prometheus:9090/alerts)
