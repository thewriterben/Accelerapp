# Meshtastic Quick Start Guide

Get started with Meshtastic mesh networking in Accelerapp in under 5 minutes!

## Installation

```bash
# Clone and install Accelerapp
git clone https://github.com/thewriterben/Accelerapp.git
cd Accelerapp
pip install -e .
```

## Quick Examples

### 1. Generate Your First Meshtastic Node

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent
from pathlib import Path

# Initialize agent
agent = MeshtasticAgent()

# Generate ESP32 Meshtastic node
result = agent.generate({
    "task_type": "generate",
    "platform": "esp32",
    "device_name": "MyFirstNode",
    "features": ["wifi", "gps"]
})

# Save files
output_dir = Path("./my_meshtastic_node")
output_dir.mkdir(exist_ok=True)

for filename, content in result["files"].items():
    (output_dir / filename).write_text(content)

print(f"✓ Project generated in {output_dir}")
```

### 2. Discover Meshtastic Devices

```python
from accelerapp.meshtastic.device_interface import DeviceDiscovery

# Find all connected devices
devices = DeviceDiscovery.discover_all()

print(f"Found {len(devices)} device(s):")
for device in devices:
    print(f"  - {device.hardware_model} on {device.port or device.ip_address}")
```

### 3. Manage Firmware

```python
from accelerapp.meshtastic.firmware_manager import FirmwareManager
from pathlib import Path

# Initialize manager
manager = FirmwareManager()

# Add firmware to repository
firmware = manager.add_firmware(
    firmware_file=Path("firmware-2.3.0.bin"),
    version="2.3.0",
    hardware_model="TTGO T-Beam",
    platform="esp32"
)

# Get latest firmware
latest = manager.get_latest_firmware("TTGO T-Beam", "esp32")
print(f"Latest version: {latest.version}")
```

### 4. Build a Mesh Network

```python
from accelerapp.meshtastic.network_manager import (
    MeshNetworkManager,
    MeshNode,
    NodeStatus
)

# Create network manager
manager = MeshNetworkManager()

# Add nodes
gateway = MeshNode("!12345678", "GW", "Gateway", "TTGO T-Beam", "2.3.0", NodeStatus.ONLINE)
field_node = MeshNode("!23456789", "FN", "Field Node", "TTGO T-Beam", "2.3.0", NodeStatus.ONLINE)

manager.update_node(gateway)
manager.update_node(field_node)

# Connect nodes
manager.update_connection("!12345678", "!23456789")

# Send message
result = manager.send_message("!12345678", "!23456789", "Hello from gateway")
print(f"Message sent: {result['status']}")
```

### 5. Perform OTA Update

```python
from accelerapp.meshtastic.ota_controller import OTAController, OTAMethod
from pathlib import Path

# Initialize controller
controller = OTAController()

# Start WiFi OTA update
progress = controller.start_update(
    device_id="!12345678",
    firmware_path=Path("firmware-2.3.0.bin"),
    method=OTAMethod.WIFI,
    device_info={"ip_address": "192.168.1.100"}
)

# Check progress
current = controller.get_progress("!12345678")
print(f"Update progress: {current.progress_percent:.1f}%")
```

## Generate Complete Project

Using the platform directly for a complete PlatformIO project:

```python
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform
from pathlib import Path

# Initialize platform
platform = MeshtasticESP32Platform()

# Generate complete project
result = platform.generate_code(
    spec={
        "device_name": "FieldSensor",
        "features": ["wifi", "gps"],
        "radio_config": {
            "frequency": 915.0,
            "bandwidth": 125.0,
            "spreading_factor": 7,
            "power": 20
        }
    },
    output_dir=Path("./field_sensor")
)

print(f"Project ready in: {result['output_dir']}")
print("Build with: cd field_sensor && pio run")
```

## Configuration File

Create `meshtastic_config.yaml`:

```yaml
device_name: "MyNode"
platform: "meshtastic-esp32"

hardware:
  board: "TTGO T-Beam v1.1"
  lora_radio:
    frequency: 915.0
    spreading_factor: 7
    output_power: 20

mesh:
  region: "US"
  hop_limit: 3

features:
  wifi:
    enabled: true
  gps:
    enabled: true
  bluetooth:
    enabled: true
```

Then generate from config:

```python
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform
import yaml
from pathlib import Path

# Load configuration
with open("meshtastic_config.yaml") as f:
    config = yaml.safe_load(f)

# Generate project
platform = MeshtasticESP32Platform()
result = platform.generate_code(config, Path("./output"))
```

## Run the Demo

See everything in action:

```bash
python examples/meshtastic_demo.py
```

This demonstrates:
- Device discovery
- Firmware management
- Network operations
- OTA updates
- Code generation

## Air-Gapped Setup

For offline/air-gapped environments:

```python
from accelerapp.meshtastic.firmware_manager import FirmwareManager
from pathlib import Path

# On connected system: Download and package firmware
manager = FirmwareManager(firmware_dir=Path("./firmware_repo"))

# Add firmware files
for fw_file in Path("./downloads").glob("*.bin"):
    manager.add_firmware(
        firmware_file=fw_file,
        version="2.3.0",
        hardware_model="TTGO T-Beam",
        platform="esp32"
    )

# Transfer firmware_repo directory to air-gapped system
# On air-gapped system: Use the local repository
manager = FirmwareManager(firmware_dir=Path("./firmware_repo"))
firmware_list = manager.list_firmware()  # All available offline!
```

## Next Steps

1. **Read the full documentation**: [MESHTASTIC_INTEGRATION.md](../MESHTASTIC_INTEGRATION.md)
2. **Explore examples**: Check `examples/` directory
3. **View API reference**: See docstrings in source code
4. **Run tests**: `pytest tests/test_meshtastic.py -v`

## Common Tasks

### Check Agent Capabilities

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

agent = MeshtasticAgent()
info = agent.get_info()

print("Capabilities:", info['capabilities'])
print("Platforms:", list(info['supported_platforms'].keys()))
```

### Export Network Topology

```python
manager = MeshNetworkManager()
# ... add nodes and connections ...
manager.export_topology("network.json")
```

### Validate Configuration

```python
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform

platform = MeshtasticESP32Platform()
config = {
    "radio_config": {
        "frequency": 915.0,
        "spreading_factor": 7,
        "power": 20
    }
}

errors = platform.validate_config(config)
if errors:
    print("Configuration errors:", errors)
else:
    print("✓ Configuration valid")
```

## Troubleshooting

**Device not found?**
```python
# List all serial ports
import serial.tools.list_ports
for port in serial.tools.list_ports.comports():
    print(f"{port.device}: {port.product}")
```

**Firmware checksum mismatch?**
```python
manager = FirmwareManager()
firmware = manager.get_latest_firmware("TTGO T-Beam", "esp32")
is_valid = manager.verify_firmware(firmware)
print(f"Firmware valid: {is_valid}")
```

## Support

- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: [MESHTASTIC_INTEGRATION.md](../MESHTASTIC_INTEGRATION.md)
- Examples: `examples/` directory

---

**Happy Meshing!** 🌐✨
