"""
Meshtastic Integration Demo
Demonstrates Meshtastic mesh communication support in Accelerapp.
"""

from pathlib import Path
from accelerapp.platforms.meshtastic import (
    MeshtasticPlatform,
    DeviceDiscovery,
    FirmwareManager,
    HardwareModel,
    OTAController,
    OTAMethod,
)
from accelerapp.agents.meshtastic_agent import MeshtasticAgent


def demo_platform_info():
    """Demo 1: Get Meshtastic platform information."""
    print("=" * 60)
    print("Demo 1: Meshtastic Platform Information")
    print("=" * 60)
    
    platform = MeshtasticPlatform()
    info = platform.get_platform_info()
    
    print(f"Platform: {info['display_name']}")
    print(f"Description: {info['description']}")
    print(f"Capabilities: {', '.join(info['capabilities'][:5])}...")
    print(f"Supported Hardware: {', '.join(info['supported_hardware'])}")
    print(f"Wireless Protocols: {', '.join(info['protocols']['wireless'])}")
    print(f"Max Range: {info['max_range']}")
    print()


def demo_device_discovery():
    """Demo 2: Discover Meshtastic devices."""
    print("=" * 60)
    print("Demo 2: Device Discovery")
    print("=" * 60)
    
    discovery = DeviceDiscovery()
    
    print("Discovering serial devices...")
    serial_devices = discovery.discover_serial_devices()
    print(f"Found {len(serial_devices)} serial device(s)")
    
    for device in serial_devices:
        print(f"  - {device.device_id} ({device.connection_type.value})")
    
    print("\nDiscovering all devices...")
    all_devices = discovery.discover_all()
    print(f"Total devices found: {len(all_devices)}")
    print()


def demo_device_configuration():
    """Demo 3: Generate device configuration."""
    print("=" * 60)
    print("Demo 3: Device Configuration Generation")
    print("=" * 60)
    
    platform = MeshtasticPlatform()
    
    config_spec = {
        "task": "configure",
        "hardware_model": "esp32",
        "region": "US",
        "gps_enabled": True,
        "bluetooth_enabled": True,
        "role": "CLIENT",
        "modem_preset": "LONG_FAST",
        "hop_limit": 3,
    }
    
    output_dir = Path("/tmp/meshtastic_demo/config")
    result = platform.generate_code(config_spec, output_dir)
    
    print(f"Status: {result['status']}")
    print(f"Platform: {result['platform']}")
    print(f"Generated files:")
    for file_path in result['files_generated']:
        print(f"  - {file_path}")
    
    # Show generated config
    config_file = Path(result['files_generated'][0])
    if config_file.exists():
        print(f"\nGenerated configuration preview:")
        print("-" * 60)
        content = config_file.read_text()
        # Show first 20 lines
        lines = content.split('\n')[:20]
        print('\n'.join(lines))
        if len(content.split('\n')) > 20:
            print("...")
    print()


def demo_firmware_management():
    """Demo 4: Firmware management."""
    print("=" * 60)
    print("Demo 4: Firmware Management")
    print("=" * 60)
    
    firmware_dir = Path("/tmp/meshtastic_demo/firmware")
    firmware_dir.mkdir(parents=True, exist_ok=True)
    
    manager = FirmwareManager(offline_mode=True, firmware_dir=firmware_dir)
    
    # Create a fake firmware file for demo
    demo_firmware = firmware_dir / "firmware_tbeam_v2.3.5.bin"
    demo_firmware.write_bytes(b"fake firmware data for demo")
    
    print("Listing available firmware versions for T-Beam...")
    versions = manager.list_available_versions(HardwareModel.TBEAM)
    
    if versions:
        print(f"Found {len(versions)} version(s):")
        for version in versions:
            print(f"  - Version: {version.version}")
            print(f"    Hardware: {version.hardware_model.value}")
            print(f"    File: {version.file_path}")
    else:
        print("No firmware versions found in local repository")
    
    print("\nVerifying firmware integrity...")
    if demo_firmware.exists():
        is_valid = manager.verify_firmware(demo_firmware)
        print(f"Firmware valid: {is_valid}")
    print()


def demo_integration_code_generation():
    """Demo 5: Generate integration code."""
    print("=" * 60)
    print("Demo 5: Integration Code Generation")
    print("=" * 60)
    
    platform = MeshtasticPlatform()
    
    # Generate Python integration
    python_spec = {
        "task": "integration",
        "language": "python",
    }
    
    output_dir = Path("/tmp/meshtastic_demo/integration")
    result = platform.generate_code(python_spec, output_dir)
    
    print(f"Status: {result['status']}")
    print(f"Generated integration files:")
    for file_path in result['files_generated']:
        print(f"  - {file_path}")
    
    # Show generated integration code preview
    if result['files_generated']:
        integration_file = Path(result['files_generated'][0])
        if integration_file.exists():
            print(f"\nIntegration code preview:")
            print("-" * 60)
            content = integration_file.read_text()
            # Show first 30 lines
            lines = content.split('\n')[:30]
            print('\n'.join(lines))
            if len(content.split('\n')) > 30:
                print("...")
    print()


