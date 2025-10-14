# Accelerapp Helm Chart

This Helm chart deploys Accelerapp on Kubernetes with production-ready configurations including auto-scaling, persistent storage, and monitoring.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (if persistence is enabled)

## Installing the Chart

### From Local Directory

```bash
helm install accelerapp ./deployment/helm/accelerapp \
  --namespace accelerapp \
  --create-namespace
```

### With Custom Values

```bash
helm install accelerapp ./deployment/helm/accelerapp \
  -f custom-values.yaml \
  --namespace accelerapp \
  --create-namespace
```

## Uninstalling the Chart

```bash
helm uninstall accelerapp --namespace accelerapp
```

## Configuration

The following table lists the configurable parameters of the Accelerapp chart and their default values.

### Basic Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `ghcr.io/thewriterben/accelerapp` |
| `image.tag` | Image tag | `"latest-production"` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8080` |

### Resource Limits

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.requests.memory` | Memory request | `"256Mi"` |
| `resources.requests.cpu` | CPU request | `"250m"` |
| `resources.limits.memory` | Memory limit | `"512Mi"` |
| `resources.limits.cpu` | CPU limit | `"500m"` |

### Autoscaling

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `70` |
| `autoscaling.targetMemoryUtilizationPercentage` | Target Memory % | `80` |

### Persistence

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistence | `true` |
| `persistence.size` | Volume size | `"10Gi"` |
| `persistence.storageClass` | Storage class | `""` (default) |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |

### Pod Disruption Budget

| Parameter | Description | Default |
|-----------|-------------|---------|
| `podDisruptionBudget.enabled` | Enable PDB | `true` |
| `podDisruptionBudget.minAvailable` | Min available pods | `1` |

## Example Configurations

### Production Environment

```yaml
# production-values.yaml
replicaCount: 3

image:
  tag: "v1.0.0-production"
  pullPolicy: Always

resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60
  targetMemoryUtilizationPercentage: 70

persistence:
  enabled: true
  size: 50Gi
  storageClass: "fast-ssd"

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

Install:
```bash
helm install accelerapp ./deployment/helm/accelerapp \
  -f production-values.yaml \
  --namespace production \
  --create-namespace
```

### Development Environment

```yaml
# dev-values.yaml
replicaCount: 1

image:
  tag: "develop-development"
  pullPolicy: Always

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: false

persistence:
  enabled: false

podDisruptionBudget:
  enabled: false
```

Install:
```bash
helm install accelerapp ./deployment/helm/accelerapp \
  -f dev-values.yaml \
  --namespace development \
  --create-namespace
```

## Upgrading

### Upgrade with New Values

```bash
helm upgrade accelerapp ./deployment/helm/accelerapp \
  -f updated-values.yaml \
  --namespace accelerapp
```

### Rollback

```bash
# List releases
helm history accelerapp -n accelerapp

# Rollback to previous version
helm rollback accelerapp -n accelerapp

# Rollback to specific revision
helm rollback accelerapp 1 -n accelerapp
```

## Monitoring

### Check Deployment Status

```bash
# Helm status
helm status accelerapp -n accelerapp

# Pod status
kubectl get pods -n accelerapp

# Service status
kubectl get svc -n accelerapp

# HPA status
kubectl get hpa -n accelerapp
```

### View Logs

```bash
# All pods
kubectl logs -l app=accelerapp -n accelerapp --tail=100 -f

# Specific pod
kubectl logs <pod-name> -n accelerapp -f
```

### Scale Manually

```bash
# Scale deployment
kubectl scale deployment accelerapp --replicas=5 -n accelerapp
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n accelerapp

# Check events
kubectl get events -n accelerapp --sort-by='.lastTimestamp'
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n accelerapp

# Describe PVC
kubectl describe pvc accelerapp-data -n accelerapp
```

### Resource Constraints

```bash
# Check resource usage
kubectl top pods -n accelerapp
kubectl top nodes
```

## Advanced Usage

### Using Private Registry

```yaml
image:
  repository: private-registry.com/accelerapp
  pullPolicy: Always

imagePullSecrets:
  - name: regcred
```

Create secret:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=private-registry.com \
  --docker-username=<username> \
  --docker-password=<password> \
  --namespace accelerapp
```

### Custom Environment Variables

```yaml
env:
  - name: ACCELERAPP_MODE
    value: "production"
  - name: OLLAMA_HOST
    value: "http://ollama-service:11434"
  - name: CUSTOM_VAR
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: custom-value
```

### Ingress Configuration

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: accelerapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: accelerapp-tls
      hosts:
        - accelerapp.example.com
```

## Security

### Network Policies

Create a network policy to restrict traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: accelerapp-netpol
  namespace: accelerapp
spec:
  podSelector:
    matchLabels:
      app: accelerapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Pod Security

The chart includes security contexts:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

## Support

For issues and questions:
- GitHub: https://github.com/thewriterben/Accelerapp/issues
- Documentation: https://github.com/thewriterben/Accelerapp/docs

## License

MIT License
