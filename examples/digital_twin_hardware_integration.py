"""
Digital Twin Integration with Hardware Service

Demonstrates how to integrate digital twins with the existing hardware service
for comprehensive hardware monitoring and management.
"""

import asyncio
from accelerapp.services import HardwareService
from accelerapp.digital_twin import (
    DigitalTwinManager,
    TwinVisualizer,
    BlockchainLogger,
    DigitalTwinAPI,
)


async def demo_hardware_service_integration():
    """Demonstrate integration between hardware service and digital twins."""
    print("\n" + "=" * 60)
    print("Digital Twin + Hardware Service Integration")
    print("=" * 60)
    
    # Initialize services
    print("\n1. Initializing services...")
    hardware_service = HardwareService()
    await hardware_service.initialize()
    
    twin_manager = DigitalTwinManager()
    visualizer = TwinVisualizer(twin_manager)
    
    print("   ✓ Hardware Service initialized")
    print("   ✓ Digital Twin Manager initialized")
    
    # Register devices in hardware service
    print("\n2. Registering devices in Hardware Service...")
    hardware_service.register_device("arduino_uno", {
        "type": "Arduino Uno",
        "port": "/dev/ttyUSB0",
        "pins": 14,
    })
    
    hardware_service.register_device("esp32_dev", {
        "type": "ESP32 DevKit",
        "port": "/dev/ttyUSB1",
        "pins": 30,
    })
    
    print("   ✓ Registered arduino_uno")
    print("   ✓ Registered esp32_dev")
    
    # Create digital twins for each device
    print("\n3. Creating digital twins for registered devices...")
    devices = hardware_service.list_devices()
    
    for device_id in devices:
        device_info = hardware_service.get_device(device_id)
        twin = twin_manager.create_twin(device_id, device_info)
        twin.set_connection_status(True)
        print(f"   ✓ Created twin for {device_id}")
    
    # Simulate hardware operations and twin synchronization
    print("\n4. Simulating hardware operations...")
    
    # Arduino operation
    arduino_twin = twin_manager.get_twin("arduino_uno")
    arduino_twin.update_pin_state(13, True)  # LED on
    arduino_twin.update_metadata("temperature", 25.5)
    print("   ✓ Arduino: LED on, temp=25.5°C")
    
    # ESP32 operation
    esp32_twin = twin_manager.get_twin("esp32_dev")
    esp32_twin.update_pin_state(2, True)  # Built-in LED
    esp32_twin.update_analog_value(34, 2048)  # ADC reading
    esp32_twin.update_metadata("wifi_rssi", -45)
    print("   ✓ ESP32: LED on, ADC=2048, RSSI=-45dBm")
    
    # Get comprehensive system status
    print("\n5. System Status:")
    
    # Hardware service health
    hw_health = hardware_service.get_health()
    print(f"   Hardware Service: {hw_health['registered_devices']} devices")
    
    # Digital twin health
    dt_health = twin_manager.get_health_status()
    print(f"   Digital Twins: {dt_health['total_twins']} twins, "
          f"{dt_health['connected_twins']} connected")
    
    # Visualization overview
    overview = visualizer.get_overview_dashboard()
    print(f"   Dashboard: {overview['connected_devices']}/{overview['total_devices']} devices online")
    
    # Show device details
    print("\n6. Device Details:")
    for device_id in devices:
        dashboard = visualizer.get_device_dashboard(device_id)
        if dashboard:
            print(f"\n   {device_id}:")
            print(f"     Status: {'🟢 Connected' if dashboard['connection_status'] else '🔴 Disconnected'}")
            print(f"     Pins: {len(dashboard['pin_states'])} digital, "
                  f"{len(dashboard['analog_values'])} analog")
            if dashboard['metadata']:
                print(f"     Metadata: {dashboard['metadata']}")
    
    # Cleanup
    print("\n7. Shutting down services...")
    await hardware_service.shutdown()
    print("   ✓ Services shutdown complete")


