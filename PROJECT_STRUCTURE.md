# Accelerapp Project Structure

```
Accelerapp/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history and changes
├── CONTRIBUTING.md              # Contribution guidelines
├── DEMO.md                      # Interactive demo guide
├── MANIFEST.in                  # Package manifest
├── setup.py                     # Python package setup
├── requirements.txt             # Project dependencies
├── .gitignore                   # Git ignore patterns
│
├── src/accelerapp/              # Main source code
│   ├── __init__.py             # Package initialization
│   ├── core.py                 # Core orchestration system
│   ├── cli.py                  # Command-line interface
│   │
│   ├── agents/                 # Agentic coding swarm
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Abstract agent base class
│   │   └── orchestrator.py     # Agent coordination system
│   │
│   ├── firmware/               # Firmware generation
│   │   ├── __init__.py
│   │   └── generator.py        # Firmware code generator
│   │
│   ├── software/               # Software SDK generation
│   │   ├── __init__.py
│   │   └── generator.py        # Multi-language SDK generator
│   │
│   ├── ui/                     # User interface generation
│   │   ├── __init__.py
│   │   └── generator.py        # Multi-framework UI generator
│   │
│   ├── config/                 # Configuration management (future)
│   └── templates/              # Code templates (future)
│       └── firmware/
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_core.py           # Core functionality tests
│   ├── test_agents.py         # Agent system tests
│   └── test_generators.py    # Generator tests
│
├── examples/                   # Example configurations
│   ├── arduino_led.yaml       # Arduino LED controller
│   ├── sensor_array.yaml      # ESP32 sensor array
│   └── motor_controller.yaml  # STM32 motor controller
│
└── docs/                       # Documentation
    ├── GETTING_STARTED.md     # Quick start guide
    ├── ARCHITECTURE.md        # System architecture
    └── CONFIGURATION.md       # Configuration reference
```

## Module Overview

### Core Modules

#### `src/accelerapp/core.py`
Main orchestration system that:
- Loads hardware specifications from YAML
- Coordinates firmware, software, and UI generation
- Manages output directory structure
- Provides high-level generation API

#### `src/accelerapp/cli.py`
Command-line interface providing:
- `init` - Create sample configurations
- `generate` - Generate complete stacks
- `info` - Display platform information
- Component-specific generation options

### Agent System

#### `src/accelerapp/agents/base_agent.py`
Abstract base class defining:
- Agent capabilities and interfaces
- Code generation contract
- Action logging system
- Task compatibility checking

#### `src/accelerapp/agents/orchestrator.py`
Swarm coordinator that:
- Registers and manages agents
- Routes tasks to appropriate agents
- Coordinates multi-agent workflows
- Tracks agent status and history

### Generators

#### `src/accelerapp/firmware/generator.py`
Generates embedded firmware:
- **Platforms**: Arduino, STM32, ESP32
- **Output**: C/C++ source files
- **Features**: Peripheral drivers, config headers, main loop

#### `src/accelerapp/software/generator.py`
Generates software SDKs:
- **Languages**: Python, C++, JavaScript
- **Output**: Libraries and examples
- **Features**: Serial communication, device APIs

#### `src/accelerapp/ui/generator.py`
Generates user interfaces:
- **Frameworks**: React, Vue, HTML
- **Output**: Complete web applications
- **Features**: Responsive design, real-time control

## Generated Output Structure

When you run `accelerapp generate config.yaml --output ./output`, it creates:

```
output/
├── firmware/                   # Embedded firmware
│   ├── main.{ino|c}           # Main program
│   ├── config.h               # Configuration header
│   └── {peripheral}.{c|h}     # Peripheral drivers
│
├── software/                  # Software SDK
│   ├── {device}_sdk.{py|cpp|js}  # SDK implementation
│   ├── {device}.h             # Header file (C++)
│   ├── example.py             # Usage example (Python)
│   ├── requirements.txt       # Dependencies (Python)
│   └── package.json           # Dependencies (JS)
│
└── ui/                        # User interface
    ├── App.{jsx|vue|html}     # Main application
    ├── App.css                # Styles
    ├── index.html             # HTML entry point
    ├── index.js               # JS entry point (React)
    ├── package.json           # Dependencies (React/Vue)
    └── README.md              # UI documentation
```

## Key Features by Module

### Core System
- YAML configuration parsing
- Multi-component orchestration
- Error handling and reporting
- Output directory management

### Agent System
- Capability-based routing
- Task coordination
- Action history tracking
- Extensible architecture

### Firmware Generator
- Multi-platform support
- Peripheral abstraction
- Template-based generation
- Configuration management

### Software Generator
- Multi-language SDKs
- Serial communication
- Device abstraction
- Example generation

### UI Generator
- Multi-framework support
- Responsive design
- Component generation
- Build configuration

## Technology Stack

- **Language**: Python 3.8+
- **CLI Framework**: Click
- **Templating**: Jinja2 (for future template expansion)
- **Configuration**: YAML + Pydantic
- **Testing**: pytest
- **Generated Languages**: C/C++, Python, JavaScript

## Future Additions

### Planned Directories
- `src/accelerapp/templates/` - Jinja2 templates
- `src/accelerapp/plugins/` - Plugin system
- `src/accelerapp/validators/` - Configuration validators
- `benchmarks/` - Performance benchmarks
- `integration_tests/` - Integration test suite

### Planned Features
- LLM integration for intelligent generation
- Template marketplace
- Visual configuration builder
- Hardware-in-the-loop testing
- Cloud-based generation service

## Getting Started

1. **Install**: `pip install -e .`
2. **Create Config**: `accelerapp init my_device.yaml`
3. **Generate**: `accelerapp generate my_device.yaml`
4. **Deploy**: Use generated firmware, SDK, and UI

For more details, see [GETTING_STARTED.md](docs/GETTING_STARTED.md).
