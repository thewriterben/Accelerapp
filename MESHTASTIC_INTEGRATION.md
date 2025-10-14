# Meshtastic Integration Guide

## Overview

Accelerapp now provides comprehensive Meshtastic mesh communication support, enabling you to program, configure, monitor, and manage Meshtastic devices in both connected and air-gapped environments.

## Features

### Core Capabilities

- **Device Discovery**: Automatic detection via Serial, WiFi, and Bluetooth
- **Firmware Management**: Local repository with version control and validation
- **Network Management**: Real-time topology mapping and routing
- **OTA Updates**: WiFi, Bluetooth, and Serial firmware updates
- **Code Generation**: Platform-specific firmware for ESP32 and nRF52
- **Air-Gapped Support**: Complete offline operation capability

### Supported Hardware

- **ESP32**: TTGO T-Beam, LILYGO devices, Heltec LoRa boards
- **nRF52/nRF52840**: RAK4631, custom Nordic-based devices
- **RP2040**: Raspberry Pi Pico with LoRa modules (upcoming)

### LoRa Radio Support

- **SX1276/SX1278**: 433MHz, 868MHz, 915MHz
- **SX1262/SX1268**: 868MHz, 915MHz (higher performance)

## Installation

The Meshtastic integration is included in Accelerapp. Ensure you have the latest version:

```bash
pip install -e .
```

For serial device access, you may need:

```bash
# Linux
sudo usermod -a -G dialout $USER

# macOS - no additional setup needed

# Windows - install USB drivers for your device
```

## Quick Start

### Device Discovery

```python
from accelerapp.meshtastic.device_interface import DeviceDiscovery

# Discover all devices
devices = DeviceDiscovery.discover_all()

for device in devices:
    print(f"Found: {device.device_id}")
    print(f"  Type: {device.connection_type.value}")
    print(f"  Hardware: {device.hardware_model}")
```

### Firmware Management

```python
from accelerapp.meshtastic.firmware_manager import FirmwareManager
from pathlib import Path

# Initialize manager
manager = FirmwareManager()

# Add firmware to local repository
firmware = manager.add_firmware(
    firmware_file=Path("meshtastic-2.3.0.bin"),
    version="2.3.0",
    hardware_model="TTGO T-Beam",
    platform="esp32"
)

# List available firmware
firmware_list = manager.list_firmware(hardware_model="TTGO T-Beam")

# Get latest firmware
latest = manager.get_latest_firmware("TTGO T-Beam", "esp32")
print(f"Latest version: {latest.version}")
```

### Network Management

```python
from accelerapp.meshtastic.network_manager import (
    MeshNetworkManager,
    MeshNode,
    NodeStatus
)

# Initialize network manager
manager = MeshNetworkManager()

# Add nodes to network
node1 = MeshNode(
    node_id="!12345678",
    short_name="GW",
    long_name="Gateway",
    hardware_model="TTGO T-Beam",
    firmware_version="2.3.0",
    status=NodeStatus.ONLINE
)

manager.update_node(node1)

# Create connections
manager.update_connection("!12345678", "!23456789")

# Get network statistics
stats = manager.get_network_stats()
print(f"Network has {stats['total_nodes']} nodes")

# Find route between nodes
route = manager.find_route("!12345678", "!23456789")
print(f"Route: {' -> '.join(route)}")

# Send message
result = manager.send_message("!12345678", "!23456789", "Hello")
print(f"Message sent: {result['status']}")
```

### OTA Firmware Updates

```python
from accelerapp.meshtastic.ota_controller import OTAController, OTAMethod
from pathlib import Path

# Initialize OTA controller
controller = OTAController()

# Start WiFi OTA update
progress = controller.start_update(
    device_id="!12345678",
    firmware_path=Path("firmware.bin"),
    method=OTAMethod.WIFI,
    device_info={"ip_address": "192.168.1.100"}
)

# Monitor progress
current_progress = controller.get_progress("!12345678")
if current_progress:
    print(f"Progress: {current_progress.progress_percent:.1f}%")
    print(f"Status: {current_progress.status}")

# Get update history
history = controller.get_update_history(device_id="!12345678")
```

### Code Generation with Agent

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

# Initialize agent
agent = MeshtasticAgent()

# Generate Meshtastic node code
result = agent.generate({
    "task_type": "generate",
    "platform": "esp32",
    "device_name": "MyMeshtasticNode",
    "features": ["wifi", "gps", "bluetooth"]
})

if result["status"] == "success":
    # Save generated files
    for filename, content in result["files"].items():
        with open(filename, "w") as f:
            f.write(content)
```

### Platform-Specific Generation

```python
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform
from pathlib import Path

# Initialize platform
platform = MeshtasticESP32Platform()