async def demo_with_blockchain():
    """Demonstrate blockchain logging with hardware operations."""
    print("\n" + "=" * 60)
    print("Digital Twin + Blockchain Integration")
    print("=" * 60)
    
    # Setup
    hardware_service = HardwareService()
    await hardware_service.initialize()
    
    twin_manager = DigitalTwinManager()
    blockchain_loggers = {}
    
    # Register critical device
    device_id = "critical_controller"
    print(f"\n1. Registering critical device: {device_id}")
    
    hardware_service.register_device(device_id, {
        "type": "Industrial Controller",
        "criticality": "high",
    })
    
    # Create twin with blockchain logging
    twin = twin_manager.create_twin(device_id)
    logger = BlockchainLogger(device_id)
    blockchain_loggers[device_id] = logger
    
    print("   ✓ Device registered")
    print("   ✓ Digital twin created")
    print("   ✓ Blockchain logger initialized")
    
    # Simulate operations with logging
    print("\n2. Simulating operations with blockchain audit trail...")
    
    operations = [
        ("connect", lambda: twin.set_connection_status(True)),
        ("pin_13_high", lambda: twin.update_pin_state(13, True)),
        ("pin_13_low", lambda: twin.update_pin_state(13, False)),
        ("sensor_read", lambda: twin.update_analog_value(5, 768)),
    ]
    
    for op_name, op_func in operations:
        # Execute operation
        op_func()
        
        # Log to blockchain
        if op_name == "connect":
            logger.log_connection_event(True)
        elif "pin" in op_name:
            pin, value = 13, "high" in op_name
            logger.log_state_change(pin, value, "digital")
        elif "sensor" in op_name:
            logger.log_event("sensor_reading", {"pin": 5, "value": 768})
        
        print(f"   ✓ Operation: {op_name}")
    
    # Verify blockchain
    print("\n3. Verifying blockchain integrity...")
    is_valid = logger.verify_chain()
    stats = logger.get_chain_stats()
    
    print(f"   Blockchain valid: {'✓ YES' if is_valid else '✗ NO'}")
    print(f"   Total blocks: {stats['total_blocks']}")
    print(f"   Event types: {stats['event_types']}")
    
    # Export audit trail
    print("\n4. Audit trail available for compliance")
    print(f"   Can export to: JSON, regulatory formats")
    print(f"   Cryptographically verifiable")
    
    # Cleanup
    await hardware_service.shutdown()


async def demo_api_integration():
    """Demonstrate REST API with hardware service."""
    print("\n" + "=" * 60)
    print("Digital Twin API + Hardware Service Integration")
    print("=" * 60)
    
    # Setup
    hardware_service = HardwareService()
    await hardware_service.initialize()
    
    twin_manager = DigitalTwinManager()
    visualizer = TwinVisualizer(twin_manager)
    api = DigitalTwinAPI(twin_manager, visualizer)
    
    print("\n1. API and services initialized")
    
    # Register device through hardware service
    print("\n2. Registering device through hardware service...")
    hardware_service.register_device("api_device", {
        "type": "Test Device",
        "location": "Lab A",
    })
    print("   ✓ Device registered in hardware service")
    
    # Create twin through API
    print("\n3. Creating digital twin through API...")
    device_info = hardware_service.get_device("api_device")
    response = api.handle_request(
        "POST",
        "/twins",
        data={"device_id": "api_device", "device_info": device_info}
    )
    print(f"   ✓ API Response: Status {response['status_code']}")
    
    # Update state through twin
    print("\n4. Updating state...")
    twin = twin_manager.get_twin("api_device")
    twin.update_pin_state(13, True)
    twin.set_connection_status(True)
    print("   ✓ State updated")
    
    # Query through API
    print("\n5. Querying through API...")
    response = api.handle_request("GET", "/twins/api_device/dashboard")
    
    if "dashboard" in response:
        dashboard = response["dashboard"]
        print(f"   Device: {dashboard['device_id']}")
        print(f"   Connected: {dashboard['connection_status']}")
        print(f"   Pin states: {dashboard['pin_states']}")
    
    # Cleanup
    await hardware_service.shutdown()


async def main():
    """Run all integration demos."""
    print("\n" + "=" * 60)
    print("DIGITAL TWIN + HARDWARE SERVICE INTEGRATION DEMOS")
    print("=" * 60)
    
    try:
        await demo_hardware_service_integration()
        await demo_with_blockchain()
        await demo_api_integration()
        
        print("\n" + "=" * 60)
        print("ALL INTEGRATION DEMOS COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
