# Meshtastic Integration Guide

## Overview

Accelerapp now includes comprehensive support for Meshtastic mesh communication devices, enabling developers to program, configure, and manage Meshtastic devices seamlessly. This integration supports the complete Meshtastic ecosystem including firmware management, device programming, OTA updates, and air-gapped deployments.

## Features

### Core Capabilities

- **Device Discovery**: Automatic detection of Meshtastic devices via Serial, WiFi, and Bluetooth
- **Configuration Management**: Complete device configuration including channels, encryption, and radio settings
- **Firmware Management**: Flash custom and official firmware to supported hardware platforms
- **OTA Updates**: Support for both WiFi-OTA and BLE-OTA firmware update mechanisms
- **Multi-Device Support**: Manage multiple devices simultaneously
- **Air-Gapped Operation**: Full offline support with local firmware repository
- **Integration Code Generation**: Generate Python and C/C++ integration code
- **Agent-Based Operations**: Specialized Meshtastic agent for mesh networking tasks

### Supported Hardware

- **ESP32-based devices**: T-Beam, TTGO LoRa V1/V2, Heltec V2/V3
- **nRF52-based devices**: RAK4631, nRF52840-DK, Station G1, Nano G1
- **Custom hardware**: Support for custom Meshtastic-compatible builds

## Quick Start

### Basic Usage

```python
from accelerapp.platforms.meshtastic import MeshtasticPlatform

# Create platform instance
platform = MeshtasticPlatform()

# Get platform information
info = platform.get_platform_info()
print(f"Platform: {info['display_name']}")
print(f"Max Range: {info['max_range']}")
```

### Device Discovery

```python
from accelerapp.platforms.meshtastic import DeviceDiscovery

# Create discovery service
discovery = DeviceDiscovery()

# Discover all devices
devices = discovery.discover_all()

for device in devices:
    print(f"Found: {device.device_id} ({device.connection_type.value})")
```

### Device Configuration

```python
from pathlib import Path
from accelerapp.platforms.meshtastic import MeshtasticPlatform

platform = MeshtasticPlatform()

# Configuration specification
config = {
    "task": "configure",
    "hardware_model": "esp32",
    "region": "US",
    "gps_enabled": True,
    "bluetooth_enabled": True,
    "modem_preset": "LONG_FAST",
    "hop_limit": 3,
}

# Generate configuration
output_dir = Path("./meshtastic_config")
result = platform.generate_code(config, output_dir)

print(f"Configuration saved to: {result['output_dir']}")
```

### Firmware Management

```python
from pathlib import Path
from accelerapp.platforms.meshtastic import (
    FirmwareManager,
    HardwareModel
)

# Create firmware manager
manager = FirmwareManager(offline_mode=False)

# List available firmware versions
versions = manager.list_available_versions(HardwareModel.TBEAM)

for version in versions:
    print(f"Version: {version.version}")
    print(f"Hardware: {version.hardware_model.value}")

# Flash firmware to device
success = manager.flash_firmware(
    device_port="/dev/ttyUSB0",
    firmware_path=Path("./firmware.bin"),
    erase_flash=False
)
```

### OTA Updates

```python
from pathlib import Path
from accelerapp.platforms.meshtastic import OTAController, OTAMethod

# Create OTA controller
ota = OTAController()

# Perform WiFi OTA update
success = ota.perform_ota_update(
    device_id="192.168.1.100",
    firmware_path=Path("./firmware.bin"),
    method=OTAMethod.WIFI
)

print(f"OTA Update: {'Success' if success else 'Failed'}")
```

### Using the Meshtastic Agent

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

# Create agent
agent = MeshtasticAgent()

# Discover devices
result = agent.generate({
    "operation": "discover",
    "air_gapped": False
})

print(f"Devices found: {result['count']}")

# Generate configuration
config_result = agent.generate({
    "operation": "generate_config",
    "output_dir": "./config",
    "region": "US",
    "hardware_model": "esp32",
})
```

## Air-Gapped Deployment

Meshtastic integration fully supports air-gapped (offline) environments:

```python
from accelerapp.platforms.meshtastic import MeshtasticPlatform

# Enable air-gapped mode
platform = MeshtasticPlatform(air_gapped=True)

# All operations work offline:
# - Local firmware repository
# - Device configuration
# - OTA package creation
# - No external network dependencies
```

### Creating OTA Packages for Air-Gapped Deployment

```python
from pathlib import Path
from accelerapp.platforms.meshtastic import OTAController

