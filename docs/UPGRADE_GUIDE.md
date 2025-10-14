# Accelerapp Comprehensive Upgrade Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

## Overview

This guide covers the comprehensive upgrade to version 1.0.0, transforming Accelerapp into a production-ready, next-generation hardware control platform with advanced capabilities including air-gapped deployment, enterprise security, and advanced code optimization.

## What's New

### Phase 1: Core Platform Restructuring

#### Multi-Platform Support (`src/accelerapp/platforms/`)

The new platform abstraction layer provides unified support for multiple hardware platforms:

- **Arduino**: AVR-based microcontrollers (Uno, Mega, Nano)
- **ESP32**: WiFi/Bluetooth-enabled boards with camera support
- **STM32**: Industrial ARM Cortex-M microcontrollers
- **MicroPython**: Python-based rapid prototyping

**Usage Example:**

```python
from accelerapp.platforms import get_platform

# Get platform instance
platform = get_platform('esp32')

# Generate code
spec = {
    'device_name': 'My Device',
    'peripherals': [
        {'type': 'led', 'pin': 2},
        {'type': 'sensor', 'pin': 34},
    ],
}

result = platform.generate_code(spec, output_dir)
```

#### Hardware Abstraction Layer (`src/accelerapp/hardware/`)

The HAL provides component management and conflict detection:

- **Component Factory**: Dynamic component instantiation
- **Conflict Detection**: Automatic pin conflict checking
- **Resource Management**: Track and manage hardware resources

**Usage Example:**

```python
from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory

hal = HardwareAbstractionLayer()

# Create and add components
led = ComponentFactory.create_component('led', {'name': 'status_led', 'pin': 13})
hal.add_component(led)

# Check for conflicts
conflicts = hal.check_pin_conflicts(led)

# Get statistics
stats = hal.get_stats()
```

#### Template System (`src/accelerapp/templates/`)

Jinja2-based template engine for code generation:

- **Platform-specific templates**: Optimized for each target
- **Custom filters**: upper_snake_case, camelCase, PascalCase
- **Template fallback**: Graceful degradation to generic templates

**Usage Example:**

```python
from accelerapp.templates import TemplateManager

manager = TemplateManager()

# Render with filters
template = "class {{ name | pascal_case }}"
result = manager.render_string(template, {'name': 'my_device'})
# Output: "class MyDevice"

# Platform-specific generation
code = manager.generate_from_platform(
    'esp32', 'cpp', 'main', {'device_name': 'Sensor'}
)
```

### Phase 2: AI Agent Integration

#### AI Agent (`src/accelerapp/agents/ai_agent.py`)

Intelligent code optimization and analysis:

- **Code Optimization**: Detect optimization opportunities
- **Architecture Analysis**: Analyze system complexity
- **Design Patterns**: Suggest appropriate patterns
- **Code Review**: Automated code quality checks

**Usage Example:**

```python
from accelerapp.agents import AIAgent

agent = AIAgent()

# Optimize code
result = agent.generate({
    'task_type': 'optimize',
    'code': 'void loop() { delay(1000); }',
    'platform': 'arduino',
})

# Analyze architecture
result = agent.generate({
    'task_type': 'analyze',
    'peripherals': [...],
})
```

#### Firmware Agent (`src/accelerapp/agents/firmware_agent.py`)

Specialized embedded systems expert:

- **Firmware Generation**: Platform-specific firmware
- **Optimization**: Memory and performance tuning
- **Analysis**: Resource usage and constraints
- **Platform Expertise**: Expert knowledge for each platform

**Usage Example:**

```python
from accelerapp.agents import FirmwareAgent

agent = FirmwareAgent()

# Generate firmware
result = agent.generate({
    'task_type': 'generate',
    'platform': 'esp32',
    'peripherals': [...],
})

# Get platform support
support = agent.get_platform_support()
# {'arduino': 'expert', 'esp32': 'expert', ...}
```

## Migration Guide

### For Existing Users

The upgrade is **backward compatible**. Your existing code will continue to work:

```python
# This still works
from accelerapp.core import AccelerappCore
core = AccelerappCore(config_path)
result = core.generate_firmware(output_dir)
```

### Using New Features

To leverage new capabilities, update your code:

**Before:**
```python
from accelerapp.core import AccelerappCore
core = AccelerappCore(config_path)
result = core.generate_firmware(output_dir)
```

**After (with platform selection):**
```python
from accelerapp.platforms import get_platform

platform = get_platform('esp32')
result = platform.generate_code(spec, output_dir)
```

**With AI optimization:**
```python
from accelerapp.agents import AIAgent, FirmwareAgent

# Analyze first
ai_agent = AIAgent()
analysis = ai_agent.generate({'task_type': 'analyze', 'peripherals': [...]})

# Then generate
firmware_agent = FirmwareAgent()
result = firmware_agent.generate({'task_type': 'generate', ...})
```

