# Quick Start Guide

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- USB access permissions (Linux/macOS)

### Install Accelerapp

```bash
pip install accelerapp
```

### Hardware Setup

#### ESP32 Marauder

1. **Flash Marauder Firmware**
   - Download from: https://github.com/justcallmekoko/ESP32Marauder
   - Flash using ESP Flash Tool or esptool
   - Connect via USB

2. **Verify Connection**
   ```bash
   # Linux
   ls /dev/ttyUSB*
   
   # macOS
   ls /dev/cu.usbserial*
   
   # Windows
   # Check Device Manager for COM ports
   ```

#### Flipper Zero

1. **Update Firmware**
   - Use official Flipper mobile app
   - Or qFlipper desktop app
   - Ensure latest stable firmware

2. **Connect Device**
   - Connect via USB-C cable
   - Device should appear as serial port

### Permissions (Linux)

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Create udev rules
sudo nano /etc/udev/rules.d/99-hardware.rules
```

Add these rules:
```
# ESP32 devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", MODE="0666"

# Flipper Zero
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"
```

Reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Log out and back in for group changes to take effect.

## First Steps

### 1. Device Discovery

```python
import asyncio
from accelerapp.hardware import ESP32Marauder, FlipperZero

# Discover ESP32 Marauder devices
marauder_devices = ESP32Marauder.discover_devices()
print(f"Found {len(marauder_devices)} ESP32 Marauder device(s)")

# Discover Flipper Zero devices
flipper_devices = FlipperZero.discover_devices()
print(f"Found {len(flipper_devices)} Flipper Zero device(s)")
```

### 2. Connect to Device

```python
# ESP32 Marauder
marauder = ESP32Marauder(port="/dev/ttyUSB0")
if marauder.connect():
    print("Connected to ESP32 Marauder")
    
# Flipper Zero
flipper = FlipperZero(port="/dev/ttyACM0")
if flipper.connect():
    print("Connected to Flipper Zero")
```

### 3. Basic WiFi Scan

```python
async def scan_wifi():
    marauder = ESP32Marauder()
    if not marauder.connect():
        print("Failed to connect")
        return
    
    # Scan for 10 seconds
    networks = await marauder.scan_wifi_networks(duration=10.0)
    
    print(f"Found {len(networks)} networks:")
    for network in networks:
        print(f"  {network.ssid} ({network.bssid})")
        print(f"    Channel: {network.channel}")
        print(f"    RSSI: {network.rssi} dBm")
        print(f"    Encryption: {network.encryption}")
    
    marauder.disconnect()

asyncio.run(scan_wifi())
```

### 4. Basic RFID Read

```python
async def read_rfid():
    flipper = FlipperZero()
    if not flipper.connect():
        print("Failed to connect")
        return
    
    print("Hold RFID tag near Flipper Zero...")
    
    # Read for 10 seconds
    tag = await flipper.read_rfid_125khz(duration=10.0)
    
    if tag:
        print(f"Tag detected!")
        print(f"  Type: {tag.tag_type}")
        print(f"  UID: {tag.uid}")
    else:
        print("No tag detected")
    
    flipper.disconnect()

asyncio.run(read_rfid())
```

### 5. Unified Hardware Manager

```python
async def unified_demo():
    from accelerapp.managers import HardwareManager
    
    # Create manager
    manager = HardwareManager()
    
    # Auto-discover all devices
    devices = await manager.discover_devices()
    print(f"Discovered {len(devices)} device(s)")
    
    # Connect to all devices
    for device in devices:
        await manager.connect_device(device.device_id)
    
    # Perform unified scan
    results = await manager.unified_scan(duration=10.0)
    
    print(f"Scan Results:")
    print(f"  WiFi Networks: {len(results.wifi_networks)}")
    print(f"  Bluetooth Devices: {len(results.bluetooth_devices)}")
    print(f"  RFID Tags: {len(results.rfid_tags)}")
    print(f"  NFC Tags: {len(results.nfc_tags)}")
    
    # Cleanup
    await manager.shutdown()

asyncio.run(unified_demo())
```

## Common Tasks

### WiFi Network Analysis

```python
async def analyze_wifi():
    marauder = ESP32Marauder()
    marauder.connect()
    
    networks = await marauder.scan_wifi_networks(duration=30.0)
    
    # Find networks by encryption
    wep_networks = [n for n in networks if "WEP" in n.encryption]
    print(f"WEP networks (vulnerable): {len(wep_networks)}")
    
    # Find strongest signals
    sorted_by_rssi = sorted(networks, key=lambda n: n.rssi, reverse=True)
    print(f"Strongest signal: {sorted_by_rssi[0].ssid} ({sorted_by_rssi[0].rssi} dBm)")
    
    marauder.disconnect()

asyncio.run(analyze_wifi())
```

### Bluetooth Device Discovery

```python
async def discover_bluetooth():
    marauder = ESP32Marauder()
    marauder.connect()
    
    devices = await marauder.scan_bluetooth_devices(duration=30.0)
    
    print(f"Found {len(devices)} Bluetooth device(s):")
    for device in devices:
        print(f"  {device.name} ({device.address})")
        print(f"    Type: {device.device_type}")
        print(f"    RSSI: {device.rssi} dBm")
    
    marauder.disconnect()

asyncio.run(discover_bluetooth())
```

### NFC Tag Reading

```python
async def read_nfc():
    flipper = FlipperZero()
    flipper.connect()
    
    print("Hold NFC tag near Flipper Zero...")
    tag = await flipper.read_nfc(duration=10.0)
    
    if tag:
        print(f"NFC Tag detected!")
        print(f"  Type: {tag.tag_type}")
        print(f"  UID: {tag.uid}")
        print(f"  ATQA: {tag.atqa}")
        print(f"  SAK: {tag.sak}")
        
        if tag.ndef_records:
            print(f"  NDEF Records: {len(tag.ndef_records)}")
    
    flipper.disconnect()

asyncio.run(read_nfc())
```

## Configuration

### Basic Configuration

Create `config/hardware_devices.yaml`:

```yaml
devices:
  esp32_marauder:
    enabled: true
    auto_discover: true
    baudrate: 115200
    
  flipper_zero:
    enabled: true
    auto_discover: true
    baudrate: 230400

hardware_manager:
  auto_discovery_enabled: true
  auto_reconnect: true
```

### Load Configuration

```python
import yaml
from accelerapp.managers import HardwareManager

# Load config
with open('config/hardware_devices.yaml') as f:
    config = yaml.safe_load(f)

# Create manager with config
manager = HardwareManager()
```

## Troubleshooting

### Device Not Found

```python
# Check for all serial devices
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")
```

### Connection Timeout

```python
# Increase timeout
marauder = ESP32Marauder(timeout=10.0)
flipper = FlipperZero(timeout=10.0)
```

### Permission Denied

```bash
# Check permissions
ls -l /dev/ttyUSB0

# Add to group (Linux)
sudo usermod -a -G dialout $USER

# Logout and login again
```

## Next Steps

1. Review [Security Best Practices](security.md)
2. Explore [Example Scripts](../../examples/)
3. Read [API Reference](api_reference.md)
4. Join community discussions

## Getting Help

- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides and API docs
- Examples: Working code samples
- Community: Discussion forums and chat

## Important Reminders

⚠️ **Always ensure you have proper authorization before testing any networks or devices**

⚠️ **Enable audit logging for accountability**

⚠️ **Follow ethical hacking guidelines**

⚠️ **Comply with local laws and regulations**
