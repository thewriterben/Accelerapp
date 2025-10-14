"""
Digital Twin Platform Integration Demo

Demonstrates the digital twin capabilities of Accelerapp:
- Real-time state synchronization
- Visualization and monitoring
- Blockchain-verifiable logs
- AR/VR interface integration
- REST API for management
"""

from accelerapp.digital_twin import (
    DigitalTwinManager,
    TwinVisualizer,
    BlockchainLogger,
    DigitalTwinAPI,
    ARVRInterface,
)
import time
import json


def demo_basic_twin():
    """Demo basic digital twin functionality."""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Digital Twin Creation and State Management")
    print("=" * 60)
    
    # Create a digital twin manager
    manager = DigitalTwinManager()
    
    # Create a digital twin for an Arduino device
    print("\n1. Creating digital twin for 'arduino_device1'...")
    twin = manager.create_twin(
        "arduino_device1",
        {"type": "Arduino Uno", "version": "1.0", "pins": 14}
    )
    print(f"   ✓ Twin created: {twin.device_id}")
    
    # Update pin states
    print("\n2. Updating pin states...")
    twin.update_pin_state(13, True)  # LED on pin 13
    twin.update_pin_state(12, False)  # Another digital pin
    twin.update_analog_value(5, 512)  # Analog pin A5
    print("   ✓ Pin 13: HIGH")
    print("   ✓ Pin 12: LOW")
    print("   ✓ Analog Pin 5: 512")
    
    # Set connection status
    twin.set_connection_status(True)
    print("   ✓ Device connected")
    
    # Get current state
    print("\n3. Current state:")
    state = twin.get_current_state()
    print(f"   Connected: {state['connected']}")
    print(f"   Digital pins: {state['pin_states']}")
    print(f"   Analog pins: {state['analog_values']}")
    print(f"   Metadata: {state['metadata']}")


def demo_synchronization():
    """Demo hardware synchronization."""
    print("\n" + "=" * 60)
    print("Demo 2: Hardware State Synchronization")
    print("=" * 60)
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    # Simulate hardware state changes
    print("\n1. Simulating hardware state updates...")
    
    for i in range(3):
        hardware_state = {
            "pin_states": {13: i % 2 == 0, 12: i % 2 == 1},
            "analog_values": {5: 256 * i},
            "connected": True,
            "metadata": {"temperature": 25 + i, "iteration": i},
        }
        
        manager.sync_from_hardware("device1", hardware_state)
        print(f"   ✓ Sync iteration {i+1}: Pin 13={'HIGH' if i%2==0 else 'LOW'}, "
              f"Analog=5:{256*i}, Temp={25+i}°C")
        time.sleep(0.1)
    
    # Get synchronized state
    twin = manager.get_twin("device1")
    print("\n2. Final synchronized state:")
    print(f"   {json.dumps(twin.get_current_state(), indent=2)}")


def demo_visualization():
    """Demo visualization and monitoring."""
    print("\n" + "=" * 60)
    print("Demo 3: Visualization and Monitoring")
    print("=" * 60)
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    
    # Create multiple devices
    print("\n1. Setting up multiple devices...")
    for i in range(3):
        device_id = f"device{i+1}"
        twin = manager.create_twin(device_id, {"location": f"Lab {i+1}"})
        twin.update_pin_state(13, i % 2 == 0)
        twin.set_connection_status(i < 2)  # Only first two connected
        print(f"   ✓ Created {device_id} in Lab {i+1}")
    
    # Get overview dashboard
    print("\n2. Overview Dashboard:")
    overview = visualizer.get_overview_dashboard()
    print(f"   Total devices: {overview['total_devices']}")
    print(f"   Connected: {overview['connected_devices']}")
    print(f"   Devices:")
    for device in overview['devices']:
        status = "🟢" if device['connected'] else "🔴"
        print(f"     {status} {device['device_id']}: "
              f"{device['pin_count']} digital pins, "
              f"{device['analog_count']} analog pins")
    
    # Get device dashboard
    print("\n3. Device1 Dashboard:")
    dashboard = visualizer.get_device_dashboard("device1")
    if dashboard:
        print(f"   Device: {dashboard['device_id']}")
        print(f"   Status: {'🟢 Connected' if dashboard['connection_status'] else '🔴 Disconnected'}")
        print(f"   Pin States: {dashboard['pin_states']}")
    
    # Generate status report
    print("\n4. Device1 Status Report:")
    report = visualizer.generate_status_report("device1")
    if report:
        print("\n" + report)


