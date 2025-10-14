# Accelerapp Demo Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

This guide demonstrates the core capabilities of Accelerapp through practical examples.

## Setup

```bash
# Install Accelerapp
pip install -e .

# Verify installation
accelerapp --version
accelerapp info
```

## Demo 1: Arduino LED Controller

Generate a complete Arduino LED control system.

### Step 1: Create Configuration

```bash
# View the example configuration
cat examples/arduino_led.yaml
```

### Step 2: Generate Code

```bash
# Generate firmware, software SDK, and UI
accelerapp generate examples/arduino_led.yaml --output ./demo_led
```

### Step 3: Explore Generated Files

```bash
# View firmware
ls -la demo_led/firmware/
# Files: main.ino, config.h, led.c, led.h

# View Python SDK
ls -la demo_led/software/
# Files: arduino_led_controller_sdk.py, example.py, requirements.txt

# View React UI
ls -la demo_led/ui/
# Files: App.jsx, App.css, index.html, index.js, package.json
```

### Step 4: Use Generated Code

**Flash Firmware:**
```bash
# Open demo_led/firmware/main.ino in Arduino IDE and flash to board
```

**Use Python SDK:**
```bash
cd demo_led/software
pip install -r requirements.txt
python example.py
```

**Run UI:**
```bash
cd demo_led/ui
npm install
npm start
```

## Demo 2: ESP32 Sensor Array

Generate an ESP32-based multi-sensor data acquisition system.

### Generate System

```bash
accelerapp generate examples/sensor_array.yaml --output ./demo_sensors
```

### Key Features

- **WiFi-enabled firmware** for ESP32
- **Multiple sensor support** (temperature, humidity, pressure)
- **Real-time data streaming** via serial
- **Web dashboard** for monitoring

### Generated Components

1. **Firmware** (`demo_sensors/firmware/`)
   - ESP32-optimized C code
   - WiFi configuration
   - Sensor reading routines
   - JSON data formatting

2. **Python SDK** (`demo_sensors/software/`)
   - Async serial communication
   - Data parsing and validation
   - Connection management

3. **React UI** (`demo_sensors/ui/`)
   - Real-time sensor graphs
   - Connection status indicator
   - Data export functionality

## Demo 3: STM32 Motor Controller

Generate a professional motor control system for STM32.

### Generate System

```bash
accelerapp generate examples/motor_controller.yaml --output ./demo_motor
```

### Key Features

- **STM32 firmware** with PWM control
- **C++ SDK** for high-performance control
- **Encoder feedback** handling
- **HTML control interface**

### Generated Components

1. **Firmware** (`demo_motor/firmware/`)
   - STM32 HAL-compatible code
   - PWM generation
   - Encoder reading
   - Safety features (limit switches)

2. **C++ SDK** (`demo_motor/software/`)
   - Low-level motor control
   - Position/speed control
   - Serial protocol implementation

3. **HTML UI** (`demo_motor/ui/`)
   - Simple, responsive interface
   - Direct motor control
   - Position monitoring

## Custom Hardware Example

Create your own hardware configuration:

```bash
# Generate a template
accelerapp init my_device.yaml

# Edit the configuration
nano my_device.yaml

# Generate everything
accelerapp generate my_device.yaml
```

### Sample Custom Configuration

```yaml
device_name: "Custom Robot Arm"
platform: "esp32"
software_language: "python"
ui_framework: "react"

peripherals:
  - type: "motor"
    pin: 3
    description: "Base rotation motor"
  
  - type: "motor"
    pin: 5
    description: "Shoulder motor"
  
  - type: "sensor"
    pin: 34
    description: "Position feedback"
  
  - type: "button"
    pin: 2
    description: "Emergency stop"
```

## Advanced Usage

### Generate Specific Components

```bash
# Firmware only
accelerapp generate my_device.yaml --firmware-only

# Software SDK only
accelerapp generate my_device.yaml --software-only

# UI only
accelerapp generate my_device.yaml --ui-only
```

### Multiple Language Support

```bash
# Python SDK
accelerapp generate config.yaml --software-only

# Change to C++ in config.yaml: software_language: "cpp"
accelerapp generate config.yaml --software-only

# Change to JavaScript: software_language: "javascript"
accelerapp generate config.yaml --software-only
```

### Multiple UI Frameworks

```bash
# React (modern, feature-rich)
# ui_framework: "react"
accelerapp generate config.yaml --ui-only

# HTML (simple, no build step)
# ui_framework: "html"
accelerapp generate config.yaml --ui-only

# Vue (progressive framework)
# ui_framework: "vue"
accelerapp generate config.yaml --ui-only
```

## Performance Metrics

Typical generation times on modern hardware:

| Project Type | Firmware | Software | UI | Total |
|-------------|----------|----------|-----|-------|
| Simple (LED) | <1s | <1s | <1s | ~2s |
| Medium (Sensors) | <1s | <1s | <1s | ~3s |
| Complex (Motor) | <1s | <1s | <1s | ~3s |

## Next Steps

1. Explore the [Architecture Documentation](docs/ARCHITECTURE.md)
2. Read the [Configuration Reference](docs/CONFIGURATION.md)
3. Check out [Contributing Guide](CONTRIBUTING.md)
4. Create your own hardware configurations
5. Share your projects with the community

## Troubleshooting

**Issue: Import errors after installation**
```bash
# Reinstall in development mode
pip install -e .
```

**Issue: Missing dependencies**
```bash
# Install all requirements
pip install -r requirements.txt
```

**Issue: Generation fails**
```bash
# Validate your YAML configuration
python -c "import yaml; yaml.safe_load(open('your_config.yaml'))"
```

## Community Examples

Share your configurations and generated projects:
- GitHub Discussions
- Discord Community
- Example Gallery (coming soon)

Happy Building! 🚀
