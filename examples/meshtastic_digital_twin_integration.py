"""
Meshtastic Digital Twin Integration Example
Demonstrates integration between Meshtastic devices and Accelerapp's Digital Twin platform.
"""

from pathlib import Path
from accelerapp.platforms.meshtastic import (
    MeshtasticPlatform,
    MeshtasticDevice,
    ConnectionType,
)
from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer


def create_meshtastic_digital_twins():
    """Create digital twins for Meshtastic mesh nodes."""
    print("=" * 60)
    print("Meshtastic Digital Twin Integration")
    print("=" * 60)
    print()
    
    # Initialize components
    platform = MeshtasticPlatform()
    twin_manager = DigitalTwinManager()
    visualizer = TwinVisualizer(twin_manager)
    
    # Simulate discovered Meshtastic devices
    # In production, these would come from actual device discovery
    simulated_devices = [
        MeshtasticDevice(
            device_id="mesh_node_001",
            connection_type=ConnectionType.SERIAL,
            device_name="Base Station",
            hardware_model="T-Beam",
            firmware_version="2.3.5",
            connection_info={"port": "/dev/ttyUSB0"}
        ),
        MeshtasticDevice(
            device_id="mesh_node_002",
            connection_type=ConnectionType.WIFI,
            device_name="Remote Node 1",
            hardware_model="TTGO LoRa",
            firmware_version="2.3.5",
            connection_info={"ip": "192.168.1.100"}
        ),
        MeshtasticDevice(
            device_id="mesh_node_003",
            connection_type=ConnectionType.BLUETOOTH,
            device_name="Mobile Node",
            hardware_model="RAK4631",
            firmware_version="2.3.4",
            connection_info={"ble_address": "AA:BB:CC:DD:EE:FF"}
        ),
    ]
    
    print("Creating digital twins for mesh nodes...")
    print()
    
    # Create digital twin for each Meshtastic device
    for device in simulated_devices:
        twin = twin_manager.create_twin(
            device.device_id,
            device_info={
                "type": "meshtastic",
                "device_name": device.device_name,
                "hardware_model": device.hardware_model,
                "firmware_version": device.firmware_version,
                "connection_type": device.connection_type.value,
                "role": "mesh_node",
            }
        )
        
        print(f"✓ Created twin for {device.device_name}")
        print(f"  - Device ID: {device.device_id}")
        print(f"  - Hardware: {device.hardware_model}")
        print(f"  - Connection: {device.connection_type.value}")
        print()
        
        # Simulate initial state using metadata
        twin.set_connection_status(True)
        twin.update_metadata("device_name", device.device_name)
        twin.update_metadata("hardware_model", device.hardware_model)
        twin.update_metadata("firmware_version", device.firmware_version)
        twin.update_metadata("connection_type", device.connection_type.value)
        twin.update_metadata("signal_strength", -75)  # dBm
        twin.update_metadata("battery_level", 85.0)  # percent
        twin.update_metadata("gps_latitude", 37.7749)
        twin.update_metadata("gps_longitude", -122.4194)
        twin.update_metadata("messages_sent", 0)
        twin.update_metadata("messages_received", 0)
    
    return twin_manager, visualizer, simulated_devices


def simulate_mesh_activity(twin_manager, devices):
    """Simulate mesh network activity."""
    print("=" * 60)
    print("Simulating Mesh Network Activity")
    print("=" * 60)
    print()
    
    import random
    
    # Simulate mesh node communication
    for i in range(5):
        print(f"Activity cycle {i+1}:")
        
        for device in devices:
            twin = twin_manager.get_twin(device.device_id)
            if twin:
                # Update mesh node state
                current_state = twin.get_current_state()
                metadata = current_state.get("metadata", {})
                
                # Simulate message activity
                messages_sent = metadata.get("messages_sent", 0) + random.randint(0, 3)
                messages_received = metadata.get("messages_received", 0) + random.randint(0, 5)
                
                # Simulate signal strength variation
                signal_strength = -75 + random.randint(-15, 10)
                
                # Simulate battery drain
                battery_level = max(0, metadata.get("battery_level", 100) - random.uniform(0.5, 2.0))
                
                # Update metadata
                twin.update_metadata("signal_strength", signal_strength)
                twin.update_metadata("battery_level", battery_level)
                twin.update_metadata("messages_sent", messages_sent)
                twin.update_metadata("messages_received", messages_received)
                twin.update_metadata("last_seen", "now")
                
                print(f"  {device.device_name}: "
                      f"Signal={signal_strength}dBm, "
                      f"Battery={battery_level:.1f}%, "
                      f"TX={messages_sent}, RX={messages_received}")
        
        print()


def visualize_mesh_network(twin_manager, visualizer):
    """Visualize mesh network status."""
    print("=" * 60)
    print("Mesh Network Overview")
    print("=" * 60)
    print()
    
    overview = visualizer.get_overview_dashboard()
    
    print(f"Total Mesh Nodes: {overview['total_devices']}")
    print(f"Connected Nodes: {overview['connected_devices']}")
    print(f"Update Frequency: {overview.get('update_frequency', 'N/A')} Hz")
    print()
    
    print("Node Details:")
    print("-" * 60)
    
    for twin_id in twin_manager.list_twins():
        twin = twin_manager.get_twin(twin_id)
        if twin:
            state = twin.get_current_state()
            metadata = state.get("metadata", {})
            
            print(f"\n{metadata.get('device_name', twin_id)}")
            print(f"  Hardware: {metadata.get('hardware_model', 'Unknown')}")
            print(f"  Firmware: {metadata.get('firmware_version', 'Unknown')}")
            print(f"  Connection: {metadata.get('connection_type', 'Unknown')}")
            print(f"  Signal: {metadata.get('signal_strength', 'N/A')} dBm")
            print(f"  Battery: {metadata.get('battery_level', 'N/A'):.1f}%")
            print(f"  Messages TX/RX: {metadata.get('messages_sent', 0)}/{metadata.get('messages_received', 0)}")
            
            # GPS position if available
            lat = metadata.get('gps_latitude')
            lon = metadata.get('gps_longitude')
            if lat and lon:
                print(f"  Position: {lat:.4f}, {lon:.4f}")


