# Enhanced Hardware Support for Accelerapp v2.0

**Version:** 2.0.0  
**Last Updated:** 2025-10-14

## Overview

Accelerapp v2.0 introduces comprehensive enhanced hardware support including:
- **STM32 Series Integration** - F4, H7 with HAL and CubeMX support
- **Nordic nRF Platforms** - nRF52, nRF53 with BLE and Zephyr RTOS
- **FreeRTOS Support** - Task generation, configuration, and IPC primitives
- **Advanced Peripheral Management** - Conflict resolution and resource optimization

## Table of Contents

1. [New Platforms](#new-platforms)
2. [STM32 Enhanced Support](#stm32-enhanced-support)
3. [Nordic nRF Platform Support](#nordic-nrf-platform-support)
4. [FreeRTOS Integration](#freertos-integration)
5. [Advanced Peripheral Management](#advanced-peripheral-management)
6. [Usage Examples](#usage-examples)
7. [Migration Guide](#migration-guide)

---

## New Platforms

### Supported Platforms

| Platform | Family | Core | Key Features |
|----------|--------|------|--------------|
| **STM32F4** | ARM Cortex-M4 | Up to 180MHz | FPU, DSP, USB, Ethernet |
| **STM32H7** | ARM Cortex-M7 | Up to 480MHz | Dual-precision FPU, Cache, High-speed memory |
| **nRF52** | ARM Cortex-M4F | 64MHz | BLE 5.3, NFC, Ultra-low power |
| **nRF53** | Dual Cortex-M33 | 128MHz + 64MHz | BLE 5.3, LE Audio, TrustZone, Dual-core |

### Platform Selection

```python
from accelerapp.platforms import get_platform

# Get STM32F4 platform
stm32f4 = get_platform("stm32f4")

# Get STM32H7 platform
stm32h7 = get_platform("stm32h7")

# Get Nordic nRF52 platform
nrf52 = get_platform("nrf52")

# Get Nordic nRF53 platform
nrf53 = get_platform("nrf53")
```

---

## STM32 Enhanced Support

### Features

- **Series-Specific Implementations**
  - STM32F4: Cortex-M4 with FPU, DSP instructions
  - STM32H7: Cortex-M7 with cache, high-speed memory
  
- **HAL Integration**
  - Complete HAL driver code generation
  - GPIO, UART, I2C, SPI, ADC, Timer initialization
  - DMA-based peripheral support
  
- **CubeMX Integration**
  - .ioc file generation
  - STM32CubeIDE project files (.project, .cproject)
  - Compatible with existing CubeMX workflows

### Basic Usage

```python
from accelerapp.platforms.stm32 import STM32F4Platform
from pathlib import Path

# Create platform instance
platform = STM32F4Platform()

# Get platform information
info = platform.get_platform_info()
print(f"Platform: {info['series']}")
print(f"Max Clock: {info['max_clock']} MHz")
print(f"Capabilities: {info['capabilities']}")

# Generate code
spec = {
    "device_name": "IoTSensor",
    "peripherals": [
        {"type": "led", "pin": 13},
        {"type": "button", "pin": 0},
        {"type": "sensor", "pin": 2}
    ],
    "rtos": "freertos"
}

output_dir = Path("./output/stm32_project")
result = platform.generate_code(spec, output_dir)
print(f"Generated {len(result['files_generated'])} files")
```

### HAL Code Generation

```python
from accelerapp.platforms.stm32.hal_generator import STM32HALGenerator

generator = STM32HALGenerator("F4")

# Generate GPIO initialization
gpio_config = {
    "ports": ["A", "B"],
    "pins": [
        {"port": "A", "pin": 5, "mode": "OUTPUT_PP", "pull": "NOPULL", "speed": "FREQ_LOW"}
    ]
}
gpio_code = generator.generate_gpio_init(gpio_config)

# Generate UART initialization
uart_config = {
    "instance": "USART2",
    "baudrate": 115200
}
uart_code = generator.generate_uart_init(uart_config)

# Generate I2C initialization
i2c_config = {
    "instance": "I2C1",
    "clock_speed": 100000
}
i2c_code = generator.generate_i2c_init(i2c_config)
```

### CubeMX Project Generation

```python
from accelerapp.platforms.stm32.cubemx_integration import CubeMXIntegration
from pathlib import Path

integration = CubeMXIntegration()

config = {
    "project_name": "MySTM32Project",
    "mcu": "STM32F401RETx",
    "peripherals": [
        {
            "type": "uart",
            "instance": "USART2",
            "baudrate": 115200
        }
    ]
}

output_dir = Path("./cubemx_project")
files = integration.generate_complete_project(config, output_dir)
print(f"Generated CubeMX project with {len(files)} files")
```

---

## Nordic nRF Platform Support

### Features

- **nRF52 Series**
  - BLE 5.3 stack integration
  - NFC tag support (nRF52840)
  - Ultra-low power optimization
  
- **nRF53 Series**
  - Dual-core (Application + Network)
  - LE Audio support
  - ARM TrustZone security
  
- **Zephyr RTOS**
  - Complete project configuration
  - Devicetree overlay generation
  - CMakeLists.txt and prj.conf

### Basic Usage

```python
from accelerapp.platforms.nordic import NRF52Platform
from pathlib import Path

# Create platform instance
platform = NRF52Platform()

# Generate code with BLE
spec = {
    "device_name": "BLEDevice",
    "peripherals": [
        {"type": "led", "pin": 13},
        {"type": "ble_peripheral"},
        {"type": "temperature_sensor"}
    ],
    "rtos": "zephyr"
}

output_dir = Path("./output/nrf52_project")
result = platform.generate_code(spec, output_dir)
```

### BLE Stack Integration

```python
from accelerapp.platforms.nordic.ble_stack import BLEStack

stack = BLEStack("s140")  # SoftDevice variant

# Generate custom BLE service
service_config = {
    "name": "environmental_sensing",
    "uuid": "0x181A",
    "characteristics": [
        {"name": "temperature", "uuid": "0x2A6E"},
        {"name": "humidity", "uuid": "0x2A6F"}
    ]
}

service_code = stack.generate_service(service_config)

# Generate advertising configuration
adv_config = {
    "device_name": "EnvSensor",
    "interval": 300,  # 187.5ms
    "timeout": 180    # 180 seconds
}

adv_code = stack.generate_advertising(adv_config)
```

### Zephyr RTOS Integration

```python
from accelerapp.platforms.nordic.zephyr_integration import ZephyrIntegration
from pathlib import Path

integration = ZephyrIntegration("nrf52840dk_nrf52840")

config = {
    "project_name": "sensor_app",
    "ble_enabled": True,
    "device_name": "SensorNode",
    "logging_enabled": True,
    "gpio_enabled": True,
    "leds": [
        {"pin": 13},
        {"pin": 14}
    ],
    "buttons": [
        {"pin": 11}
    ]
}

output_dir = Path("./zephyr_project")
files = integration.generate_complete_project(config, output_dir)
```

---

## FreeRTOS Integration

### Features

- **Task Generation**
  - Periodic and event-driven tasks
  - Priority management
  - Stack size optimization
  
- **Configuration Generation**
  - Platform-optimized FreeRTOSConfig.h
  - STM32, nRF, ESP32 specific settings
  
- **IPC Primitives**
  - Queues for inter-task communication
  - Semaphores (binary and counting)
  - Mutexes (regular and recursive)
  - Event groups for synchronization

### Task Generation

```python
from accelerapp.rtos.freertos import FreeRTOSTaskGenerator

generator = FreeRTOSTaskGenerator()

# Define tasks
tasks = [
    {
        "name": "sensor_read",
        "priority": "tskIDLE_PRIORITY + 2",
        "stack_size": 256,
        "period_ms": 100,
        "type": "sensor_read"
    },
    {
        "name": "data_process",
        "priority": "tskIDLE_PRIORITY + 3",
        "stack_size": 512,
        "period_ms": 1000,
        "type": "actuator_control"
    }
]

# Generate all tasks
all_tasks_code = generator.generate_all_tasks(tasks)

# Analyze task timing
analysis = generator.analyze_task_timing(tasks)
print(f"CPU Utilization: {analysis['utilization']:.1f}%")
```

### Configuration Generation

```python
from accelerapp.rtos.freertos import FreeRTOSConfigGenerator

# Generate configuration for STM32F4
generator = FreeRTOSConfigGenerator("stm32f4")

config = {
    "cpu_clock_hz": 84000000,
    "tick_rate_hz": 1000,
    "max_priorities": 5,
    "minimal_stack_size": 128,
    "total_heap_size": 15360,
    "use_mutexes": True,
    "use_timers": True,
    "use_idle_hook": False,
    "use_tick_hook": False,
    "stack_overflow_check": 2
}

config_code = generator.generate_config(config)

# Write to file
with open("FreeRTOSConfig.h", "w") as f:
    f.write(config_code)
```

### IPC Primitives

```python
from accelerapp.rtos.freertos import IPCPrimitives

ipc = IPCPrimitives()

# Define IPC primitives
ipc_config = {
    "queues": [
        {
            "name": "sensor_data_queue",
            "length": 10,
            "item_size": "sizeof(sensor_data_t)"
        }
    ],
    "semaphores": [
        {
            "name": "data_ready_sem",
            "type": "binary"
        }
    ],
    "mutexes": [
        {
            "name": "i2c_mutex",
            "recursive": False
        }
    ],
    "event_groups": [
        {
            "name": "system_events",
            "bits": {
                "sensor_ready": 0,
                "data_processed": 1,
                "error_occurred": 2
            }
        }
    ]
}

# Generate all IPC code
all_ipc_code = ipc.generate_all_ipc(ipc_config)
```

---

## Advanced Peripheral Management

### Features

- **Conflict Detection**
  - Pin conflict identification
  - Compatible function detection
  - Comprehensive conflict reporting
  
- **Resource Management**
  - DMA channel allocation
  - Timer resource optimization
  - Peripheral instance tracking
  
- **Alternative Suggestions**
  - Platform-specific pin alternatives
  - Optimal resource allocation

### Conflict Resolution

```python
from accelerapp.peripherals import PeripheralConflictResolver

resolver = PeripheralConflictResolver("stm32")

# Add peripherals
peripheral1 = {
    "id": "uart1",
    "type": "uart",
    "pins": [
        {"pin": 2, "function": "UART_TX"},
        {"pin": 3, "function": "UART_RX"}
    ]
}

success, conflicts = resolver.add_peripheral(peripheral1)
if not success:
    print(f"Conflicts detected: {conflicts}")
    
    # Get alternative suggestions
    alternatives = resolver.suggest_alternatives(peripheral1)
    print(f"Alternatives: {alternatives}")

# Generate conflict report
report = resolver.get_conflict_report()
print(f"Total peripherals: {report['total_peripherals']}")
print(f"Total pins used: {report['total_pins_used']}")
print(f"Conflicts: {len(report['conflicts'])}")
```

### Resource Management

```python
from accelerapp.peripherals import PeripheralResourceManager
from accelerapp.peripherals.resource_manager import ResourceType

manager = PeripheralResourceManager("stm32f4")

# Allocate DMA channel
dma_allocation = manager.allocate_resource(
    ResourceType.DMA_CHANNEL,
    "uart1",
    "uart",
    priority=2,
    metadata={"data_rate": 115200}
)

if dma_allocation:
    print(f"Allocated DMA channel {dma_allocation.resource_id}")

# Get DMA suggestion for high-speed peripheral
suggestion = manager.suggest_dma_allocation("spi", 1000000)
print(f"DMA recommendation: {suggestion['recommendation']}")
print(f"Estimated CPU savings: {suggestion['estimated_cpu_savings']}%")

# Optimize timer allocation for PWM
pwm_optimization = manager.optimize_timer_allocation(6)
print(f"Timers needed: {pwm_optimization['timers_needed']}")

# Get utilization report
utilization = manager.get_utilization()
for resource_type, stats in utilization.items():
    print(f"{resource_type}: {stats['allocated']}/{stats['limit']} ({stats['utilization_percent']:.1f}%)")
```

---

## Usage Examples

### Example 1: STM32F4 IoT Sensor with FreeRTOS

```python
from accelerapp.platforms.stm32 import STM32F4Platform
from accelerapp.rtos.freertos import FreeRTOSTaskGenerator, FreeRTOSConfigGenerator
from pathlib import Path

# Create platform and generators
platform = STM32F4Platform()
task_gen = FreeRTOSTaskGenerator()
config_gen = FreeRTOSConfigGenerator("stm32f4")

# Define hardware specification
spec = {
    "device_name": "IoTSensor",
    "peripherals": [
        {"type": "led", "pin": 13},
        {"type": "sensor", "pin": 2},
        {"type": "button", "pin": 0}
    ],
    "rtos": "freertos"
}

# Define RTOS tasks
tasks = [
    {
        "name": "sensor_read",
        "priority": "tskIDLE_PRIORITY + 2",
        "stack_size": 256,
        "period_ms": 100
    },
    {
        "name": "led_blink",
        "priority": "tskIDLE_PRIORITY + 1",
        "stack_size": 128,
        "period_ms": 500
    }
]

# Generate code
output_dir = Path("./output/iot_sensor")
result = platform.generate_code(spec, output_dir)

# Generate RTOS code
tasks_code = task_gen.generate_all_tasks(tasks)
config_code = config_gen.generate_config({
    "cpu_clock_hz": 84000000,
    "tick_rate_hz": 1000
})

# Write RTOS files
(output_dir / "tasks.c").write_text(tasks_code)
(output_dir / "FreeRTOSConfig.h").write_text(config_code)

print(f"Project generated at {output_dir}")
```

### Example 2: nRF52 BLE Peripheral with Zephyr

```python
from accelerapp.platforms.nordic import NRF52Platform
from accelerapp.platforms.nordic.ble_stack import BLEStack
from accelerapp.platforms.nordic.zephyr_integration import ZephyrIntegration
from pathlib import Path

# Create platform and integrations
platform = NRF52Platform()
ble_stack = BLEStack("s140")
zephyr = ZephyrIntegration("nrf52840dk_nrf52840")

# Define BLE service
service_config = {
    "name": "heart_rate",
    "uuid": "0x180D",
    "characteristics": [
        {"name": "hr_measurement", "uuid": "0x2A37"},
        {"name": "body_sensor_location", "uuid": "0x2A38"}
    ]
}

# Generate BLE service
service_code = ble_stack.generate_service(service_config)

# Generate Zephyr project
zephyr_config = {
    "project_name": "ble_heart_rate",
    "ble_enabled": True,
    "device_name": "HR_Monitor",
    "logging_enabled": True,
    "gpio_enabled": True
}

output_dir = Path("./output/ble_heart_rate")
files = zephyr.generate_complete_project(zephyr_config, output_dir)

# Write BLE service
(output_dir / "src" / "ble_service.c").write_text(service_code)

print(f"BLE project generated at {output_dir}")
```

### Example 3: Multi-Platform Project with Resource Optimization

```python
from accelerapp.platforms import get_platform
from accelerapp.peripherals import PeripheralResourceManager, PeripheralConflictResolver
from pathlib import Path

def generate_optimized_project(platform_name, spec, output_dir):
    # Get platform
    platform = get_platform(platform_name)
    
    # Create managers
    resource_mgr = PeripheralResourceManager(platform_name)
    conflict_resolver = PeripheralConflictResolver(platform_name)
    
    # Check for conflicts
    for peripheral in spec["peripherals"]:
        success, conflicts = conflict_resolver.add_peripheral(peripheral)
        if not success:
            print(f"Conflicts detected for {peripheral['id']}")
            alternatives = conflict_resolver.suggest_alternatives(peripheral)
            print(f"Suggested alternatives: {alternatives}")
            return
    
    # Optimize resources
    optimization = conflict_resolver.optimize_pin_mapping()
    print(f"Pin mapping optimization: {optimization['status']}")
    
    # Generate utilization report
    print("\nResource Utilization:")
    print(resource_mgr.generate_resource_report())
    
    # Generate code
    result = platform.generate_code(spec, output_dir)
    print(f"\nGenerated {len(result['files_generated'])} files")
    return result

# Example usage
spec = {
    "device_name": "MultiSensor",
    "peripherals": [
        {"id": "uart1", "type": "uart", "pins": [{"pin": 2}, {"pin": 3}]},
        {"id": "i2c1", "type": "i2c", "pins": [{"pin": 4}, {"pin": 5}]},
        {"id": "spi1", "type": "spi", "pins": [{"pin": 10}, {"pin": 11}, {"pin": 12}]}
    ]
}

generate_optimized_project("stm32f4", spec, Path("./output/multi_sensor"))
```

---

## Migration Guide

### From v1.0 to v2.0

#### Backward Compatibility

All v1.0 code continues to work without changes:

```python
# v1.0 code (still works)
from accelerapp.platforms import get_platform

platform = get_platform("stm32")  # Returns STM32F4Platform
```

#### Using New Features

Take advantage of new platform-specific features:

```python
# v2.0 - Specify exact series
from accelerapp.platforms import get_platform

# Use STM32H7 for high-performance applications
platform = get_platform("stm32h7")

# Use nRF52 for BLE applications
platform = get_platform("nrf52")
```

#### Enhanced Code Generation

v2.0 provides more comprehensive code generation:

```python
# v1.0 - Basic generation
result = platform.generate_code(spec, output_dir)

# v2.0 - With RTOS and optimizations
spec["rtos"] = "freertos"
spec["optimization"] = "-O2"
result = platform.generate_code(spec, output_dir)

# Now includes HAL drivers, RTOS tasks, and peripheral drivers
print(f"Generated files: {result['files_generated']}")
```

---

## API Reference

### Platform Classes

- `STM32F4Platform` - STM32F4 series support
- `STM32H7Platform` - STM32H7 series support
- `NRF52Platform` - Nordic nRF52 series support
- `NRF53Platform` - Nordic nRF53 series support

### RTOS Modules

- `FreeRTOSTaskGenerator` - Task generation
- `FreeRTOSConfigGenerator` - Configuration generation
- `IPCPrimitives` - IPC primitives generation

### Peripheral Management

- `PeripheralConflictResolver` - Pin conflict resolution
- `PeripheralResourceManager` - Resource allocation and optimization

### Code Generators

- `STM32HALGenerator` - STM32 HAL code generation
- `CubeMXIntegration` - CubeMX project generation
- `BLEStack` - Nordic BLE stack generation
- `ZephyrIntegration` - Zephyr RTOS project generation

---

## Support and Contributing

### Documentation
- [GitHub Repository](https://github.com/thewriterben/Accelerapp)
- [API Documentation](docs/)
- [Examples](examples/)

### Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License
MIT License - see [LICENSE](LICENSE) file for details.

---

**Accelerapp v2.0** - Comprehensive embedded development platform for professional embedded systems.
