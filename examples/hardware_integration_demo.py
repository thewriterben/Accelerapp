"""
ESP32 Marauder and Flipper Zero Integration Demo

Demonstrates the usage of hardware integration features including:
- Device discovery
- WiFi and Bluetooth scanning
- RFID/NFC reading
- Unified hardware management
- Coordinated multi-device operations
"""

import asyncio
import logging
from accelerapp.hardware import ESP32Marauder, FlipperZero
from accelerapp.managers import HardwareManager, DeviceCapability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_esp32_marauder():
    """Demonstrate ESP32 Marauder capabilities."""
    print("\n" + "=" * 60)
    print("ESP32 MARAUDER DEMO")
    print("=" * 60)
    
    # Discover devices
    print("\n1. Discovering ESP32 Marauder devices...")
    devices = ESP32Marauder.discover_devices()
    print(f"   Found {len(devices)} device(s)")
    for device in devices:
        print(f"   - {device['port']}: {device['description']}")
    
    if not devices:
        print("   ⚠ No devices found. Skipping connection demo.")
        return
    
    # Create marauder instance
    print("\n2. Creating ESP32 Marauder instance...")
    marauder = ESP32Marauder(
        port=devices[0]['port'],
        baudrate=115200,
        timeout=5.0,
    )
    print(f"   ✓ Instance created")
    
    # Get device info
    info = marauder.get_device_info()
    print(f"\n3. Device Information:")
    print(f"   Port: {info['port']}")
    print(f"   Connected: {info['is_connected']}")
    print(f"   Scanning: {info['is_scanning']}")
    
    # Note: Actual connection and scanning would require hardware
    print("\n4. WiFi Scanning (simulated)")
    print("   In production, this would:")
    print("   - Scan for WiFi networks")
    print("   - Detect SSIDs, BSSIDs, channels")
    print("   - Measure signal strength (RSSI)")
    print("   - Identify encryption types")
    
    print("\n5. Bluetooth Scanning (simulated)")
    print("   In production, this would:")
    print("   - Discover BLE devices")
    print("   - Read device names and addresses")
    print("   - Measure signal strength")
    print("   - Identify services")
    
    print("\n6. Security Features")
    print("   ⚠ Penetration testing capabilities require:")
    print("   - Proper authorization")
    print("   - Ethical compliance")
    print("   - Legal permissions")
    print("   - Audit logging enabled")


async def demo_flipper_zero():
    """Demonstrate Flipper Zero capabilities."""
    print("\n" + "=" * 60)
    print("FLIPPER ZERO DEMO")
    print("=" * 60)
    
    # Discover devices
    print("\n1. Discovering Flipper Zero devices...")
    devices = FlipperZero.discover_devices()
    print(f"   Found {len(devices)} device(s)")
    for device in devices:
        print(f"   - {device['port']}: {device['description']}")
    
    if not devices:
        print("   ⚠ No devices found. Skipping connection demo.")
        return
    
    # Create flipper instance
    print("\n2. Creating Flipper Zero instance...")
    flipper = FlipperZero(
        port=devices[0]['port'],
        baudrate=230400,
        timeout=5.0,
    )
    print(f"   ✓ Instance created")
    
    # Get device info
    info = flipper.get_device_info()
    print(f"\n3. Device Information:")
    print(f"   Port: {info['port']}")
    print(f"   Connected: {info['is_connected']}")
    print(f"   Reading: {info['is_reading']}")
    
    # Note: Actual operations would require hardware
    print("\n4. RFID Reading (simulated)")
    print("   In production, this would:")
    print("   - Read 125kHz RFID tags")
    print("   - Read high-frequency RFID")
    print("   - Extract UID and data")
    print("   - Support multiple protocols")
    
    print("\n5. NFC Operations (simulated)")
    print("   In production, this would:")
    print("   - Detect NFC tags")
    print("   - Read NDEF records")
    print("   - Support Mifare, NTAG, etc.")
    print("   - Extract card information")
    
    print("\n6. Sub-GHz Operations (simulated)")
    print("   In production, this would:")
    print("   - Receive signals (315/433/915 MHz)")
    print("   - Analyze protocols")
    print("   - Decode remote controls")
    print("   - Capture garage door openers")
    
    print("\n7. Infrared Operations (simulated)")
    print("   In production, this would:")
    print("   - Learn IR remote codes")
    print("   - Replay IR signals")
    print("   - Control TVs, ACs, etc.")
    print("   - Support multiple protocols")
    
    print("\n8. GPIO Control (simulated)")
    print("   In production, this would:")
    print("   - Control GPIO pins")
    print("   - Read digital inputs")
    print("   - Interface with external devices")
    print("   - Support I2C, SPI, UART")


