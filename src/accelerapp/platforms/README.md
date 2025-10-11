# Platform Abstraction Layer

## Overview

The platform abstraction layer provides unified support for multiple hardware platforms, enabling seamless code generation across different microcontroller architectures.

## Supported Platforms

### Arduino
- **MCU Family**: AVR (8-bit)
- **Languages**: C, C++
- **Capabilities**: GPIO, PWM, Analog Input, Serial, I2C, SPI
- **Build System**: Arduino IDE, PlatformIO

### ESP32
- **MCU Family**: Xtensa LX6 (32-bit)
- **Languages**: C, C++, MicroPython
- **Capabilities**: GPIO, PWM, WiFi, Bluetooth, Camera, WebSocket
- **Build System**: ESP-IDF, PlatformIO, Arduino

### STM32
- **MCU Family**: ARM Cortex-M (32-bit)
- **Languages**: C, C++
- **Capabilities**: GPIO, PWM, CAN, USB, Ethernet, DMA
- **Build System**: STM32CubeIDE, PlatformIO

### MicroPython
- **MCU Family**: Various (ESP32, Pyboard)
- **Languages**: Python, MicroPython
- **Capabilities**: GPIO, PWM, WiFi, Bluetooth, I2C, SPI
- **Build System**: MicroPython, Thonny

## Usage

### Basic Usage

```python
from accelerapp.platforms import get_platform

# Get platform instance
platform = get_platform('esp32')

# Check platform info
info = platform.get_platform_info()
print(f"Platform: {info['display_name']}")
print(f"Capabilities: {info['capabilities']}")

# Generate code
spec = {
    'device_name': 'My Device',
    'peripherals': [
        {'type': 'led', 'pin': 2},
    ],
}

result = platform.generate_code(spec, output_dir)
```

### Platform-Specific Features

#### ESP32 WiFi

```python
spec = {
    'device_name': 'ESP32 Sensor',
    'platform': 'esp32',
    'wifi': {
        'ssid': 'MyNetwork',
        'password': 'MyPassword',
    },
    'peripherals': [
        {'type': 'wifi_module'},
        {'type': 'sensor', 'pin': 34},
    ],
}
```

#### MicroPython Rapid Prototyping

```python
spec = {
    'device_name': 'Quick Prototype',
    'platform': 'micropython',
    'peripherals': [
        {'type': 'led', 'pin': 2, 'name': 'status_led'},
    ],
}
```

## Adding New Platforms

To add support for a new platform:

1. Create a new file in `src/accelerapp/platforms/`
2. Inherit from `BasePlatform`
3. Implement required methods
4. Register in `__init__.py`

Example:

```python
from .base import BasePlatform

class NewPlatform(BasePlatform):
    def __init__(self):
        super().__init__()
        self.name = "new_platform"
        self.capabilities = ['gpio', 'pwm']
        
    def get_platform_info(self):
        return {
            'name': self.name,
            'display_name': 'New Platform',
            'capabilities': self.capabilities,
        }
        
    def generate_code(self, spec, output_dir):
        # Implementation
        pass
        
    def validate_config(self, config):
        # Validation logic
        return []
```

## Platform Selection

Choose the right platform based on your needs:

| Feature | Arduino | ESP32 | STM32 | MicroPython |
|---------|---------|-------|-------|-------------|
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Performance | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| WiFi | ❌ | ✅ | Optional | ✅ |
| Cost | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Development Speed | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Examples

See `examples/` directory for complete examples:
- `multi_platform_led.yaml`: Works on all platforms
- `esp32_wifi_sensor.yaml`: ESP32-specific features