# Create OTA controller in air-gapped mode
ota = OTAController(air_gapped=True)

# Create OTA package
success = ota.create_ota_package(
    firmware_path=Path("./firmware.bin"),
    output_path=Path("./ota_package.zip"),
    metadata={
        "version": "2.3.5",
        "hardware": "esp32",
        "build_date": "2025-10-14"
    }
)
```

## Configuration Generation

### Device Configuration

Generate complete Meshtastic device configurations in YAML format:

```python
spec = {
    "task": "configure",
    "hardware_model": "esp32",
    "region": "US",
    "role": "CLIENT",
    "gps_enabled": True,
    "position_interval": 900,
    "modem_preset": "LONG_FAST",
    "hop_limit": 3,
    "bluetooth_enabled": True,
    "bluetooth_mode": "RANDOM_PIN",
    "wifi_enabled": False,
    "channels": [
        {"index": 0, "name": "Primary", "psk": "AQ=="},
        {"index": 1, "name": "Secondary", "psk": "Ag=="}
    ]
}

result = platform.generate_code(spec, output_dir)
```

### Firmware Build Configuration

Generate custom firmware build configurations:

```python
spec = {
    "task": "firmware",
    "hardware_model": "esp32",
    "debug_build": False,
    "optimize": "size",
    "enable_gps": True,
    "enable_bluetooth": True,
    "enable_wifi": True,
    "enable_display": True,
    "custom_defines": {
        "LORA_FREQUENCY": "915.0",
        "MESH_MAX_NODES": "100"
    }
}

result = platform.generate_code(spec, output_dir)
```

### Integration Code Generation

Generate integration code for other platforms:

```python
# Python integration
python_spec = {
    "task": "integration",
    "language": "python",
}

result = platform.generate_code(python_spec, output_dir)

# C/C++ integration
cpp_spec = {
    "task": "integration",
    "language": "cpp",
}

result = platform.generate_code(cpp_spec, output_dir)
```

## Configuration Validation

Validate configurations before applying them:

```python
config = {
    "hardware_model": "esp32",
    "region": "US",
    "channels": [
        {"index": 0, "name": "Primary"}
    ]
}

errors = platform.validate_config(config)

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration valid!")
```

## Platform Integration

### Registering with Accelerapp

The Meshtastic platform is automatically registered with Accelerapp's platform factory:

```python
from accelerapp.platforms import get_platform

# Get Meshtastic platform instance
platform = get_platform("meshtastic")
```

### Integration with Digital Twin System

Meshtastic devices can be integrated with Accelerapp's digital twin platform:

```python
from accelerapp.digital_twin import DigitalTwinManager
from accelerapp.platforms.meshtastic import MeshtasticPlatform

# Create digital twin manager
twin_manager = DigitalTwinManager()

# Create platform
platform = MeshtasticPlatform()

# Discover devices
devices = platform.discover_devices()

# Create digital twins for each device
for device in devices:
    twin = twin_manager.create_twin(
        device.device_id,
        {
            "type": "meshtastic",
            "hardware_model": device.hardware_model,
            "connection_type": device.connection_type.value
        }
    )
```

## Advanced Features

### Multi-Device Management

Manage multiple Meshtastic devices simultaneously:

```python
from accelerapp.platforms.meshtastic import MeshtasticPlatform

platform = MeshtasticPlatform()

# Discover all devices
devices = platform.discover_devices()

# Configure each device
for device in devices:
    interface = platform.connect_device(device)
    if interface:
        interface.configure_device({
            "region": "US",
            "role": "CLIENT"
        })
        interface.disconnect()
```

### Custom Firmware Builds

Create custom firmware builds with specific features:

```python
from accelerapp.platforms.meshtastic import FirmwareManager, HardwareModel

manager = FirmwareManager()

success = manager.create_custom_firmware(
    base_version="2.3.5",
    hardware_model=HardwareModel.TBEAM,
    config={
        "enable_gps": True,
        "enable_display": True,
        "lora_frequency": 915.0,
        "custom_features": ["telemetry", "position_sharing"]
    },
    output_path=Path("./custom_firmware.bin")
)
```

### Mesh Network Monitoring

Monitor mesh network status and topology:

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

agent = MeshtasticAgent()

# Get mesh network status
result = agent.generate({
    "operation": "mesh_status",
    "device_id": "device_001"
})

print(f"Mesh status: {result['status']}")
```