async def demo_unified_hardware_manager():
    """Demonstrate unified hardware management."""
    print("\n" + "=" * 60)
    print("UNIFIED HARDWARE MANAGER DEMO")
    print("=" * 60)
    
    # Create manager
    print("\n1. Creating Hardware Manager...")
    manager = HardwareManager()
    print("   ✓ Manager created")
    
    # Discover all devices
    print("\n2. Discovering all hardware devices...")
    discovered = await manager.discover_devices()
    print(f"   Found {len(discovered)} device(s) total")
    for device in discovered:
        print(f"   - {device.device_id} ({device.device_type.value})")
        caps = [cap.value for cap in device.capabilities]
        print(f"     Capabilities: {', '.join(caps)}")
    
    if not discovered:
        print("   ⚠ No devices found.")
    
    # Get available capabilities
    print("\n3. Available Capabilities Across All Devices:")
    capabilities = manager.get_capabilities()
    for cap in sorted(capabilities, key=lambda x: x.value):
        print(f"   - {cap.value}")
    
    # Unified scan demo
    print("\n4. Unified Scanning (simulated)")
    print("   In production, this would:")
    print("   - Coordinate scans across all devices")
    print("   - Run operations in parallel")
    print("   - Aggregate results")
    print("   - Deduplicate findings")
    
    # Get manager status
    status = manager.get_status()
    print(f"\n5. Manager Status:")
    print(f"   Total devices: {status['total_devices']}")
    print(f"   Connected devices: {status['connected_devices']}")
    print(f"   Busy devices: {status['busy_devices']}")
    
    # Cleanup
    await manager.shutdown()
    print("\n6. Manager shutdown complete")


async def demo_coordinated_operations():
    """Demonstrate coordinated multi-device operations."""
    print("\n" + "=" * 60)
    print("COORDINATED OPERATIONS DEMO")
    print("=" * 60)
    
    manager = HardwareManager()
    
    print("\n1. Setting up event callbacks...")
    
    def on_device_connected(device):
        print(f"   📱 Device connected: {device.device_id}")
    
    def on_scan_complete(results):
        print(f"   ✓ Scan complete!")
        print(f"     WiFi networks: {len(results.wifi_networks)}")
        print(f"     Bluetooth devices: {len(results.bluetooth_devices)}")
        print(f"     RFID tags: {len(results.rfid_tags)}")
        print(f"     NFC tags: {len(results.nfc_tags)}")
        print(f"     Devices used: {', '.join(results.devices_used)}")
    
    def on_error(error):
        print(f"   ⚠ Error: {error}")
    
    manager.add_callback("device_connected", on_device_connected)
    manager.add_callback("scan_complete", on_scan_complete)
    manager.add_callback("error", on_error)
    
    print("   ✓ Callbacks registered")
    
    print("\n2. Coordinated Scanning Strategy:")
    print("   - ESP32 Marauder: WiFi + Bluetooth scanning")
    print("   - Flipper Zero: RFID + NFC reading")
    print("   - Parallel execution for efficiency")
    print("   - Real-time result aggregation")
    
    print("\n3. Security Considerations:")
    print("   - All operations logged for audit")
    print("   - Authorization required for attacks")
    print("   - Rate limiting enforced")
    print("   - Ethical compliance checks")
    
    await manager.shutdown()


async def demo_practical_use_cases():
    """Demonstrate practical use cases."""
    print("\n" + "=" * 60)
    print("PRACTICAL USE CASES")
    print("=" * 60)
    
    print("\n1. Network Security Assessment")
    print("   Use case: Audit WiFi network security")
    print("   Tools: ESP32 Marauder")
    print("   Operations:")
    print("   - Scan for rogue access points")
    print("   - Test WPA/WPA2 encryption")
    print("   - Identify weak configurations")
    print("   - Monitor for deauth attacks")
    
    print("\n2. IoT Device Testing")
    print("   Use case: Test IoT device security")
    print("   Tools: ESP32 Marauder + Flipper Zero")
    print("   Operations:")
    print("   - Scan for WiFi/BLE vulnerabilities")
    print("   - Test RFID authentication")
    print("   - Analyze Sub-GHz communications")
    print("   - Test physical access controls")
    
    print("\n3. Physical Security Assessment")
    print("   Use case: Test building access systems")
    print("   Tools: Flipper Zero")
    print("   Operations:")
    print("   - Read RFID badge systems")
    print("   - Test NFC door locks")
    print("   - Analyze garage door security")
    print("   - Test IR-based controls")
    
    print("\n4. Red Team Operations")
    print("   Use case: Penetration testing engagements")
    print("   Tools: Both devices coordinated")
    print("   Operations:")
    print("   - Comprehensive wireless assessment")
    print("   - Physical access testing")
    print("   - Social engineering support")
    print("   - Documentation and reporting")
    
    print("\n5. Research and Development")
    print("   Use case: Wireless protocol research")
    print("   Tools: Both devices")
    print("   Operations:")
    print("   - Capture and analyze signals")
    print("   - Reverse engineer protocols")
    print("   - Test custom implementations")
    print("   - Develop security improvements")


async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("HARDWARE INTEGRATION DEMONSTRATION")
    print("ESP32 Marauder & Flipper Zero")
    print("=" * 60)
    
    try:
        await demo_esp32_marauder()
        await demo_flipper_zero()
        await demo_unified_hardware_manager()
        await demo_coordinated_operations()
        await demo_practical_use_cases()
        
        print("\n" + "=" * 60)
        print("ALL DEMONSTRATIONS COMPLETED!")
        print("=" * 60)
        
        print("\n📖 For more information, see:")
        print("   - docs/hardware/esp32_marauder.md")
        print("   - docs/hardware/flipper_zero.md")
        print("   - docs/hardware/hardware_manager.md")
        
        print("\n⚠️  IMPORTANT SECURITY REMINDERS:")
        print("   - Only use on authorized networks/devices")
        print("   - Obtain written permission before testing")
        print("   - Follow ethical hacking guidelines")
        print("   - Comply with local laws and regulations")
        print("   - Enable audit logging for accountability")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
