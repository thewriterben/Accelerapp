# Accelerapp

<div align="center">

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/thewriterben/Accelerapp/releases)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-438%2B%20passing-brightgreen.svg)](#testing-and-quality)
[![Production Ready](https://img.shields.io/badge/production-ready-brightgreen.svg)](#production-ready-status)

**Next-Generation IoT Development Platform**

*Multi-Agent AI • Zero-Trust Security • Air-Gapped Deployment • TinyML Integration • Digital Twin Platform*

[Quick Start](#quick-start) • [Documentation](#documentation) • [Features](#key-features) • [Examples](#examples)

</div>

---

## Overview

**Accelerapp** is a production-ready, enterprise-grade IoT development platform that generates complete hardware control systems including firmware, software SDKs, and user interfaces. Powered by advanced multi-agent AI systems and featuring zero-trust security with post-quantum cryptography, Accelerapp enables rapid development of sophisticated IoT solutions from simple YAML specifications.

### What Makes Accelerapp Unique

- 🤖 **Multi-Agent AI System**: Intelligent orchestration of specialized code generation agents
- 🔒 **Zero-Trust Security**: Post-quantum cryptography (Kyber-768, Dilithium-3) and continuous authentication
- 🌐 **Air-Gapped Operations**: Complete offline code generation with local LLMs (Ollama, LocalAI)
- 🧠 **TinyML & Edge AI**: On-device machine learning with model optimization and federated learning
- 👥 **Digital Twin Platform**: Real-time virtual replicas with blockchain-verifiable audit trails
- 🎯 **Multi-Platform Support**: Arduino, ESP32, STM32, Nordic, Raspberry Pi, and more
- 🏢 **Enterprise Ready**: Multi-tenancy, RBAC, audit logging, and comprehensive monitoring
- ✅ **Production Quality**: 438+ tests ensuring reliability and performance

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Platform Support](#platform-support)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Enterprise Capabilities](#enterprise-capabilities)
- [Security Architecture](#security-architecture)
- [Deployment Options](#deployment-options)
- [Testing and Quality](#testing-and-quality)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

### 🤖 Multi-Agent AI Code Generation

Accelerapp employs a sophisticated multi-agent system where specialized AI agents collaborate to generate optimized code:

- **Firmware Agent**: Hardware-specific embedded code generation
- **Software Agent**: SDK and API generation for multiple languages
- **UI Agent**: User interface generation for web and mobile
- **TinyML Agent**: Edge AI and machine learning integration
- **Agent Coordinator**: Intelligent task orchestration with multiple strategies

```yaml
# Simple YAML specification
device_name: "Smart Sensor"
platform: "esp32"
peripherals:
  - type: "temperature_sensor"
    pin: 4
  - type: "led"
    pin: 13
```

**→** Generates complete firmware, Python SDK, and React UI

### 🔒 Zero-Trust Hardware Security

Enterprise-grade security built into every generated system:

- **Cryptographic Device Identities**: Unique PKI-based identities for every device
- **Continuous Authentication**: Real-time behavioral analysis with dynamic trust scoring
- **Post-Quantum Cryptography**: Kyber-768 (key exchange) and Dilithium-3 (signatures)
- **Hybrid Cryptography**: Combined classical and post-quantum algorithms
- **Micro-Segmented Networks**: Isolated communication channels with fine-grained policies
- **Automated Incident Response**: Device isolation and credential rotation

📖 [Zero-Trust Architecture Documentation](docs/ZERO_TRUST_ARCHITECTURE.md)

### 🌐 Air-Gapped Deployment

Complete offline operation for secure, isolated environments:

- **Local LLM Integration**: Ollama, LocalAI, llama.cpp support
- **Multi-Agent Communication**: Internal messaging without external dependencies
- **Knowledge Base Management**: Offline code templates and patterns
- **Autonomous Generation**: Self-hosted code generation pipeline
- **Zero External Dependencies**: No internet connection required

```bash
# Install for air-gapped deployment
sudo bash deployment/install/install-airgap.sh

# Generate code offline
accelerapp generate device.yaml --offline
```

📖 [Air-Gapped Deployment Guide](config/airgap/README.md) • [Implementation Summary](AIRGAP_FEATURES.md)

### 🧠 TinyML & Edge AI Integration

On-device machine learning for intelligent embedded systems:

- **Neural Network Inference**: Optimized inference code for microcontrollers
- **Model Optimization**: Quantization (int8), pruning, knowledge distillation
- **Federated Learning**: Privacy-preserving distributed learning
- **Adaptive Behavior**: Online learning and environment adaptation
- **Multi-Framework Support**: TensorFlow Lite, Edge Impulse, CMSIS-NN

```python
ml_config = {
    "task": "inference",
    "model": "temperature_prediction.tflite",
    "optimization": "int8_quantization",
    "target_platform": "esp32"
}
```

📖 [TinyML Implementation](TINYML_IMPLEMENTATION_SUMMARY.md) • [Integration Guide](docs/TINYML_INTEGRATION.md)

### 👥 Digital Twin Platform

Real-time virtual replicas of physical hardware:

- **Live State Synchronization**: Real-time monitoring and control
- **Blockchain Audit Trails**: Verifiable hardware operation logs
- **REST API**: Complete remote management interface
- **AR/VR Integration**: Immersive hardware control interfaces
- **Device Simulation**: Test before physical deployment

```python
from accelerapp.digital_twin import DigitalTwinManager

manager = DigitalTwinManager()
twin = manager.create_twin("device_001", device_config)
twin.update_pin_state(13, True)  # Control remotely
```

📖 [Digital Twin Features](DIGITAL_TWIN_FEATURES.md)

### 🎯 Comprehensive Platform Support

| Platform | Firmware | SDK | Status |
|----------|----------|-----|--------|
| Arduino (Uno, Mega, Nano) | ✅ | ✅ | Production |
| ESP32 / ESP8266 | ✅ | ✅ | Production |
| STM32 (F4, H7) | ✅ | ✅ | Production |
| Nordic (nRF52, nRF53) | ✅ | ✅ | Production |
| Raspberry Pi Pico | ✅ | ✅ | Production |
| Raspberry Pi (Linux) | ✅ | ✅ | Production |
| Meshtastic | ✅ | ✅ | Production |
| Generic MicroPython | ✅ | ✅ | Production |

**Software SDKs**: Python, JavaScript/Node.js, C/C++, Rust  
**UI Frameworks**: React, Vue.js, Angular, React Native

---

## Architecture

Accelerapp is built on a modern, layered architecture designed for scalability and extensibility:

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   CLI/UI     │  │   Examples   │  │  Integration    │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Hardware    │  │   AI Agent   │  │   Workflow      │  │
│  │   Service     │  │   Service    │  │   Service       │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Security    │  │   Digital    │  │   Knowledge     │  │
│  │   Service     │  │   Twin       │  │   Base          │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                       Core Layer                             │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Dependency  │  │   Config     │  │   Event Bus     │  │
│  │   Injection   │  │   Manager    │  │   System        │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

- **Multi-Agent AI System**: Coordinated code generation with specialized agents
- **Hardware Abstraction Layer**: Unified API for diverse hardware platforms
- **Template Engine**: Jinja2-based code generation with platform-specific templates
- **Security Engine**: Zero-trust implementation with post-quantum cryptography
- **Digital Twin Manager**: Real-time device state management
- **Knowledge Base**: Offline code patterns and templates
- **Local LLM Service**: Air-gapped AI code generation

📖 [Architecture Documentation](ARCHITECTURE.md) • [V2.0 Enhancements](V2.0_ARCHITECTURE_SUMMARY.md)

---

## Platform Support

### Embedded Platforms

**Arduino Family**
- Arduino Uno, Mega, Nano, Due
- Platform-specific optimizations
- Hardware abstraction layer

**ESP32/ESP8266**
- WiFi and Bluetooth integration
- FreeRTOS support
- OTA firmware updates

**STM32**
- F4 and H7 series support
- HAL code generation
- CubeMX integration
- Advanced peripherals (DMA, timers, ADC)

**Nordic Semiconductor**
- nRF52 and nRF53 series
- Bluetooth Low Energy (BLE) stack
- Zephyr RTOS integration
- Thread networking

**Raspberry Pi**
- Raspberry Pi Pico (RP2040)
- Raspberry Pi 3/4/5 (Linux)
- GPIO, I2C, SPI support

**Meshtastic**
- LoRa mesh networking
- Remote firmware management
- OTA updates

### Software Platforms

- **Python**: Full-featured SDK with async support
- **JavaScript/Node.js**: Cross-platform SDK
- **C/C++**: Native performance libraries
- **Rust**: Memory-safe embedded systems
- **React**: Modern web UI components
- **React Native**: Cross-platform mobile apps

---

## Installation

### Method 1: Install from PyPI

```bash
pip install accelerapp
```

### Method 2: Install from Source

```bash
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp
pip install -e .
```

### Method 3: Docker Deployment

```bash
cd deployment/docker
docker-compose up -d
```

### Method 4: Kubernetes Deployment

```bash
kubectl apply -f deployment/kubernetes/
```

### Method 5: Air-Gapped Installation

```bash
# On connected system: package dependencies
pip download accelerapp -d ./packages

# Transfer to air-gapped system, then:
cd packages
pip install --no-index --find-links . accelerapp

# Install Ollama for local LLM
curl https://ollama.ai/install.sh | sh
ollama pull codellama:7b
```

📖 [Deployment Guide](deployment/README.md) • [Air-Gap Setup](config/airgap/README.md)

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Docker for containerized deployment
- (Optional) Ollama for air-gapped AI features

---

## Quick Start

### 1. Initialize a New Project

```bash
accelerapp init my_device.yaml
```

This creates a sample YAML configuration file.

### 2. Configure Your Hardware

Edit `my_device.yaml`:

```yaml
device_name: "Smart LED Controller"
platform: "esp32"
software_language: "python"
ui_framework: "react"

peripherals:
  - type: "led"
    pin: 13
    color: "blue"
    description: "Status LED"
  
  - type: "button"
    pin: 2
    pull_up: true
    description: "Control button"
```

### 3. Generate Complete System

```bash
accelerapp generate my_device.yaml --output ./output
```

This generates:
- ✅ ESP32 firmware (C++)
- ✅ Python SDK with async support
- ✅ React web interface
- ✅ API documentation
- ✅ Build scripts and configuration

### 4. Build and Deploy

```bash
cd output/firmware
pio run --target upload  # Upload firmware

cd ../software
pip install -e .          # Install SDK

cd ../ui
npm install && npm start  # Run web UI
```

📖 [Getting Started Guide](docs/GETTING_STARTED.md) • [Configuration Reference](docs/CONFIGURATION.md)

---

## Usage Examples

### Basic LED Control

```yaml
device_name: "LED Blinker"
platform: "arduino"

peripherals:
  - type: "led"
    pin: 13
```

```bash
accelerapp generate led_blinker.yaml
```

### Multi-Sensor IoT Device

```yaml
device_name: "Environmental Monitor"
platform: "esp32"
connectivity:
  wifi:
    ssid: "your_network"
  mqtt:
    broker: "mqtt.example.com"

peripherals:
  - type: "temperature_sensor"
    pin: 4
    model: "DHT22"
  
  - type: "light_sensor"
    pin: 34
    
  - type: "oled_display"
    i2c_address: 0x3C
```

### TinyML Integration

```yaml
device_name: "Smart Predictor"
platform: "esp32"

ml_config:
  task: "inference"
  model: "models/temperature_prediction.tflite"
  optimization: "int8_quantization"
  framework: "tflite"

peripherals:
  - type: "temperature_sensor"
    pin: 4
```

### Air-Gapped Generation

```bash
# Configure for offline operation
export ACCELERAPP_AIRGAP_ENABLED=true
export ACCELERAPP_LLM_BACKEND=ollama
export ACCELERAPP_LLM_MODEL=codellama:7b

# Generate without internet
accelerapp generate device.yaml --offline
```

📖 [Example Gallery](examples/) • [Demo Scripts](DEMO.md)

---

## Advanced Features

### Multi-Agent Code Generation

Leverage specialized AI agents for optimal code quality:

```python
from accelerapp.agents import AgentCoordinator, CoordinationStrategy

coordinator = AgentCoordinator()
coordinator.set_strategy(CoordinationStrategy.SEQUENTIAL)

# Register specialized agents
coordinator.register_agent("firmware-agent", "Firmware Generator", ["firmware"])
coordinator.register_agent("software-agent", "SDK Generator", ["software"])
coordinator.register_agent("ui-agent", "UI Generator", ["ui"])

# Execute coordinated generation
result = coordinator.execute_workflow(hardware_spec)
```

### Digital Twin Management

```python
from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer

# Create and manage digital twins
manager = DigitalTwinManager()
twin = manager.create_twin("device_001", {
    "type": "ESP32",
    "firmware_version": "1.0.0"
})

# Real-time state updates
twin.update_pin_state(13, True)
twin.update_metadata("temperature", 25.5)

# Visualization
visualizer = TwinVisualizer(manager)
dashboard = visualizer.get_device_dashboard("device_001")
```

### Custom Platform Integration

```python
from accelerapp.platforms import PlatformBase

class CustomPlatform(PlatformBase):
    def get_platform_name(self) -> str:
        return "custom_mcu"
    
    def generate_initialization_code(self) -> str:
        return "// Custom initialization"
    
    def supports_peripheral(self, peripheral_type: str) -> bool:
        return peripheral_type in ["gpio", "uart", "i2c"]

# Register platform
from accelerapp.platforms import register_platform
register_platform("custom", CustomPlatform)
```

### Knowledge Base Management

```python
from accelerapp.knowledge import TemplateManager, Template, TemplateCategory

tm = TemplateManager()
template = Template(
    id="custom-firmware",
    name="Custom Template",
    category=TemplateCategory.FIRMWARE,
    content="void setup() { {{init_code}} }",
    variables=["init_code"]
)
tm.add_template(template)
```

📖 [Advanced Usage Guide](docs/CONFIGURATION.md) • [API Reference](docs/API_TINYML.md)

---

## Enterprise Capabilities

### Multi-Tenancy Support

Serve multiple clients from a single instance with complete isolation:

- Tenant-isolated data and configurations
- Per-tenant resource quotas
- Centralized management console
- Audit logging per tenant

### Role-Based Access Control (RBAC)

Granular permission system:

- **Admin**: Full system access
- **Developer**: Code generation and deployment
- **Operator**: Monitor and manage devices
- **Viewer**: Read-only access

### Audit Logging

Comprehensive activity tracking:

- All code generation operations
- Configuration changes
- Device deployments
- Security events

### Monitoring and Observability

Enterprise-grade monitoring:

- Prometheus metrics export
- Grafana dashboards
- Health check endpoints
- Performance profiling
- Real-time alerting

```bash
# Run health check
python deployment/monitoring/health_check.py

# View metrics
curl http://localhost:9090/metrics
```

📖 [Operations Guide](docs/OPERATIONS.md) • [Performance Tuning](docs/PERFORMANCE_TUNING.md)

---

## Security Architecture

### Zero-Trust Implementation

**Principle**: Never trust, always verify

```python
from accelerapp.security import (
    DeviceIdentityManager,
    ZeroTrustPolicy,
    BehavioralAnalysis
)

# Device identity
identity_manager = DeviceIdentityManager()
identity = identity_manager.create_identity(device_info)

# Continuous authentication
policy = ZeroTrustPolicy(min_trust_score=0.7)
behavior = BehavioralAnalysis()
trust_score = behavior.calculate_trust_score(device_id, metrics)

# Micro-segmentation
if trust_score >= policy.min_trust_score:
    allow_communication(device_id)
else:
    isolate_device(device_id)
```

### Post-Quantum Cryptography

Future-proof security against quantum computing threats:

- **Kyber-768**: Post-quantum key encapsulation
- **Dilithium-3**: Post-quantum digital signatures
- **Hybrid Mode**: Combined classical and PQC algorithms
- **NIST Standards**: Compliant with latest PQC standards

### Security Features

- ✅ Hardware-based device identities
- ✅ Mutual TLS (mTLS) authentication
- ✅ Certificate rotation and revocation
- ✅ Encrypted data at rest and in transit
- ✅ Secure boot and firmware verification
- ✅ Runtime integrity monitoring
- ✅ Automated incident response

📖 [Zero-Trust Architecture](docs/ZERO_TRUST_ARCHITECTURE.md) • [Security Guide](SECURITY.md) • [Quick Start](docs/ZERO_TRUST_QUICKSTART.md)

---

## Deployment Options

### Local Development

```bash
# Install and run locally
pip install -e .
accelerapp generate device.yaml
```

### Docker Containers

```bash
# Using Docker Compose
cd deployment/docker
docker-compose up -d

# Or standalone
docker run -p 8000:8000 accelerapp:latest
```

### Kubernetes Cluster

```bash
# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/

# Helm chart
helm install accelerapp deployment/helm/accelerapp
```

### Air-Gapped Environment

```bash
# Complete offline installation
sudo bash deployment/install/install-airgap.sh

# Configure for offline operation
cp config/airgap/settings.yaml ~/.accelerapp/config.yaml

# Verify installation
accelerapp info
python deployment/monitoring/health_check.py
```

### Cloud Platforms

- **AWS**: ECS, EKS, EC2 support
- **Azure**: AKS, Container Instances
- **Google Cloud**: GKE, Cloud Run
- **On-Premises**: Kubernetes, Docker Swarm

📖 [Deployment Guide](deployment/README.md) • [Cost Optimization](docs/COST_OPTIMIZATION.md)

---

## Testing and Quality

### Comprehensive Test Coverage

**438+ Tests** ensuring production quality:

- ✅ Unit tests: Core functionality
- ✅ Integration tests: Component interaction
- ✅ Security tests: Vulnerability scanning
- ✅ Performance tests: Load and stress testing
- ✅ Platform tests: Hardware compatibility
- ✅ E2E tests: Complete workflows

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests
pytest -m security       # Security tests
pytest -m performance    # Performance tests

# With coverage report
pytest --cov=accelerapp --cov-report=html
```

### Quality Metrics

- **Code Coverage**: 71%+ across core modules
- **Test Pass Rate**: 100% (438/438 passing)
- **Performance**: <2s code generation for typical projects
- **Security**: Zero known vulnerabilities

### Continuous Integration

- Automated testing on every commit
- Multi-platform test matrix
- Security scanning (Bandit, Safety)
- Code quality checks (Black, Flake8, MyPy)
- Documentation validation

📖 [Testing Guide](TESTING.md) • [Testing Infrastructure](TESTING_INFRASTRUCTURE_SUMMARY.md) • [Quick Start](TESTING_QUICKSTART.md)

---

## Documentation

### Core Documentation

- **[Getting Started](docs/GETTING_STARTED.md)**: Installation and first steps
- **[Architecture](ARCHITECTURE.md)**: System design and components
- **[Configuration](docs/CONFIGURATION.md)**: YAML reference and examples
- **[API Reference](docs/API_TINYML.md)**: Complete API documentation

### Feature Documentation

- **[Air-Gapped Deployment](AIRGAP_FEATURES.md)**: Offline code generation
- **[TinyML Integration](TINYML_IMPLEMENTATION_SUMMARY.md)**: Edge AI features
- **[Digital Twin Platform](DIGITAL_TWIN_FEATURES.md)**: Virtual hardware replicas
- **[Zero-Trust Security](docs/ZERO_TRUST_ARCHITECTURE.md)**: Security architecture
- **[Meshtastic Integration](MESHTASTIC_INTEGRATION.md)**: LoRa mesh networking

### Operations

- **[Deployment Guide](deployment/README.md)**: Production deployment
- **[Operations Manual](docs/OPERATIONS.md)**: Day-to-day operations
- **[Performance Tuning](docs/PERFORMANCE_TUNING.md)**: Optimization guide
- **[Monitoring](docs/OPERATIONAL_PROCEDURES.md)**: Observability setup

### Guides

- **[Upgrade Guide](docs/UPGRADE_GUIDE.md)**: Version migration
- **[Contributing](CONTRIBUTING.md)**: Development guidelines
- **[Changelog](CHANGELOG.md)**: Version history
- **[Examples](examples/)**: Code examples and demos

---

## Production-Ready Status

Accelerapp v1.0.0 is **production-ready** and battle-tested:

✅ **438+ Tests** covering all critical functionality  
✅ **Enterprise Deployments** in secure environments  
✅ **Air-Gapped Operations** validated in isolated networks  
✅ **Multi-Platform Support** across 10+ hardware families  
✅ **Security Hardened** with zero-trust and post-quantum crypto  
✅ **Comprehensive Documentation** for all features  
✅ **Active Maintenance** with regular updates  
✅ **Professional Support** available for enterprise users

### Version History

- **v1.0.0** (Current): Production release with full feature set
- **v0.3.0**: Cloud services and marketplace
- **v0.2.0**: Air-gapped deployment and agent communication
- **v0.1.0**: Initial release with core generation

📖 [Release Notes](V2.0_RELEASE_NOTES.md) • [Changelog](CHANGELOG.md)

---

## Contributing

We welcome contributions from the community! Whether it's bug reports, feature requests, documentation improvements, or code contributions, your input is valued.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run code quality checks
black src tests
flake8 src tests
mypy src
```

### Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Write clear commit messages

📖 [Contributing Guide](CONTRIBUTING.md) • [Code of Conduct](CONTRIBUTING.md#code-of-conduct)

---

## Community and Support

### Get Help

- 📖 **Documentation**: [GitHub Wiki](https://github.com/thewriterben/Accelerapp)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thewriterben/Accelerapp/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/thewriterben/Accelerapp/issues)
- 📧 **Email**: thewriterben@protonmail.com

### Stay Connected

- ⭐ Star the repository to show your support
- 👀 Watch for updates and releases
- 🔀 Fork to create your own version

### Enterprise Support

Professional support available for enterprise deployments:
- Custom platform integration
- On-site training and consulting
- Priority bug fixes and features
- SLA guarantees

Contact: thewriterben@protonmail.com

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 The Writer Ben

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

### Compliance

- ✅ NIST Post-Quantum Cryptography Standards
- ✅ MIT License (permissive open source)
- ✅ Export compliance documentation available

📖 [Compliance Documentation](COMPLIANCE.md)

---

## Acknowledgments

Built with these excellent technologies:

- **Python** - Core language
- **Jinja2** - Template engine
- **Pydantic** - Data validation
- **Ollama** - Local LLM inference
- **Docker** - Containerization
- **Kubernetes** - Orchestration

Special thanks to all contributors and the open-source community!

---

<div align="center">

**[⬆ Back to Top](#accelerapp)**

Made with ❤️ by [The Writer Ben](https://github.com/thewriterben)

</div>