def demonstrate_state_history(twin_manager):
    """Demonstrate state history tracking."""
    print("\n" + "=" * 60)
    print("State History Tracking")
    print("=" * 60)
    print()
    
    # Get history from first twin
    twin_ids = twin_manager.list_twins()
    if twin_ids:
        twin = twin_manager.get_twin(twin_ids[0])
        history = twin.get_history()
        
        print(f"State History Statistics:")
        print(f"  Total Snapshots: {len(history)}")
        print(f"  Device ID: {twin.device_id}")
        
        # Show last few state changes
        if history:
            print(f"\nRecent State Changes (Last {min(3, len(history))} snapshots):")
            for snapshot in history[-3:]:
                print(f"\n  Snapshot at: {snapshot.timestamp}")
                print(f"  Pin States: {len(snapshot.pin_states)} pins")
                print(f"  Analog Values: {len(snapshot.analog_values)} values")
                if snapshot.metadata:
                    # Show some metadata
                    if 'signal_strength' in snapshot.metadata:
                        print(f"  Signal: {snapshot.metadata['signal_strength']} dBm")
                    if 'battery_level' in snapshot.metadata:
                        print(f"  Battery: {snapshot.metadata['battery_level']:.1f}%")


def demonstrate_predictive_analytics(twin_manager):
    """Demonstrate predictive analytics for mesh network."""
    print("\n" + "=" * 60)
    print("Predictive Analytics for Mesh Network")
    print("=" * 60)
    print()
    
    print("Analyzing mesh node health and predicting maintenance needs...")
    print()
    
    for twin_id in twin_manager.list_twins():
        twin = twin_manager.get_twin(twin_id)
        if twin:
            state = twin.get_current_state()
            metadata = state.get("metadata", {})
            
            device_name = metadata.get('device_name', twin_id)
            battery = metadata.get('battery_level', 100)
            signal = metadata.get('signal_strength', -75)
            
            # Simple predictive analytics
            print(f"{device_name}:")
            
            # Battery prediction
            if battery < 20:
                print(f"  ⚠️  LOW BATTERY: {battery:.1f}% - Immediate attention required")
            elif battery < 50:
                print(f"  ⚡ Battery: {battery:.1f}% - Consider charging soon")
            else:
                print(f"  ✓ Battery: {battery:.1f}% - Healthy")
            
            # Signal strength analysis
            if signal < -90:
                print(f"  ⚠️  WEAK SIGNAL: {signal} dBm - May lose connectivity")
            elif signal < -80:
                print(f"  ⚡ Signal: {signal} dBm - Acceptable but could improve")
            else:
                print(f"  ✓ Signal: {signal} dBm - Strong connection")
            
            print()


def demonstrate_remote_management():
    """Demonstrate remote mesh network management via REST API."""
    print("=" * 60)
    print("Remote Mesh Network Management")
    print("=" * 60)
    print()
    
    print("REST API endpoints available for remote management:")
    print()
    print("  GET  /api/mesh/nodes          - List all mesh nodes")
    print("  GET  /api/mesh/node/{id}      - Get node details")
    print("  POST /api/mesh/node/{id}/config - Update node configuration")
    print("  POST /api/mesh/node/{id}/ota  - Trigger OTA update")
    print("  GET  /api/mesh/topology       - Get mesh network topology")
    print("  GET  /api/mesh/metrics        - Get network performance metrics")
    print()
    
    print("Example API usage:")
    print("  curl http://localhost:8000/api/mesh/nodes")
    print("  curl http://localhost:8000/api/mesh/node/mesh_node_001")
    print()


def main():
    """Main demonstration."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 6 + "Meshtastic Digital Twin Integration" + " " * 17 + "║")
    print("║" + " " * 15 + "Advanced Features Demo" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Create digital twins for mesh nodes
    twin_manager, visualizer, devices = create_meshtastic_digital_twins()
    
    # Simulate mesh network activity
    simulate_mesh_activity(twin_manager, devices)
    
    # Visualize mesh network
    visualize_mesh_network(twin_manager, visualizer)
    
    # Demonstrate state history
    demonstrate_state_history(twin_manager)
    
    # Demonstrate predictive analytics
    demonstrate_predictive_analytics(twin_manager)
    
    # Demonstrate remote management capabilities
    demonstrate_remote_management()
    
    print("=" * 60)
    print("Integration Complete!")
    print("=" * 60)
    print()
    print("Key Integration Features:")
    print("  ✓ Digital twins for each mesh node")
    print("  ✓ Real-time state synchronization")
    print("  ✓ State history tracking")
    print("  ✓ Predictive analytics for maintenance")
    print("  ✓ Remote management via REST API")
    print("  ✓ Network topology visualization")
    print()


if __name__ == "__main__":
    main()