def demo_agent_operations():
    """Demo 6: Using Meshtastic Agent."""
    print("=" * 60)
    print("Demo 6: Meshtastic Agent Operations")
    print("=" * 60)
    
    agent = MeshtasticAgent()
    
    print(f"Agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Capabilities: {', '.join(agent.capabilities)}")
    
    print("\nTesting task detection...")
    test_tasks = [
        "Configure Meshtastic device",
        "Setup mesh network",
        "Perform OTA update",
        "Unrelated Arduino task",
    ]
    
    for task in test_tasks:
        can_handle = agent.can_handle(task)
        print(f"  '{task}': {'✓' if can_handle else '✗'}")
    
    print("\nExecuting device discovery...")
    result = agent.generate({"operation": "discover"})
    print(f"Status: {result['status']}")
    print(f"Devices found: {result['count']}")
    
    print("\nGenerating configuration...")
    config_result = agent.generate({
        "operation": "generate_config",
        "output_dir": "/tmp/meshtastic_demo/agent_config",
        "region": "US",
        "hardware_model": "esp32",
    })
    print(f"Status: {config_result['status']}")
    print()


def demo_air_gapped_mode():
    """Demo 7: Air-gapped deployment."""
    print("=" * 60)
    print("Demo 7: Air-Gapped Mode")
    print("=" * 60)
    
    # Create platform in air-gapped mode
    platform = MeshtasticPlatform(air_gapped=True)
    
    print("Air-gapped mode enabled")
    print(f"Offline mode: {platform.air_gapped}")
    print(f"Firmware manager offline: {platform.firmware_manager.offline_mode}")
    print(f"OTA controller air-gapped: {platform.ota_controller.air_gapped}")
    
    print("\nAir-gapped mode features:")
    print("  - Local firmware repository")
    print("  - Offline device configuration")
    print("  - No external network dependencies")
    print("  - Complete mesh network operation without internet")
    
    # Demo OTA package creation
    print("\nCreating OTA package for air-gapped deployment...")
    ota = OTAController(air_gapped=True)
    
    # Create fake firmware for demo
    firmware_path = Path("/tmp/meshtastic_demo/firmware/demo_firmware.bin")
    firmware_path.parent.mkdir(parents=True, exist_ok=True)
    firmware_path.write_bytes(b"demo firmware data")
    
    output_path = Path("/tmp/meshtastic_demo/ota_package.zip")
    result = ota.create_ota_package(
        firmware_path,
        output_path,
        metadata={"version": "2.3.5", "hardware": "esp32"}
    )
    
    print(f"OTA package creation: {'Success' if result else 'Failed'}")
    print()


def demo_config_validation():
    """Demo 8: Configuration validation."""
    print("=" * 60)
    print("Demo 8: Configuration Validation")
    print("=" * 60)
    
    platform = MeshtasticPlatform()
    
    print("Validating correct configuration...")
    good_config = {
        "hardware_model": "esp32",
        "region": "US",
        "channels": [
            {"index": 0, "name": "Primary"},
            {"index": 1, "name": "Secondary"},
        ]
    }
    errors = platform.validate_config(good_config)
    print(f"Errors: {errors if errors else 'None - Configuration valid ✓'}")
    
    print("\nValidating incorrect configuration...")
    bad_config = {
        "region": "INVALID_REGION",
        "channels": [{"index": i} for i in range(10)],  # Too many
    }
    errors = platform.validate_config(bad_config)
    print(f"Errors found:")
    for error in errors:
        print(f"  - {error}")
    print()


def main():
    """Run all Meshtastic demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Meshtastic Integration Demo" + " " * 21 + "║")
    print("║" + " " * 10 + "Accelerapp Platform" + " " * 27 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    demos = [
        demo_platform_info,
        demo_device_discovery,
        demo_device_configuration,
        demo_firmware_management,
        demo_integration_code_generation,
        demo_agent_operations,
        demo_air_gapped_mode,
        demo_config_validation,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Error in demo: {e}")
            print()
    
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✓ Platform information and capabilities")
    print("  ✓ Device discovery (Serial, WiFi, BLE)")
    print("  ✓ Device configuration generation")
    print("  ✓ Firmware management and flashing")
    print("  ✓ Integration code generation")
    print("  ✓ Agent-based operations")
    print("  ✓ Air-gapped deployment support")
    print("  ✓ Configuration validation")
    print("\nFor more information, visit:")
    print("  https://github.com/thewriterben/Accelerapp")
    print("  https://meshtastic.org/")
    print()


if __name__ == "__main__":
    main()
