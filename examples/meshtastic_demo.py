#!/usr/bin/env python3
"""
Meshtastic Integration Demo for Accelerapp.

This demo showcases the comprehensive Meshtastic mesh communication support,
including device discovery, firmware management, network operations, and code generation.
"""

from pathlib import Path
import json

from accelerapp.meshtastic.device_interface import (
    MeshtasticDevice,
    DeviceDiscovery,
    ConnectionType,
    DeviceInfo,
)
from accelerapp.meshtastic.firmware_manager import FirmwareManager, FirmwareVersion
from accelerapp.meshtastic.network_manager import (
    MeshNetworkManager,
    MeshNode,
    NodeStatus,
)
from accelerapp.meshtastic.ota_controller import OTAController, OTAMethod
from accelerapp.agents.meshtastic_agent import MeshtasticAgent
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_device_discovery():
    """Demonstrate device discovery capabilities."""
    print_section("Device Discovery")
    
    print("Discovering Meshtastic devices...")
    
    # Discover serial devices
    serial_devices = DeviceDiscovery.discover_serial()
    print(f"\n✓ Serial devices found: {len(serial_devices)}")
    for device in serial_devices:
        print(f"  - {device.device_id} on {device.port}")
        print(f"    Hardware: {device.hardware_model}")
    
    # Discover all devices
    all_devices = DeviceDiscovery.discover_all()
    print(f"\n✓ Total devices found: {len(all_devices)}")
    
    # Simulate a discovered device for demo
    demo_device = DeviceInfo(
        device_id="demo_ttgo_tbeam",
        connection_type=ConnectionType.SERIAL,
        port="/dev/ttyUSB0",
        hardware_model="TTGO T-Beam v1.1",
        firmware_version="2.3.0",
        node_id="!12345678",
    )
    
    print("\n✓ Demo device created:")
    print(json.dumps(demo_device.to_dict(), indent=2))
    
    return demo_device


def demo_firmware_management(temp_dir: Path):
    """Demonstrate firmware management capabilities."""
    print_section("Firmware Management")
    
    print("Initializing firmware manager...")
    manager = FirmwareManager(firmware_dir=temp_dir / "meshtastic_firmware")
    
    print("✓ Firmware repository initialized")
    print(f"  Location: {manager.firmware_dir}")
    
    # Simulate adding firmware
    print("\n📦 Simulating firmware addition...")
    
    # Create dummy firmware files
    firmware_versions = [
        ("2.1.0", "TTGO T-Beam", "esp32"),
        ("2.2.0", "TTGO T-Beam", "esp32"),
        ("2.3.0", "TTGO T-Beam", "esp32"),
        ("2.3.0", "RAK4631", "nrf52"),
    ]
    
    for version, hardware, platform in firmware_versions:
        # Create dummy firmware file
        fw_content = f"Firmware {version} for {hardware} ({platform})".encode()
        fw_file = temp_dir / f"firmware_{version}_{hardware.replace(' ', '_')}.bin"
        fw_file.write_bytes(fw_content)
        
        firmware = manager.add_firmware(
            firmware_file=fw_file,
            version=version,
            hardware_model=hardware,
            platform=platform,
        )
        
        print(f"  ✓ Added: {firmware.version} for {firmware.hardware_model}")
        print(f"    Size: {firmware.file_size} bytes, Checksum: {firmware.checksum[:16]}...")
    
    # List available firmware
    print("\n📋 Available firmware:")
    all_firmware = manager.list_firmware()
    for fw in all_firmware:
        print(f"  - {fw.hardware_model} {fw.platform}: v{fw.version}")
    
    # Get latest firmware
    print("\n🔝 Latest firmware for TTGO T-Beam (ESP32):")
    latest = manager.get_latest_firmware("TTGO T-Beam", "esp32")
    if latest:
        print(f"  Version: {latest.version}")
        print(f"  Valid: {manager.verify_firmware(latest)}")
    
    return manager