def demo_blockchain():
    """Demo blockchain-verifiable logging."""
    print("\n" + "=" * 60)
    print("Demo 4: Blockchain-Verifiable Hardware Logs")
    print("=" * 60)
    
    logger = BlockchainLogger("secure_device1")
    
    print("\n1. Logging hardware events to blockchain...")
    
    # Log various events
    logger.log_connection_event(True)
    print("   ✓ Logged connection event")
    
    logger.log_state_change(13, True, "digital")
    print("   ✓ Logged digital pin 13 state change")
    
    logger.log_state_change(5, 512, "analog")
    print("   ✓ Logged analog pin 5 value")
    
    logger.log_event("sensor_reading", {
        "sensor": "temperature",
        "value": 25.5,
        "unit": "celsius"
    })
    print("   ✓ Logged sensor reading")
    
    # Verify blockchain integrity
    print("\n2. Verifying blockchain integrity...")
    is_valid = logger.verify_chain()
    print(f"   Blockchain valid: {'✓ YES' if is_valid else '✗ NO'}")
    
    # Get blockchain stats
    print("\n3. Blockchain Statistics:")
    stats = logger.get_chain_stats()
    print(f"   Total blocks: {stats['total_blocks']}")
    print(f"   Is valid: {stats['is_valid']}")
    print(f"   Event types: {stats['event_types']}")
    
    # Show recent events
    print("\n4. Recent Events:")
    recent = logger.get_recent_events(3)
    for block in recent:
        print(f"   Block {block['index']}: {block['data'].get('event_type', 'N/A')} "
              f"at {block['timestamp']}")


def demo_api():
    """Demo REST API."""
    print("\n" + "=" * 60)
    print("Demo 5: REST API for Digital Twin Management")
    print("=" * 60)
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    print("\n1. API Health Check:")
    response = api.handle_request("GET", "/health")
    print(f"   Status: {response['status']}")
    print(f"   Health: {response['health']}")
    
    print("\n2. Creating twin via API:")
    response = api.handle_request(
        "POST",
        "/twins",
        data={"device_id": "api_device1", "device_info": {"type": "ESP32"}}
    )
    print(f"   Status Code: {response['status_code']}")
    print(f"   Device ID: {response.get('device_id', 'N/A')}")
    
    print("\n3. Listing all twins:")
    response = api.handle_request("GET", "/twins")
    print(f"   Total twins: {response['count']}")
    print(f"   Twins: {response['twins']}")
    
    print("\n4. Getting twin state:")
    response = api.handle_request("GET", "/twins/api_device1/state")
    print(f"   State: {json.dumps(response.get('state', {}), indent=2)}")
    
    print("\n5. Getting dashboard:")
    response = api.handle_request("GET", "/twins/api_device1/dashboard")
    if "dashboard" in response:
        dashboard = response["dashboard"]
        print(f"   Device: {dashboard['device_id']}")
        print(f"   Connected: {dashboard['connection_status']}")