# Generate complete project
result = platform.generate_code(
    spec={
        "device_name": "FieldNode",
        "features": ["wifi", "gps"],
        "radio_config": {
            "frequency": 915.0,  # MHz
            "bandwidth": 125.0,  # kHz
            "spreading_factor": 7,
            "power": 20  # dBm
        }
    },
    output_dir=Path("./my_meshtastic_node")
)

print(f"Project generated in: {result['output_dir']}")
```

## Air-Gapped Deployment

### Preparing for Air-Gapped Environment

1. **Download firmware on connected system**:

```bash
# Create firmware package
mkdir -p firmware_package
cd firmware_package

# Download official firmware
wget https://github.com/meshtastic/firmware/releases/download/v2.3.0/firmware-esp32-2.3.0.bin
wget https://github.com/meshtastic/firmware/releases/download/v2.3.0/firmware-nrf52-2.3.0.bin

# Package for transfer
tar czf meshtastic_firmware.tar.gz *.bin
```

2. **Transfer to air-gapped system**:

```bash
# On air-gapped system
tar xzf meshtastic_firmware.tar.gz

# Add to Accelerapp firmware repository
python3 << EOF
from accelerapp.meshtastic.firmware_manager import FirmwareManager
from pathlib import Path

manager = FirmwareManager()

for fw_file in Path(".").glob("*.bin"):
    # Extract metadata from filename
    parts = fw_file.stem.split("-")
    manager.add_firmware(
        firmware_file=fw_file,
        version="2.3.0",
        hardware_model=parts[1],
        platform=parts[1]
    )
EOF
```

3. **Use in air-gapped environment**:

```python
from accelerapp.meshtastic.firmware_manager import FirmwareManager

# All firmware is now available locally
manager = FirmwareManager()
firmware_list = manager.list_firmware()

print(f"Available firmware (offline): {len(firmware_list)} versions")
```

## Advanced Features

### Custom Firmware Builds

```python
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform

platform = MeshtasticESP32Platform()

# Generate custom firmware
result = platform.generate_code(
    spec={
        "device_name": "CustomNode",
        "features": ["wifi", "gps", "environment"],
        "radio_config": {
            "frequency": 915.0,
            "bandwidth": 125.0,
            "spreading_factor": 7,
            "coding_rate": 5,
            "sync_word": 0x12,
            "power": 20,
            "max_hops": 3,
            "beacon_interval_ms": 60000
        }
    },
    output_dir=Path("./custom_firmware")
)

# Build with PlatformIO
# cd custom_firmware
# pio run
```

### Network Topology Visualization

```python
from accelerapp.meshtastic.network_manager import MeshNetworkManager

manager = MeshNetworkManager()

# Build network
# ... add nodes and connections ...

# Export topology for visualization
manager.export_topology("network_topology.json")

# The JSON file can be imported into visualization tools
# or processed with your own visualization code
```

### Batch Device Configuration

```python
from accelerapp.agents.meshtastic_agent import MeshtasticAgent

agent = MeshtasticAgent()

# Configure multiple devices
device_configs = [
    {"device_id": "!12345678", "region": "US", "role": "gateway"},
    {"device_id": "!23456789", "region": "US", "role": "router"},
    {"device_id": "!34567890", "region": "US", "role": "client"},
]

for config in device_configs:
    result = agent.generate({
        "task_type": "configure",
        "device_id": config["device_id"],
        "config": {
            "region": config["region"],
            "lora": {
                "region": config["region"],
                "hop_limit": 3
            }
        }
    })
    print(f"Configured {config['device_id']}: {result['status']}")
```

## Integration with Accelerapp Features

### Digital Twin Integration

```python
from accelerapp.digital_twin.device_twin import DeviceTwin
from accelerapp.meshtastic.device_interface import DeviceInfo, ConnectionType

# Create digital twin for Meshtastic device
device_info = DeviceInfo(
    device_id="!12345678",
    connection_type=ConnectionType.SERIAL,
    port="/dev/ttyUSB0",
    hardware_model="TTGO T-Beam",
    firmware_version="2.3.0"
)

twin = DeviceTwin(
    device_id=device_info.device_id,
    device_type="meshtastic_node",
    metadata=device_info.to_dict()
)

# Sync state
twin.update_state({
    "status": "online",
    "battery_level": 85,
    "signal_strength": -75,
    "last_heard": "2025-10-14T22:00:00Z"
})

# Query twin
state = twin.get_state()
print(f"Device battery: {state['battery_level']}%")
```

### Security Integration

```python
from accelerapp.security.network_segmentation import (
    NetworkSegmentationService,
    NetworkZone,
    Protocol
)

# Create secure mesh network segment
security = NetworkSegmentationService()

# Create segment for Meshtastic devices
segment = security.create_segment(
    segment_id="mesh_network",
    zone=NetworkZone.INTERNAL,
    description="Meshtastic mesh network devices"
)

