# Meshtastic Quick Start Guide

## Installation

Accelerapp now includes built-in Meshtastic support. No additional dependencies required for basic functionality.

## 5-Minute Quick Start

### 1. Import Meshtastic Platform

```python
from accelerapp.platforms.meshtastic import MeshtasticPlatform

# Create platform instance
platform = MeshtasticPlatform()
```

### 2. Discover Devices

```python
# Discover all Meshtastic devices
devices = platform.discover_devices()

for device in devices:
    print(f"Found: {device.device_name} on {device.connection_type.value}")
```

### 3. Generate Configuration

```python
from pathlib import Path

# Create device configuration
config = {
    "task": "configure",
    "hardware_model": "esp32",
    "region": "US",  # US, EU_868, EU_433, etc.
    "gps_enabled": True,
    "bluetooth_enabled": True,
}

# Generate config files
result = platform.generate_code(config, Path("./meshtastic_config"))
print(f"Configuration saved to: {result['output_dir']}")
```

### 4. Use the Agent

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

# Create agent
agent = MeshtasticAgent()

# Discover devices
result = agent.generate({"operation": "discover"})
print(f"Found {result['count']} devices")
```

## Common Tasks

### Configure a Device

```python
config_spec = {
    "operation": "generate_config",
    "output_dir": "./my_config",
    "region": "US",
    "hardware_model": "esp32",
    "gps_enabled": True,
    "modem_preset": "LONG_FAST",  # LONG_FAST, LONG_SLOW, MEDIUM_FAST
}

result = agent.generate(config_spec)
```

### Flash Firmware

```python
from accelerapp.platforms.meshtastic import HardwareModel

platform.flash_firmware(
    device_port="/dev/ttyUSB0",
    hardware_model=HardwareModel.TBEAM,
    version="2.3.5"  # or None for latest
)
```

### Perform OTA Update

```python
from accelerapp.platforms.meshtastic import OTAMethod
from pathlib import Path

platform.perform_ota_update(
    device_id="192.168.1.100",  # IP for WiFi, address for BLE
    firmware_path=Path("./firmware.bin"),
    method=OTAMethod.WIFI  # or OTAMethod.BLE
)
```

### Air-Gapped Deployment

```python
# Enable air-gapped mode
platform = MeshtasticPlatform(air_gapped=True)

# All operations work offline
devices = platform.discover_devices()
config = platform.generate_code(spec, output_dir)
```

## Examples

### Run Basic Demo

```bash
cd examples
python meshtastic_demo.py
```

### Run Digital Twin Integration

```bash
python meshtastic_digital_twin_integration.py
```

## Supported Hardware

- **ESP32**: T-Beam, TTGO LoRa V1/V2, Heltec V2/V3
- **nRF52**: RAK4631, nRF52840-DK, Station G1
- **Custom**: Any Meshtastic-compatible hardware

## Key Features

- ✅ **Device Discovery**: Automatic detection via Serial, WiFi, BLE
- ✅ **Configuration Management**: Complete device setup
- ✅ **Firmware Management**: Flash and verify firmware
- ✅ **OTA Updates**: WiFi and BLE over-the-air updates
- ✅ **Air-Gapped Mode**: Full offline operation
- ✅ **Digital Twin Integration**: Real-time monitoring
- ✅ **Multi-Device Support**: Manage multiple devices
- ✅ **Integration Code Gen**: Python and C/C++ code generation

## Documentation

- **Full Guide**: [MESHTASTIC_INTEGRATION.md](MESHTASTIC_INTEGRATION.md)
- **API Reference**: See inline documentation
- **Examples**: [examples/](examples/)

## Need Help?

1. Check the [full documentation](MESHTASTIC_INTEGRATION.md)
2. Run the examples to see working code
3. Review test cases in `tests/test_meshtastic.py`

## Regional Frequency Settings

| Region | Frequency Band |
|--------|---------------|
| US | 915 MHz |
| EU_868 | 868 MHz |
| EU_433 | 433 MHz |
| CN | 470-510 MHz |
| JP | 920 MHz |
| ANZ | 915-928 MHz |

## Modem Presets

| Preset | Range | Bandwidth | Use Case |
|--------|-------|-----------|----------|
| LONG_FAST | High | Medium | General use, good balance |
| LONG_SLOW | Very High | Low | Maximum range, slow updates |
| MEDIUM_FAST | Medium | High | Faster messaging, shorter range |
| SHORT_FAST | Low | Very High | High bandwidth, short range |

## Next Steps

1. ✅ Read the [full documentation](MESHTASTIC_INTEGRATION.md)
2. ✅ Run the demo scripts
3. ✅ Try the digital twin integration
4. ✅ Configure your own Meshtastic device
5. ✅ Explore the API reference

Happy meshing! 🌐📡