## Configuration Updates

### New YAML Fields

The configuration format has been extended:

```yaml
# Standard fields (existing)
device_name: "My Device"
platform: "esp32"  # Now supports: arduino, esp32, stm32, micropython

# New WiFi support (ESP32)
wifi:
  ssid: "MyNetwork"
  password: "MyPassword"

# Enhanced peripheral definitions
peripherals:
  - type: "camera"           # NEW: ESP32-CAM support
    description: "RTSP camera"
  
  - type: "wifi_module"      # NEW: WiFi capability
    description: "WiFi connectivity"
  
  - type: "bluetooth_module" # NEW: Bluetooth support
    description: "BLE connectivity"
```

## Examples

### Example 1: ESP32 WiFi Sensor

See `examples/esp32_wifi_sensor.yaml`:

```yaml
device_name: "ESP32 WiFi Sensor"
platform: "esp32"

wifi:
  ssid: "MyNetwork"
  password: "MyPassword"

peripherals:
  - type: "sensor"
    pin: 34
  - type: "wifi_module"
```

### Example 2: Multi-Platform LED Controller

See `examples/multi_platform_led.yaml`:

```yaml
device_name: "LED Controller"
platform: "arduino"  # Change to esp32, stm32, micropython

peripherals:
  - type: "led"
    pin: 13
```

## Running the Demo

Test all new features with the demonstration script:

```bash
python examples/platform_demo.py
```

This demonstrates:
- Platform abstraction for all platforms
- Hardware abstraction layer with conflict detection
- Template system with filters
- AI and Firmware agents
- Complete code generation workflow

## Testing

The upgrade includes 57 new tests:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_platforms.py      # Platform abstraction tests
pytest tests/test_hardware.py       # HAL tests
pytest tests/test_templates.py      # Template system tests
pytest tests/test_new_agents.py     # Agent tests
```

All 138 tests (81 original + 57 new) pass successfully.

## API Reference

### Platform API

```python
from accelerapp.platforms import get_platform, BasePlatform

# Get platform
platform = get_platform('arduino')

# Platform info
info = platform.get_platform_info()

# Generate code
result = platform.generate_code(spec, output_dir)

# Validate config
errors = platform.validate_config(config)

# Build config
build_config = platform.get_build_config()
```

### Hardware Abstraction API

```python
from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory

# Create HAL
hal = HardwareAbstractionLayer()

# Create component
component = ComponentFactory.create_component('led', {'pin': 13})

# Add component
success = hal.add_component(component)

# Check conflicts
conflicts = hal.check_pin_conflicts(component)

# Get statistics
stats = hal.get_stats()
```

### Template API

```python
from accelerapp.templates import TemplateManager

# Create manager
manager = TemplateManager()

# Render string
result = manager.render_string(template, context)

# Render file
result = manager.render_template('main.j2', context)

# Platform-specific
code = manager.generate_from_platform(platform, lang, type, context)
```

### Agent API

```python
from accelerapp.agents import AIAgent, FirmwareAgent

# AI Agent
ai = AIAgent()
result = ai.generate(spec, context)
capabilities = ai.get_capabilities()
info = ai.get_info()

# Firmware Agent
firmware = FirmwareAgent()
result = firmware.generate(spec, context)
support = firmware.get_platform_support()
```

## Troubleshooting

### Platform Not Found

```python
ValueError: Unsupported platform: xyz
```

**Solution**: Use one of: 'arduino', 'esp32', 'stm32', 'micropython'

### Pin Conflict

```python
# Component not added due to conflict
result = hal.add_component(component)  # Returns False
```

**Solution**: Check conflicts before adding:
```python
conflicts = hal.check_pin_conflicts(component)
if not conflicts:
    hal.add_component(component)
```

### Template Not Found

```python
# Returns empty string if template doesn't exist
result = manager.render_template('missing.j2', {})  # ""
```

**Solution**: Check template existence:
```python
if manager.template_exists('template.j2'):
    result = manager.render_template('template.j2', context)
```

## Next Steps

### Phase 3-5 (Planned)

- Enhanced ESP32-CAM support with RTSP streaming
- CAN-BUS and Modbus protocol integration
- Wildlife monitoring features
- Industrial IoT capabilities
- Advanced power management

### Contributing

To extend the platform:

1. **Add new platform**: Inherit from `BasePlatform`
2. **Add new component**: Extend `ComponentFactory`
3. **Add new template**: Create `.j2` files in `templates/files/`
4. **Add new agent**: Inherit from `BaseAgent`

See `CONTRIBUTING.md` for details.

## Support

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Tests**: `tests/` directory
- **Issues**: GitHub issue tracker

## Version History

- **v0.1.0**: Initial release
- **v0.2.0**: Phases 1-2 comprehensive upgrade
  - Multi-platform support
  - Hardware abstraction layer
  - Template system
  - AI and Firmware agents
  - 57 new tests
