# Getting Started with Accelerapp

Accelerapp is a next-generation platform for generating hardware control firmware, software SDKs, and user interfaces using advanced agentic coding swarms and emerging technologies.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp
pip install -e .
```

## Quick Start

### 1. Create a Configuration File

Generate a sample configuration file:

```bash
accelerapp init my_device.yaml
```

This creates a YAML file with sample hardware specifications that you can customize.

### 2. Edit Your Configuration

Open `my_device.yaml` and modify it to match your hardware:

```yaml
device_name: "My Custom Device"
platform: "arduino"
software_language: "python"
ui_framework: "react"

peripherals:
  - type: "led"
    pin: 13
    description: "Status LED"
```

### 3. Generate Your Code

Generate the complete stack (firmware, software, and UI):

```bash
accelerapp generate my_device.yaml --output ./output
```

Or generate specific components:

```bash
# Firmware only
accelerapp generate my_device.yaml --firmware-only

# Software SDK only
accelerapp generate my_device.yaml --software-only

# UI only
accelerapp generate my_device.yaml --ui-only
```

## What Gets Generated

### Firmware
- Platform-specific embedded code (Arduino, STM32, ESP32)
- Peripheral drivers
- Configuration headers
- Build-ready project structure

### Software SDK
- Python, C++, or JavaScript libraries
- Serial communication handling
- Device control API
- Example usage code

### User Interface
- React, Vue, or HTML-based control panel
- Real-time device monitoring
- Interactive controls for peripherals
- Ready-to-deploy web application

## Examples

Check out the `examples/` directory for pre-configured projects:

- `arduino_led.yaml` - Simple LED controller
- `sensor_array.yaml` - Multi-sensor data acquisition
- `motor_controller.yaml` - DC motor control system

## Next Steps

- Read the [Architecture Guide](ARCHITECTURE.md)
- Learn about [Configuration Options](CONFIGURATION.md)
- Explore [Advanced Features](ADVANCED.md)
