# Air-Gapped Deployment Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0 | **Status**: Production Ready

This directory contains configuration files for running Accelerapp in air-gapped (offline) environments.

## Overview

Accelerapp can operate entirely offline using local LLM models and autonomous agent collaboration. This enables secure, air-gapped code generation for sensitive environments without any external network dependencies.

## Features

### 1. Local LLM Integration
- **Ollama Support**: Run code generation models locally
- **Multiple Backends**: Support for Ollama, LocalAI, and llama.cpp
- **Model Management**: Download and manage models offline
- **Fallback System**: Automatic fallback to alternative models

### 2. Agent-to-Agent Communication
- **Message Bus**: Internal pub/sub messaging without external dependencies
- **Coordination**: Central agent coordinator for task distribution
- **Shared Context**: Thread-safe shared state across agents
- **Collaboration Protocols**: Predefined interaction patterns

### 3. Offline Knowledge Management
- **Knowledge Base**: Local vector database for code patterns
- **Template System**: Versioned code templates with optimization
- **Pattern Learning**: Analyze generated code for improvements
- **Offline Docs**: Searchable local documentation

### 4. Security Hardening
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete operation logs for compliance
- **Encryption**: Secure storage for sensitive data
- **Network Isolation**: Enforced offline operation

## Configuration

### Main Configuration File

Edit `config/airgap/settings.yaml` to customize your deployment:

```yaml
airgap:
  enabled: true
  offline_mode: true
  strict_mode: false

llm:
  backend: ollama
  base_url: http://localhost:11434
  default_model: codellama:7b
```

### Environment Variables

Override settings with environment variables:

```bash
export ACCELERAPP_AIRGAP_ENABLED=true
export ACCELERAPP_LLM_BACKEND=ollama
export ACCELERAPP_LLM_MODEL=codellama:7b
```

## Quick Start

### 1. Install Accelerapp

```bash
# See deployment/README.md for installation options
sudo bash deployment/install/install-airgap.sh
```

### 2. Install and Configure Ollama

```bash
# Install Ollama (on a connected system first)
curl https://ollama.ai/install.sh | sh

# Pull required models
ollama pull codellama:7b
ollama pull llama2:7b

# For air-gapped: Copy ~/.ollama/models to target system
```

### 3. Configure Accelerapp

```bash
# Copy air-gap config
cp config/airgap/settings.yaml ~/.accelerapp/config.yaml

# Edit as needed
vim ~/.accelerapp/config.yaml
```

### 4. Verify Installation

```bash
# Check health
accelerapp info

# Run health check
python deployment/monitoring/health_check.py
```

### 5. Generate Code

```bash
# Create project config
accelerapp init mydevice.yaml

# Generate firmware, software, and UI
accelerapp generate mydevice.yaml --output ./output
```

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│                  Accelerapp Core                     │
├─────────────────────────────────────────────────────┤
│  CLI │ Core Orchestration │ Generators              │
└──┬───────────────┬───────────────────────┬──────────┘
   │               │                       │
┌──▼───────────┐ ┌─▼──────────────┐ ┌─────▼────────┐
│ LLM Module   │ │ Communication  │ │  Knowledge   │
│              │ │                │ │              │
│ • Ollama     │ │ • Message Bus  │ │ • Templates  │
│ • LocalAI    │ │ • Coordinator  │ │ • Patterns   │
│ • llama.cpp  │ │ • Shared Ctx   │ │ • Docs       │
└──────────────┘ └────────────────┘ └──────────────┘
```

### Data Flow

1. **User Request** → CLI parses config
2. **Core Orchestration** → Routes to generators
3. **Generator** → Uses LLM service for code generation
4. **LLM Service** → Calls local Ollama/LocalAI
5. **Communication** → Agents coordinate via message bus
6. **Knowledge** → Templates and patterns enhance output
7. **Output** → Generated firmware/software/UI code

## Advanced Configuration

### Multi-Model Setup

Configure different models for different tasks:

```yaml
llm:
  models:
    firmware:
      model: codellama:7b
      temperature: 0.5
    software:
      model: codellama:13b
      temperature: 0.7
    ui:
      model: llama2:7b
      temperature: 0.8
```

### Custom Templates

Add custom code templates:

```python
from accelerapp.knowledge import TemplateManager, Template, TemplateCategory

