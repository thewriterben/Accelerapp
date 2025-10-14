# Accelerapp Deployment Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0 | **Status**: Production Ready

This directory contains deployment configurations for running Accelerapp in various environments, including Docker, Kubernetes, air-gapped, and offline installations.

## Directory Structure

```
deployment/
├── docker/              # Docker containers and compose files
├── kubernetes/          # Kubernetes manifests
├── install/            # Installation scripts
├── monitoring/         # Health checks and monitoring
└── README.md           # This file
```

## Deployment Options

### 1. Docker Deployment

#### Quick Start

```bash
cd deployment/docker
docker-compose up -d
```

#### Building Images

```bash
# Build production image
docker build -t accelerapp:latest -f deployment/docker/Dockerfile --target production .

# Build development image
docker build -t accelerapp:dev -f deployment/docker/Dockerfile --target development .
```

#### Air-Gapped Docker Deployment

For air-gapped environments:

1. Build and save images on a connected machine:
```bash
docker build -t accelerapp:latest .
docker save accelerapp:latest -o accelerapp-latest.tar
docker pull ollama/ollama:latest
docker save ollama/ollama:latest -o ollama-latest.tar
```

2. Transfer tar files to air-gapped environment

3. Load images:
```bash
docker load -i accelerapp-latest.tar
docker load -i ollama-latest.tar
```

4. Start services:
```bash
docker-compose up -d
```

### 2. Kubernetes Deployment

#### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Persistent storage provisioner

#### Deploy to Kubernetes

```bash
# Create namespace and deploy
kubectl apply -f deployment/kubernetes/accelerapp-deployment.yaml

# Check deployment status
kubectl get pods -n accelerapp

# View logs
kubectl logs -n accelerapp -l app=accelerapp

# Access service
kubectl port-forward -n accelerapp svc/accelerapp-service 8080:8080
```

#### Air-Gapped Kubernetes Deployment

1. Pre-pull and save images (on connected machine):
```bash
docker pull accelerapp:latest
docker save accelerapp:latest | gzip > accelerapp-k8s.tar.gz
```

2. Load images on all cluster nodes:
```bash
gunzip -c accelerapp-k8s.tar.gz | docker load
```

3. Deploy manifests:
```bash
kubectl apply -f deployment/kubernetes/
```

### 3. Offline/Air-Gapped Installation

#### System Requirements

- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+) or macOS 11+
- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **Disk Space**: 10GB minimum, 20GB recommended
- **RAM**: 4GB minimum, 8GB recommended (16GB+ for 13B models)
- **CPU**: Modern multi-core CPU with AVX2 support (for LLM inference)
- **Network**: Not required for air-gapped deployment

#### Installation Steps

1. Prepare installation package on connected system:
```bash
# Clone repository
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp

# Download Python dependencies as wheels
pip download -r requirements.txt -d wheels/

# Package everything
tar czf accelerapp-airgap.tar.gz \
    src/ \
    deployment/ \
    wheels/ \
    requirements.txt \
    setup.py \
    README.md
```

2. Transfer `accelerapp-airgap.tar.gz` to air-gapped system

3. Extract and install:
```bash
tar xzf accelerapp-airgap.tar.gz
cd Accelerapp
sudo bash deployment/install/install-airgap.sh
```

4. Download and transfer Ollama models:

On connected system:
```bash
# Pull models
ollama pull codellama:7b
ollama pull llama2:7b

# Export models
ollama list
# Copy models from ~/.ollama/models/
```

Transfer models to air-gapped system's `~/.ollama/models/` directory.

## Configuration

### Environment Variables

- `ACCELERAPP_MODE`: Deployment mode (development, production)
- `OLLAMA_HOST`: Ollama service URL (default: http://localhost:11434)
- `ACCELERAPP_MODELS_DIR`: Directory for storing models
- `ACCELERAPP_CACHE_DIR`: Directory for caching data

### Air-Gap Configuration

Create `config/airgap/settings.yaml`:

```yaml
airgap:
  enabled: true
  offline_mode: true
  
llm:
  backend: ollama
  base_url: http://localhost:11434
  default_model: codellama:7b
  fallback_models:
    - llama2:7b
    - mistral:7b

communication:
  message_bus:
    type: local  # local, redis
    max_queue_size: 1000
  
storage:
  models_dir: /app/models
  cache_dir: /app/cache
  output_dir: /app/output
```

## Monitoring and Health Checks

### Manual Health Check

```bash
# Run health check script
python deployment/monitoring/health_check.py

# Check service status
systemctl status accelerapp  # For systemd installation

# Docker health check
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Automated Monitoring

Health check endpoints are available at:

- `http://localhost:8080/health` - Overall health status
- `http://localhost:8080/metrics` - System metrics

### Logs

- Docker: `docker logs accelerapp-main`
- Systemd: `journalctl -u accelerapp -f`
- Files: `/var/log/accelerapp/`

## Resource Requirements

### Minimum Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Accelerapp | 1 core | 2GB | 5GB |
| Ollama (7B model) | 2 cores | 8GB | 4GB |
| Total | 2 cores | 10GB | 10GB |

### Recommended Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Accelerapp | 2 cores | 4GB | 10GB |
| Ollama (13B model) | 4 cores | 16GB | 8GB |
| Total | 4 cores | 20GB | 20GB |

### GPU Requirements (Optional)

For faster inference:
- NVIDIA GPU with 8GB+ VRAM
- CUDA 11.8+ drivers
- nvidia-docker runtime

## Troubleshooting

### Common Issues

1. **Ollama not accessible**
   - Check if Ollama service is running: `curl http://localhost:11434/api/tags`
   - Verify firewall rules
   - Check OLLAMA_HOST environment variable

2. **Out of memory errors**
   - Reduce model size (use 7B instead of 13B)
   - Increase system RAM
   - Enable swap space

3. **Slow generation**
   - Use GPU acceleration if available
   - Reduce max_tokens parameter
   - Use smaller models

4. **Permission denied errors**
   - Check directory permissions
   - Run as appropriate user (accelerapp user for systemd)
   - Verify volume mounts (Docker/K8s)

### Support

For issues and support:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: See README.md in project root

## Security Considerations

### Air-Gapped Security

1. **Network Isolation**
   - Ensure no external network access
   - Use internal DNS only
   - Firewall rules to block outbound traffic

2. **Access Control**
   - Run services as non-root user
   - Use RBAC for Kubernetes
   - Implement authentication for API endpoints

3. **Data Security**
   - Encrypt sensitive configuration
   - Use secrets management
   - Regular security audits

4. **Updates and Patches**
   - Plan for offline update process
   - Maintain security patches locally
   - Version control all configurations

## Maintenance

### Backup

```bash
# Backup models
tar czf models-backup.tar.gz /app/models

# Backup cache and configurations
tar czf config-backup.tar.gz /app/cache /app/config

# Backup generated output
tar czf output-backup.tar.gz /app/output
```

### Updates

For air-gapped updates:

1. Prepare update package on connected system
2. Transfer to air-gapped environment
3. Stop services
4. Apply updates
5. Restart services
6. Verify health

### Model Management

```bash
# List installed models
ollama list

# Remove unused models
ollama rm <model-name>

# Check model disk usage
du -sh ~/.ollama/models/
```

## License

MIT License - See LICENSE file in project root

---

**Last Updated**: 2025-10-14 | **Version**: 1.0.0 | **Deployment Status**: Production Ready