## Command Line Interface

Use Accelerapp's CLI to work with Meshtastic devices:

```bash
# Discover Meshtastic devices
accelerapp meshtastic discover

# Generate device configuration
accelerapp meshtastic config \
  --hardware esp32 \
  --region US \
  --output ./config

# Flash firmware
accelerapp meshtastic flash \
  --port /dev/ttyUSB0 \
  --firmware ./firmware.bin

# Perform OTA update
accelerapp meshtastic ota \
  --device 192.168.1.100 \
  --firmware ./firmware.bin \
  --method wifi
```

## API Reference

### MeshtasticPlatform

Main platform class for Meshtastic operations.

**Methods:**
- `get_platform_info()`: Get platform information
- `generate_code(spec, output_dir)`: Generate configuration and code
- `validate_config(config)`: Validate configuration
- `discover_devices()`: Discover available devices
- `connect_device(device)`: Connect to a device
- `flash_firmware(device_port, hardware_model, version)`: Flash firmware
- `perform_ota_update(device_id, firmware_path, method)`: Perform OTA update

### DeviceDiscovery

Device discovery service.

**Methods:**
- `discover_serial_devices()`: Discover serial devices
- `discover_wifi_devices(timeout)`: Discover WiFi devices
- `discover_bluetooth_devices(timeout)`: Discover Bluetooth devices
- `discover_all()`: Discover all devices
- `get_discovered_devices()`: Get list of discovered devices

### FirmwareManager

Firmware management and flashing.

**Methods:**
- `list_available_versions(hardware_model)`: List firmware versions
- `download_firmware(version, hardware_model)`: Download firmware
- `flash_firmware(device_port, firmware_path, erase_flash)`: Flash firmware
- `verify_firmware(firmware_path, expected_checksum)`: Verify firmware
- `get_device_firmware_version(device_port)`: Get current firmware version
- `create_custom_firmware(base_version, hardware_model, config, output_path)`: Build custom firmware

### OTAController

OTA update controller.

**Methods:**
- `check_update_available(current_version, hardware_model)`: Check for updates
- `perform_ota_update(device_id, firmware_path, method, progress_callback)`: Perform OTA
- `rollback_firmware(device_id, method)`: Rollback firmware
- `create_ota_package(firmware_path, output_path, metadata)`: Create OTA package

### MeshtasticAgent

Specialized agent for Meshtastic operations.

**Supported Operations:**
- `discover`: Device discovery
- `configure`: Device configuration
- `flash_firmware`: Firmware flashing
- `ota_update`: OTA updates
- `generate_config`: Configuration generation
- `mesh_status`: Mesh network status

## Examples

See the comprehensive demo in `examples/meshtastic_demo.py` for complete examples of all features.

## Testing

Run the Meshtastic integration tests:

```bash
pytest tests/test_meshtastic.py -v
```

All 28 tests cover:
- Platform initialization and configuration
- Device discovery and interface
- Firmware management
- OTA updates
- Agent operations
- Configuration validation

## Troubleshooting

### Device Not Found

If devices are not discovered:
1. Check USB connection (for serial devices)
2. Verify device drivers are installed
3. Check device is powered on
4. Try manual port specification

### Firmware Flashing Failed

If firmware flashing fails:
1. Verify firmware file is valid
2. Check device is in bootloader mode
3. Ensure correct hardware model selected
4. Try erasing flash first

### OTA Update Failed

If OTA update fails:
1. Verify device is connected to WiFi/BLE
2. Check firmware file size and format
3. Ensure device has sufficient battery
4. Verify network connectivity

## Contributing

Contributions to the Meshtastic integration are welcome! Areas for enhancement:
- Additional hardware model support
- Web interface integration
- Advanced mesh topology visualization
- ML-based mesh optimization
- Enhanced air-gapped features

## Resources

- [Meshtastic Official Documentation](https://meshtastic.org/)
- [Meshtastic Firmware Repository](https://github.com/meshtastic/firmware)
- [Meshtastic Python API](https://github.com/meshtastic/python)
- [Accelerapp Documentation](https://github.com/thewriterben/Accelerapp)

## License

This integration is part of Accelerapp and is licensed under the MIT License.