tm = TemplateManager()
template = Template(
    id="custom-firmware",
    name="Custom Firmware Template",
    category=TemplateCategory.FIRMWARE,
    content="void setup() { {{init_code}} }",
    variables=["init_code"]
)
tm.add_template(template)
```

### Pattern Learning

Enable pattern learning for continuous improvement:

```yaml
knowledge:
  patterns:
    enable_learning: true
    min_frequency: 3
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   systemctl restart ollama
   ```

2. **Model Not Found**
   ```bash
   # List available models
   ollama list
   
   # Pull missing model
   ollama pull codellama:7b
   ```

3. **Permission Denied**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER ~/.accelerapp
   ```

4. **Out of Memory**
   - Use smaller models (7B instead of 13B/34B)
   - Reduce max_tokens in config
   - Add swap space if needed

### Diagnostic Commands

```bash
# System health check
python deployment/monitoring/health_check.py

# Check disk space
df -h ~/.accelerapp

# View logs
tail -f ~/.accelerapp/logs/accelerapp.log

# Test LLM connection
curl http://localhost:11434/api/generate -d '{
  "model": "codellama:7b",
  "prompt": "Write a hello world in C"
}'
```

## Security Best Practices

### Network Isolation

1. **Firewall Configuration**
   ```bash
   # Block all outbound traffic except local
   sudo ufw deny out
   sudo ufw allow out to 127.0.0.1
   sudo ufw allow out to 172.16.0.0/12
   ```

2. **DNS Configuration**
   - Use only internal DNS
   - Disable public DNS servers

3. **Air-Gap Verification**
   ```bash
   # Test network isolation
   ping -c 1 8.8.8.8  # Should fail
   curl https://google.com  # Should fail
   ```

### Access Control

Enable authentication and RBAC:

```yaml
security:
  authentication:
    enabled: true
    method: local
  access_control:
    enabled: true
    default_role: developer
```

### Audit Logging

Review audit logs regularly:

```bash
# View recent security events
tail -f ~/.accelerapp/logs/audit.log

# Search for failed access attempts
grep "success.*false" ~/.accelerapp/logs/audit.log
```

## Performance Optimization

### Hardware Recommendations

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| CPU | 4 cores | 8 cores | 16+ cores |
| RAM | 8GB | 16GB | 32GB+ |
| Storage | 50GB SSD | 100GB SSD | 500GB+ NVMe |
| GPU | None | 8GB VRAM | 16GB+ VRAM |

### Model Selection

Choose models based on your hardware:

- **7B models**: Entry-level, 8GB RAM minimum
- **13B models**: Mid-range, 16GB RAM recommended
- **34B models**: High-end, 32GB+ RAM + GPU

### Caching

Enable caching for faster repeated operations:

```yaml
performance:
  enable_cache: true
  cache_ttl: 3600
```

## Backup and Recovery

### Backup Strategy

```bash
# Backup models
tar czf models-backup.tar.gz ~/.accelerapp/models/

# Backup knowledge base
tar czf knowledge-backup.tar.gz ~/.accelerapp/knowledge/

# Backup templates
tar czf templates-backup.tar.gz ~/.accelerapp/templates/

# Backup configurations
tar czf config-backup.tar.gz ~/.accelerapp/config/
```

### Recovery

```bash
# Restore from backup
tar xzf models-backup.tar.gz -C ~/
tar xzf knowledge-backup.tar.gz -C ~/
tar xzf templates-backup.tar.gz -C ~/
tar xzf config-backup.tar.gz -C ~/
```

## Monitoring

### Health Checks

Automated health monitoring:

```bash
# Run health check
python deployment/monitoring/health_check.py

# Check exit code
echo $?  # 0=healthy, 1=unhealthy, 2=degraded
```

### Metrics

Key metrics to monitor:

- LLM response time
- Agent task completion rate
- Memory usage
- Disk space
- Cache hit rate

## Support

For issues and questions:

- Documentation: See main README.md
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Deployment Guide: See deployment/README.md
- Security: See SECURITY.md

## License

MIT License - See LICENSE file in project root

---

**Last Updated**: 2025-10-14 | **Version**: 1.0.0 | **Deployment Type**: Air-Gapped/Offline