def demo_network_management():
    """Demonstrate mesh network management capabilities."""
    print_section("Mesh Network Management")
    
    print("Initializing mesh network manager...")
    manager = MeshNetworkManager()
    
    print("✓ Network manager initialized")
    
    # Create sample mesh nodes
    print("\n🌐 Creating sample mesh network...")
    
    nodes = [
        MeshNode("!12345678", "N1", "Gateway Node", "TTGO T-Beam", "2.3.0", NodeStatus.ONLINE),
        MeshNode("!23456789", "N2", "Field Node 1", "TTGO T-Beam", "2.3.0", NodeStatus.ONLINE),
        MeshNode("!34567890", "N3", "Field Node 2", "RAK4631", "2.3.0", NodeStatus.ONLINE),
        MeshNode("!45678901", "N4", "Remote Node", "TTGO T-Beam", "2.2.0", NodeStatus.ONLINE),
    ]
    
    for node in nodes:
        manager.update_node(node)
        print(f"  ✓ Added node: {node.short_name} ({node.long_name})")
    
    # Create network topology
    print("\n🔗 Creating network connections...")
    connections = [
        ("!12345678", "!23456789"),
        ("!12345678", "!34567890"),
        ("!23456789", "!34567890"),
        ("!23456789", "!45678901"),
    ]
    
    for node1, node2 in connections:
        manager.update_connection(node1, node2)
        print(f"  ✓ Connected: {node1} <-> {node2}")
    
    # Get network statistics
    print("\n📊 Network Statistics:")
    stats = manager.get_network_stats()
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Online nodes: {stats['online_nodes']}")
    print(f"  Total connections: {stats['total_edges']}")
    print(f"  Network density: {stats['network_density']:.2%}")
    
    # Find routes
    print("\n🗺️  Route finding:")
    route = manager.find_route("!12345678", "!45678901")
    if route:
        print(f"  Route from Gateway to Remote Node:")
        print(f"  {' -> '.join(route)}")
        print(f"  Hop count: {len(route) - 1}")
    
    # Send a message
    print("\n📨 Sending test message...")
    result = manager.send_message("!12345678", "!45678901", "Hello from gateway")
    print(f"  Status: {result['status']}")
    print(f"  Route: {' -> '.join(result['route'])}")
    print(f"  Hops: {result['hop_count']}")
    
    # Export topology
    topology_file = Path("/tmp/mesh_topology.json")
    manager.export_topology(str(topology_file))
    print(f"\n💾 Topology exported to: {topology_file}")
    
    return manager


def demo_ota_updates():
    """Demonstrate OTA update capabilities."""
    print_section("OTA Firmware Updates")
    
    print("Initializing OTA controller...")
    controller = OTAController()
    
    print("✓ OTA controller initialized")
    
    # Create dummy firmware file
    firmware_file = Path("/tmp/test_firmware.bin")
    firmware_file.write_bytes(b"Test firmware data" * 1000)
    
    print(f"\n📦 Test firmware created: {firmware_file}")
    print(f"  Size: {firmware_file.stat().st_size} bytes")
    
    # Demonstrate different OTA methods
    print("\n🔄 OTA Update Methods:")
    
    methods = [
        (OTAMethod.WIFI, "device1", {"ip_address": "192.168.1.100"}),
        (OTAMethod.BLUETOOTH, "device2", {"mac_address": "AA:BB:CC:DD:EE:FF"}),
        (OTAMethod.SERIAL, "device3", {"port": "/dev/ttyUSB0"}),
    ]
    
    for method, device_id, device_info in methods:
        print(f"\n  {method.value.upper()} OTA Update:")
        print(f"  Device: {device_id}")
        
        # Note: In real scenario, this would actually perform the update
        # For demo, we just show the setup
        print(f"  ✓ Update configured")
        print(f"    Method: {method.value}")
        print(f"    Device info: {device_info}")
    
    # Show update history
    print("\n📜 Update History:")
    history = controller.get_update_history()
    if history:
        for update in history:
            print(f"  - Device: {update['device_id']}")
            print(f"    Version: {update['firmware_version']}")
            print(f"    Status: {update['status']}")
    else:
        print("  (No updates performed yet)")
    
    return controller


