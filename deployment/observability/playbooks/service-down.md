# Incident Response Playbook: Service Down

## Alert Details
**Alert Name:** ServiceDown  
**Severity:** Critical  
**Threshold:** Service unavailable for 2 minutes  

## Description
This alert fires when the Accelerapp service becomes unavailable and fails health checks.

## Immediate Actions (5 minutes)

### 1. Verify Service Status
```bash
# Kubernetes
kubectl get pods -n accelerapp
kubectl get deployments -n accelerapp

# Docker
docker ps | grep accelerapp
```

### 2. Check Pod/Container Status
```bash
# Kubernetes - Check pod status
kubectl describe pod <pod-name> -n accelerapp

# Kubernetes - Check recent events
kubectl get events -n accelerapp --sort-by='.lastTimestamp' | head -20

# Docker - Check container logs
docker logs accelerapp-main --tail=100
```

### 3. Check Resource Availability
```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n accelerapp

# Check disk space
df -h
```

## Common Causes and Solutions

### Cause 1: Pod CrashLoopBackOff

**Symptoms:**
- Pod status shows CrashLoopBackOff
- Container restarts frequently

**Investigation:**
```bash
# Check pod logs
kubectl logs -n accelerapp <pod-name> --previous

# Check pod events
kubectl describe pod -n accelerapp <pod-name>
```

**Solution:**
```bash
# Check configuration
kubectl get configmap accelerapp-config -n accelerapp -o yaml

# Check secrets
kubectl get secrets -n accelerapp

# Fix config and restart
kubectl rollout restart deployment/accelerapp -n accelerapp
```

### Cause 2: ImagePullBackOff

**Symptoms:**
- Pod cannot pull container image
- Status shows ImagePullBackOff

**Investigation:**
```bash
kubectl describe pod -n accelerapp <pod-name> | grep -A 5 "Events:"
```

**Solution:**
```bash
# Check image name and tag
kubectl get deployment accelerapp -n accelerapp -o yaml | grep image:

# Verify image exists
docker pull <image-name>

# Update deployment with correct image
kubectl set image deployment/accelerapp accelerapp=<correct-image> -n accelerapp
```

### Cause 3: Resource Exhaustion

**Symptoms:**
- Pod shows OOMKilled
- Node resources maxed out

**Investigation:**
```bash
# Check resource limits
kubectl describe pod -n accelerapp <pod-name> | grep -A 5 "Limits:"

# Check node capacity
kubectl describe node <node-name>
```

**Solution:**
```bash
# Increase resource limits
kubectl edit deployment accelerapp -n accelerapp
# Update memory/CPU limits

# Or scale horizontally
kubectl scale deployment/accelerapp --replicas=3 -n accelerapp
```

### Cause 4: Health Check Failures

**Symptoms:**
- Container running but failing health checks
- Pod shows not ready

**Investigation:**
```bash
# Check health endpoint manually
kubectl port-forward -n accelerapp <pod-name> 8080:8080
curl http://localhost:8080/health

# Check health check configuration
kubectl get deployment accelerapp -n accelerapp -o yaml | grep -A 10 "livenessProbe"
```

**Solution:**
```bash
# Temporarily disable health checks for debugging
kubectl edit deployment accelerapp -n accelerapp
# Comment out livenessProbe/readinessProbe

# Fix underlying issue
# Re-enable health checks
```

### Cause 5: Dependency Unavailable

**Symptoms:**
- Accelerapp up but failing to connect to dependencies
- Errors about Ollama/Redis/etc. unavailable

**Investigation:**
```bash
# Check all services
kubectl get services -n accelerapp

# Check Ollama
kubectl get pods -n accelerapp -l app=ollama

# Check connectivity
kubectl exec -n accelerapp <accelerapp-pod> -- curl http://ollama-service:11434/api/tags
```

**Solution:**
```bash
# Restart dependency
kubectl rollout restart deployment/ollama -n accelerapp

# Check service endpoints
kubectl get endpoints -n accelerapp ollama-service
```

## Recovery Procedures

### Quick Recovery (Restart)
```bash
# Kubernetes
kubectl rollout restart deployment/accelerapp -n accelerapp

# Docker
docker restart accelerapp-main
```

### Rollback to Previous Version
```bash
# Check history
kubectl rollout history deployment/accelerapp -n accelerapp

# Rollback
kubectl rollout undo deployment/accelerapp -n accelerapp

# Verify rollback
kubectl rollout status deployment/accelerapp -n accelerapp
```

### Complete Redeployment
```bash
# Delete and recreate
kubectl delete deployment accelerapp -n accelerapp
kubectl apply -f /path/to/deployment.yaml

# Or use helm
helm upgrade --install accelerapp ./helm/accelerapp -n accelerapp
```

## Monitoring During Recovery

### 1. Watch Pod Status
```bash
watch -n 2 kubectl get pods -n accelerapp
```

### 2. Stream Logs
```bash
kubectl logs -n accelerapp -f deployment/accelerapp
```

### 3. Check Metrics
- Grafana: http://grafana:3000
- Prometheus: http://prometheus:9090
- Check service uptime metric

## Verification Steps

After recovery, verify:

- [ ] All pods are running and ready
- [ ] Health checks passing
- [ ] Service accessible
- [ ] No errors in logs
- [ ] Metrics collecting normally
- [ ] Dependencies connected

```bash
# Verify deployment
kubectl get deployments -n accelerapp

# Test service
curl http://accelerapp-service.accelerapp:8080/health

# Check metrics endpoint
curl http://accelerapp-service.accelerapp:8080/metrics
```

## Communication

### During Incident
1. Post in #accelerapp-critical Slack channel
2. Update status page immediately
3. Notify on-call manager if > 5 minutes downtime

### After Recovery
1. Post all-clear in Slack
2. Update status page with resolution
3. Create incident ticket
4. Schedule post-mortem

## Post-Incident Actions

- [ ] Document root cause
- [ ] Update runbook if needed
- [ ] Create preventive tasks
- [ ] Review monitoring/alerting
- [ ] Conduct post-mortem within 24 hours

## Escalation Path

**Immediate escalation if:**
- Cannot diagnose in 5 minutes
- Cannot recover in 10 minutes
- Multiple services affected
- Data loss suspected

Contact: Senior Engineer → Engineering Manager → CTO

## Related Playbooks
- [High Error Rate](./high-error-rate.md)
- [Database Connection Issues](./database-issues.md)
- [Resource Exhaustion](./resource-exhaustion.md)