def demo_arvr():
    """Demo AR/VR interface."""
    print("\n" + "=" * 60)
    print("Demo 6: AR/VR Interface Integration")
    print("=" * 60)
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    # Create a device
    print("\n1. Setting up device for AR/VR...")
    twin = manager.create_twin("vr_device1", {"type": "Arduino Mega"})
    twin.update_pin_state(13, True)
    twin.update_analog_value(5, 512)
    twin.set_connection_status(True)
    print("   ✓ Device created and configured")
    
    # Create VR session
    print("\n2. Creating VR session...")
    session = arvr.create_session("vr_session_1", "vr_device1", "vr")
    print(f"   ✓ Session ID: {session['session_id']}")
    print(f"   ✓ Interface: {session['interface_type']}")
    
    # Get 3D model
    print("\n3. Loading 3D model for VR visualization...")
    model = arvr.get_3d_model("vr_device1")
    print(f"   Model type: {model['model_type']}")
    print(f"   Components: {len(model['components'])}")
    for comp in model['components'][:2]:  # Show first 2 components
        print(f"     - {comp['type']} at {comp['position']}, state: {comp.get('state', comp.get('value', 'N/A'))}")
    
    # Send control command
    print("\n4. Sending control command from VR interface...")
    result = arvr.send_control_command(
        "vr_session_1",
        {"type": "digital_write", "pin": 12, "value": True}
    )
    print(f"   ✓ Command: {result['command']}")
    print(f"   ✓ Success: {result['success']}")
    
    # Get haptic feedback
    print("\n5. Generating haptic feedback...")
    haptic = arvr.get_haptic_feedback("vr_device1")
    print(f"   Intensity: {haptic['intensity']:.2f}")
    print(f"   Pattern: {haptic['pattern']}")
    
    # Session stats
    print("\n6. Session Statistics:")
    stats = arvr.get_session_stats()
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Active sessions: {stats['active_sessions']}")


def demo_integration():
    """Demo full integration workflow."""
    print("\n" + "=" * 60)
    print("Demo 7: Full Integration Workflow")
    print("=" * 60)
    
    # Setup all components
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    blockchain_loggers = {"production_device": BlockchainLogger("production_device")}
    api = DigitalTwinAPI(manager, visualizer, blockchain_loggers)
    arvr = ARVRInterface(manager, visualizer)
    
    print("\n1. Complete setup initialized")
    print("   ✓ Twin Manager")
    print("   ✓ Visualizer")
    print("   ✓ Blockchain Logger")
    print("   ✓ REST API")
    print("   ✓ AR/VR Interface")
    
    # Create device via API
    print("\n2. Creating production device via API...")
    api.handle_request(
        "POST",
        "/twins",
        data={
            "device_id": "production_device",
            "device_info": {"type": "Industrial Controller", "location": "Factory Floor"}
        }
    )
    print("   ✓ Device created")
    
    # Simulate operation cycle
    print("\n3. Simulating operation cycle...")
    twin = manager.get_twin("production_device")
    
    for i in range(3):
        # Update state
        twin.update_pin_state(13, i % 2 == 0)
        twin.update_analog_value(5, 256 + i * 100)
        
        # Log to blockchain
        blockchain_loggers["production_device"].log_state_change(
            13, i % 2 == 0, "digital"
        )
        
        print(f"   Cycle {i+1}: Pin 13={'HIGH' if i%2==0 else 'LOW'}, "
              f"Analog={256+i*100}, Logged to blockchain")
        time.sleep(0.1)
    
    # Create AR session for monitoring
    print("\n4. Creating AR monitoring session...")
    arvr.create_session("monitor_session", "production_device", "ar")
    print("   ✓ AR session active")
    
    # Get overview
    print("\n5. System Overview:")
    health = manager.get_health_status()
    print(f"   Total twins: {health['total_twins']}")
    print(f"   Connected: {health['connected_twins']}")
    
    overview = visualizer.get_overview_dashboard()
    print(f"   Monitoring: {overview['total_devices']} devices")
    
    blockchain_stats = blockchain_loggers["production_device"].get_chain_stats()
    print(f"   Blockchain: {blockchain_stats['total_blocks']} blocks, "
          f"Valid: {blockchain_stats['is_valid']}")
    
    arvr_stats = arvr.get_session_stats()
    print(f"   AR/VR: {arvr_stats['active_sessions']} active sessions")
    
    print("\n✓ Integration workflow complete!")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("ACCELERAPP DIGITAL TWIN PLATFORM DEMO")
    print("=" * 60)
    print("\nThis demo showcases the comprehensive digital twin capabilities")
    print("for hardware projects, including:")
    print("  • Real-time state synchronization")
    print("  • Visualization and monitoring")
    print("  • Blockchain-verifiable logs")
    print("  • REST API management")
    print("  • AR/VR interface integration")
    
    try:
        demo_basic_twin()
        demo_synchronization()
        demo_visualization()
        demo_blockchain()
        demo_api()
        demo_arvr()
        demo_integration()
        
        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