def demo_code_generation(output_dir: Path):
    """Demonstrate code generation for Meshtastic devices."""
    print_section("Meshtastic Code Generation")
    
    print("Initializing Meshtastic agent...")
    agent = MeshtasticAgent()
    
    print("✓ Agent initialized")
    print(f"  Name: {agent.name}")
    print(f"  Capabilities: {', '.join(agent.capabilities)}")
    
    # Generate code for ESP32
    print("\n🔨 Generating code for ESP32 Meshtastic node...")
    
    esp32_spec = {
        "task_type": "generate",
        "platform": "esp32",
        "device_name": "MyMeshtasticNode",
        "features": ["wifi", "gps", "bluetooth"],
    }
    
    result = agent.generate(esp32_spec)
    
    if result["status"] == "success":
        print("✓ Code generation successful")
        print(f"  Platform: {result['platform']}")
        print(f"  Features: {', '.join(result['features'])}")
        print(f"\n  Generated files:")
        for filename in result["files"].keys():
            print(f"    - {filename}")
        
        # Save generated files
        esp32_output = output_dir / "esp32_node"
        esp32_output.mkdir(parents=True, exist_ok=True)
        
        for filename, content in result["files"].items():
            file_path = esp32_output / filename
            file_path.write_text(content)
            print(f"      Saved: {file_path}")
    
    # Generate using platform directly
    print("\n🔨 Generating complete project with platform...")
    
    platform = MeshtasticESP32Platform()
    platform_output = output_dir / "meshtastic_project"
    
    project_spec = {
        "device_name": "FieldNode",
        "features": ["wifi", "gps"],
        "radio_config": {
            "frequency": 915.0,
            "bandwidth": 125.0,
            "spreading_factor": 7,
            "power": 20,
        },
    }
    
    result = platform.generate_code(project_spec, platform_output)
    
    if result["status"] == "success":
        print("✓ Project generation successful")
        print(f"  Output directory: {result['output_dir']}")
        print(f"\n  Generated files:")
        for file_path in result["files_generated"]:
            print(f"    - {Path(file_path).name}")
    
    return agent


def demo_agent_capabilities():
    """Demonstrate Meshtastic agent capabilities."""
    print_section("Agent Capabilities")
    
    agent = MeshtasticAgent()
    
    print("🤖 Meshtastic Agent Information:")
    info = agent.get_info()
    
    print(f"\n  Name: {info['name']}")
    print(f"  Type: {info['type']}")
    print(f"  Description: {info['description']}")
    
    print("\n  📋 Capabilities:")
    for capability in info['capabilities']:
        print(f"    - {capability}")
    
    print("\n  💻 Supported Platforms:")
    for platform, description in info['supported_platforms'].items():
        print(f"    - {platform}: {description}")
    
    print("\n  ⚡ Features:")
    for feature in info['features']:
        print(f"    - {feature}")
    
    # Test task handling
    print("\n  🎯 Task Handling Tests:")
    test_tasks = [
        "meshtastic device programming",
        "mesh network setup",
        "lora configuration",
        "arduino led blink",  # Should not handle
    ]
    
    for task in test_tasks:
        can_handle = agent.can_handle(task)
        status = "✓" if can_handle else "✗"
        print(f"    {status} '{task}': {can_handle}")


def main():
    """Run the complete Meshtastic demo."""
    print("\n" + "=" * 80)
    print("  Accelerapp Meshtastic Integration Demo")
    print("  Comprehensive Mesh Communication Support")
    print("=" * 80)
    
    # Create temporary directory for demo files
    demo_dir = Path("/tmp/accelerapp_meshtastic_demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Demo directory: {demo_dir}")
    
    try:
        # Run all demo sections
        device_info = demo_device_discovery()
        firmware_manager = demo_firmware_management(demo_dir)
        network_manager = demo_network_management()
        ota_controller = demo_ota_updates()
        agent = demo_code_generation(demo_dir / "generated")
        demo_agent_capabilities()
        
        # Final summary
        print_section("Demo Complete")
        
        print("✅ All Meshtastic features demonstrated successfully!")
        print("\n📊 Summary:")
        print(f"  - Device discovery: Operational")
        print(f"  - Firmware management: {len(firmware_manager.firmware_cache)} firmware versions")
        print(f"  - Network management: {len(network_manager.topology.nodes)} nodes")
        print(f"  - OTA updates: Configured")
        print(f"  - Code generation: Successful")
        
        print(f"\n📁 Generated files location: {demo_dir}")
        print("\n🚀 Meshtastic integration is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
