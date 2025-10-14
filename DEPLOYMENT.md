# Accelerapp Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Status**: Production Ready

## Overview

This guide covers containerization and CI/CD deployment options for Accelerapp, including Docker, Kubernetes, and automated workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Workflows](#cicd-workflows)
- [Monitoring](#monitoring)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Using Docker Compose (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp

# Start all services
cd deployment/docker
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f accelerapp

# Stop services
docker-compose down
```

## Docker Deployment

### Building Docker Images

Accelerapp provides multi-stage Dockerfile with three targets:

#### 1. Production Image (Minimal)

```bash
docker build -t accelerapp:latest \
  -f deployment/docker/Dockerfile \
  --target production .
```

Features:
- Minimal footprint
- Non-root user
- Optimized for production
- No development tools

#### 2. Development Image

```bash
docker build -t accelerapp:dev \
  -f deployment/docker/Dockerfile \
  --target development .
```

Features:
- Includes test frameworks
- Development tools (pytest, black, flake8, mypy)
- Source code and tests included

#### 3. Base Image

```bash
docker build -t accelerapp:base \
  -f deployment/docker/Dockerfile \
  --target base .
```

### Running Docker Containers

#### Basic Usage

```bash
# Run with default command
docker run --rm accelerapp:latest

# Run specific command
docker run --rm accelerapp:latest accelerapp --version

# Interactive mode
docker run -it --rm accelerapp:latest bash
```

#### With Volume Mounts

```bash
docker run -d \
  --name accelerapp \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/output:/app/output \
  accelerapp:latest
```

#### With Environment Variables

```bash
docker run -d \
  --name accelerapp \
  -e ACCELERAPP_MODE=production \
  -e OLLAMA_HOST=http://ollama:11434 \
  accelerapp:latest
```

### Docker Compose Services

The `docker-compose.yml` includes:

1. **accelerapp**: Main application service
2. **ollama**: Local LLM service
3. **redis**: Message bus (optional)
4. **monitoring**: Health check service (optional)

#### Start Specific Services

```bash
# Start only main app and ollama
docker-compose up -d accelerapp ollama

# Start with monitoring
docker-compose --profile monitoring up -d
```

#### Configuration

Edit `deployment/docker/docker-compose.yml`:

```yaml
services:
  accelerapp:
    environment:
      - ACCELERAPP_MODE=production
      - OLLAMA_HOST=http://ollama:11434
    volumes:
      - ./custom-models:/app/models
```

## Kubernetes Deployment

### Using Helm (Recommended)

#### Install Helm Chart

```bash
# Add the repository (if published)
# helm repo add accelerapp https://charts.accelerapp.io
# helm repo update

# Install from local chart
helm install accelerapp ./deployment/helm/accelerapp \
  --namespace accelerapp \
  --create-namespace
```

#### Customize Installation

Create `custom-values.yaml`:

```yaml
replicaCount: 3

image:
  repository: ghcr.io/thewriterben/accelerapp
  tag: "latest-production"
  pullPolicy: IfNotPresent

resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

persistence:
  enabled: true
  size: 10Gi
  storageClass: "fast-ssd"
```

Install with custom values:

```bash
helm install accelerapp ./deployment/helm/accelerapp \
  -f custom-values.yaml \
  --namespace accelerapp \
  --create-namespace
```

#### Helm Operations

```bash
# Upgrade release
helm upgrade accelerapp ./deployment/helm/accelerapp \
  -f custom-values.yaml

# Check status
helm status accelerapp -n accelerapp

# View values
helm get values accelerapp -n accelerapp

# Rollback
helm rollback accelerapp -n accelerapp

# Uninstall
helm uninstall accelerapp -n accelerapp
```

### Using Kubernetes Manifests

```bash
# Apply deployment
kubectl apply -f deployment/kubernetes/accelerapp-deployment.yaml

# Check deployment
kubectl get deployments -n accelerapp
kubectl get pods -n accelerapp

# View logs
kubectl logs -f deployment/accelerapp -n accelerapp

# Delete deployment
kubectl delete -f deployment/kubernetes/accelerapp-deployment.yaml
```

## CI/CD Workflows

### GitHub Actions Workflows

Accelerapp includes three automated workflows:

#### 1. CI/CD Pipeline (`.github/workflows/ci.yml`)

Triggers:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

Jobs:
- **Test**: Runs tests on Python 3.8-3.12
- **Lint**: Code quality checks (black, flake8, isort, mypy)
- **Security**: Bandit and Safety scans
- **Performance**: Performance test suite
- **Build**: Package building and validation

#### 2. Docker Build and Push (`.github/workflows/docker.yml`)

Triggers:
- Push to `main` or `develop` branches
- Tags matching `v*`
- Pull requests to `main`
- Manual trigger

Jobs:
- **build-and-push**: Builds and pushes Docker images
  - Multi-platform (linux/amd64, linux/arm64)
  - Multiple targets (production, development)
  - Automatic tagging based on branch/tag
- **build-compose**: Tests Docker Compose setup
- **scan-security**: Trivy security scanning
- **publish-manifest**: Multi-arch manifest for releases

#### 3. Security Scanning (`.github/workflows/security.yml`)

Triggers:
- Weekly schedule
- Manual trigger

Jobs:
- Dependency vulnerability scanning
- Code security analysis

#### 4. Release (`.github/workflows/release.yml`)

Triggers:
- GitHub release published
- Manual trigger

Jobs:
- Build and publish Python package to PyPI
- Create GitHub release assets
- Build documentation

### Docker Image Tags

Images are pushed to GitHub Container Registry:

```
ghcr.io/thewriterben/accelerapp:<tag>-<target>
```

Tag formats:
- `main-production`: Latest from main branch (production)
- `main-development`: Latest from main branch (development)
- `develop-production`: Latest from develop branch
- `v1.0.0-production`: Specific version tag
- `sha-<commit>-production`: Specific commit

Examples:
```bash
# Pull latest production image
docker pull ghcr.io/thewriterben/accelerapp:main-production

# Pull specific version
docker pull ghcr.io/thewriterben/accelerapp:v1.0.0-production

# Pull development image
docker pull ghcr.io/thewriterben/accelerapp:main-development
```

## Monitoring

### Health Check Endpoints

When using the monitoring service:

```bash
# Health check
curl http://localhost:8080/health

# Metrics (Prometheus format)
curl http://localhost:8080/metrics

# Service status
curl http://localhost:8080/status
```

### Kubernetes Health Probes

The Helm chart includes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCELERAPP_MODE` | Deployment mode | `production` |
| `OLLAMA_HOST` | Ollama service URL | `http://localhost:11434` |
| `ACCELERAPP_MODELS_DIR` | Models directory | `/app/models` |
| `ACCELERAPP_CACHE_DIR` | Cache directory | `/app/cache` |
| `ACCELERAPP_OUTPUT_DIR` | Output directory | `/app/output` |
| `MONITOR_PORT` | Monitoring service port | `8080` |

### Volume Mounts

Recommended volumes:

```yaml
volumes:
  - /path/to/models:/app/models    # Pre-trained models
  - /path/to/cache:/app/cache      # Runtime cache
  - /path/to/output:/app/output    # Generated output
```

## Troubleshooting

### Docker Issues

#### Container won't start

```bash
# Check logs
docker logs accelerapp

# Inspect container
docker inspect accelerapp

# Run with shell access
docker run -it --rm accelerapp:latest bash
```

#### Port conflicts

```bash
# Find process using port
lsof -i :8080

# Use different port
docker run -p 8081:8080 accelerapp:latest
```

### Kubernetes Issues

#### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n accelerapp

# Check events
kubectl get events -n accelerapp --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n accelerapp
```

#### Resource constraints

```bash
# Check resource usage
kubectl top pods -n accelerapp
kubectl top nodes

# Scale deployment
kubectl scale deployment accelerapp --replicas=2 -n accelerapp
```

### CI/CD Issues

#### Workflow failures

1. Check GitHub Actions logs
2. Verify secrets are configured:
   - `GITHUB_TOKEN` (automatic)
   - `PYPI_API_TOKEN` (for releases)
   - `TEST_PYPI_API_TOKEN` (optional)

#### Docker build failures

```bash
# Test build locally
docker build -f deployment/docker/Dockerfile --target production .

# Check .dockerignore
cat .dockerignore
```

## Security Considerations

### Docker Security

1. **Non-root user**: Production image runs as non-root user (UID 1000)
2. **Minimal image**: Based on `python:3.11-slim`
3. **No secrets in image**: Use environment variables or secrets management
4. **Regular scanning**: Trivy scans in CI/CD

### Kubernetes Security

1. **RBAC**: Use appropriate service accounts
2. **Network Policies**: Restrict pod-to-pod communication
3. **Secrets**: Use Kubernetes secrets for sensitive data
4. **Pod Security**: Configure security contexts

Example:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
      - ALL
```

## Best Practices

### Development Workflow

1. Develop locally with Docker Compose
2. Test with development image
3. Push to feature branch
4. CI runs tests automatically
5. Merge to develop/main
6. Docker images built and pushed
7. Deploy to staging/production

### Production Deployment

1. Use Helm for Kubernetes deployments
2. Enable autoscaling
3. Configure resource limits
4. Set up monitoring and alerts
5. Use persistent volumes for data
6. Regular backups
7. Security scanning

### Versioning

- Use semantic versioning (v1.0.0)
- Tag releases in Git
- Docker images automatically tagged
- Helm chart versions match app versions

## Additional Resources

- [Helm Chart README](deployment/helm/accelerapp/README.md)
- [Docker Deployment README](deployment/README.md)
- [Phase 3 Features](docs/PHASE3_FEATURES.md)
- [Testing Guide](TESTING.md)

## Support

For issues and questions:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: https://github.com/thewriterben/Accelerapp/docs

## License

MIT License - see [LICENSE](LICENSE) for details