# Assign devices to segment
security.assign_device_to_segment("!12345678", "mesh_network")
security.assign_device_to_segment("!23456789", "mesh_network")

# Create communication policy
policy = security.create_policy(
    policy_id="mesh_communication",
    source_device="!12345678",
    destination_device="!23456789",
    allowed_protocols=[Protocol.UDP],
    allowed_ports=[4403]  # Meshtastic default port
)
```

## Troubleshooting

### Device Not Detected

```python
from accelerapp.meshtastic.device_interface import DeviceDiscovery

# Check USB permissions (Linux)
import os
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Port: {port.device}")
    print(f"  Manufacturer: {port.manufacturer}")
    print(f"  Product: {port.product}")
    print(f"  VID:PID: {port.vid:04X}:{port.pid:04X}")
```

### Firmware Update Failed

```python
from accelerapp.meshtastic.firmware_manager import FirmwareManager

manager = FirmwareManager()

# Verify firmware integrity
firmware = manager.get_latest_firmware("TTGO T-Beam", "esp32")
is_valid = manager.verify_firmware(firmware)

if not is_valid:
    print("Firmware checksum mismatch - redownload required")
else:
    print("Firmware is valid")
```

### Network Route Not Found

```python
from accelerapp.meshtastic.network_manager import MeshNetworkManager

manager = MeshNetworkManager()

# Check network topology
topology = manager.get_topology()
print(f"Network has {len(topology.nodes)} nodes")
print(f"Network has {len(topology.edges)} connections")

# Check if both nodes exist
source_node = topology.get_node("!12345678")
dest_node = topology.get_node("!23456789")

if not source_node:
    print("Source node not in network")
if not dest_node:
    print("Destination node not in network")

# Find alternative routes
# ... implement custom routing logic ...
```

## Examples

### Complete Demo

Run the comprehensive demo:

```bash
python examples/meshtastic_demo.py
```

This demonstrates:
- Device discovery
- Firmware management
- Network operations
- OTA updates
- Code generation
- Agent capabilities

## API Reference

### Device Interface

- `DeviceDiscovery.discover_serial()` - Discover serial devices
- `DeviceDiscovery.discover_wifi()` - Discover WiFi devices
- `DeviceDiscovery.discover_bluetooth()` - Discover Bluetooth devices
- `DeviceDiscovery.discover_all()` - Discover all devices
- `MeshtasticDevice.connect()` - Connect to device
- `MeshtasticDevice.send_command()` - Send command to device
- `MeshtasticDevice.configure_channel()` - Configure mesh channel

### Firmware Manager

- `FirmwareManager.list_firmware()` - List available firmware
- `FirmwareManager.get_latest_firmware()` - Get latest version
- `FirmwareManager.add_firmware()` - Add firmware to repository
- `FirmwareManager.verify_firmware()` - Verify firmware integrity
- `FirmwareManager.delete_firmware()` - Remove firmware

### Network Manager

- `MeshNetworkManager.update_node()` - Add/update network node
- `MeshNetworkManager.update_connection()` - Add node connection
- `MeshNetworkManager.get_topology()` - Get network topology
- `MeshNetworkManager.get_network_stats()` - Get statistics
- `MeshNetworkManager.find_route()` - Find route between nodes
- `MeshNetworkManager.send_message()` - Send mesh message

### OTA Controller

- `OTAController.start_update()` - Start firmware update
- `OTAController.get_progress()` - Get update progress
- `OTAController.cancel_update()` - Cancel ongoing update
- `OTAController.get_update_history()` - Get update history
- `OTAController.register_progress_callback()` - Register progress callback

### Meshtastic Agent

- `MeshtasticAgent.generate()` - Generate code/configuration
- `MeshtasticAgent.can_handle()` - Check task capability
- `MeshtasticAgent.get_platform_support()` - Get supported platforms
- `MeshtasticAgent.get_info()` - Get agent information

## Best Practices

1. **Always verify firmware** before flashing to devices
2. **Use air-gapped mode** for sensitive deployments
3. **Monitor network topology** regularly for optimal routing
4. **Keep firmware updated** for security and features
5. **Test updates** on a single device before batch deployment
6. **Document your mesh network** configuration and topology
7. **Use encryption** for all mesh communications
8. **Monitor battery levels** on remote nodes
9. **Plan radio frequencies** for your region (compliance)
10. **Keep backups** of firmware and configurations

## Contributing

To extend Meshtastic support:

1. Add new hardware platforms in `src/accelerapp/platforms/`
2. Implement new features in `src/accelerapp/meshtastic/`
3. Add tests in `tests/test_meshtastic.py`
4. Update documentation

## Support

For issues or questions:

- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Meshtastic Documentation: https://meshtastic.org/docs
- Accelerapp Documentation: See README.md

## License

MIT License - See LICENSE file for details

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Status**: Production Ready
