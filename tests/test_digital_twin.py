"""
Tests for digital twin platform integration.
"""

import pytest
from datetime import datetime, timedelta


def test_digital_twin_imports():
    """Test that digital twin modules can be imported."""
    from accelerapp.digital_twin import (
        TwinState,
        StateSnapshot,
        DigitalTwinManager,
        TwinVisualizer,
        BlockchainLogger,
        DigitalTwinAPI,
        ARVRInterface,
    )
    
    assert TwinState is not None
    assert StateSnapshot is not None
    assert DigitalTwinManager is not None
    assert TwinVisualizer is not None
    assert BlockchainLogger is not None
    assert DigitalTwinAPI is not None
    assert ARVRInterface is not None


def test_twin_state_creation():
    """Test creating a twin state."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    
    assert twin.device_id == "device1"
    assert twin.current_state["connected"] == False
    assert len(twin.state_history) == 0


def test_twin_state_pin_update():
    """Test updating pin state."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    twin.update_pin_state(13, True)
    
    state = twin.get_current_state()
    assert state["pin_states"][13] == True
    assert len(twin.state_history) == 1


def test_twin_state_analog_update():
    """Test updating analog value."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    twin.update_analog_value(5, 512)
    
    state = twin.get_current_state()
    assert state["analog_values"][5] == 512


def test_twin_state_metadata():
    """Test updating metadata."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    twin.update_metadata("temperature", 25.5)
    
    state = twin.get_current_state()
    assert state["metadata"]["temperature"] == 25.5


def test_twin_state_subscription():
    """Test state update subscriptions."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    events = []
    
    def callback(event_type, data):
        events.append({"type": event_type, "data": data})
    
    twin.subscribe(callback)
    twin.update_pin_state(13, True)
    
    assert len(events) == 1
    assert events[0]["type"] == "pin_update"
    assert events[0]["data"]["pin"] == 13


def test_twin_state_export_import():
    """Test exporting and importing state."""
    from accelerapp.digital_twin import TwinState
    
    twin = TwinState("device1")
    twin.update_pin_state(13, True)
    twin.update_analog_value(5, 512)
    
    exported = twin.export_state()
    
    twin2 = TwinState("device2")
    twin2.import_state(exported)
    
    assert twin2.current_state["pin_states"][13] == True
    assert twin2.current_state["analog_values"][5] == 512


def test_digital_twin_manager_creation():
    """Test creating digital twin manager."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    
    assert len(manager.twins) == 0
    assert len(manager.physical_devices) == 0


def test_digital_twin_manager_create_twin():
    """Test creating twins through manager."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    twin = manager.create_twin("device1", {"type": "arduino"})
    
    assert twin.device_id == "device1"
    assert "device1" in manager.twins
    assert twin.current_state["metadata"]["type"] == "arduino"


def test_digital_twin_manager_get_twin():
    """Test retrieving twin from manager."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    twin = manager.get_twin("device1")
    assert twin is not None
    assert twin.device_id == "device1"
    
    twin2 = manager.get_twin("nonexistent")
    assert twin2 is None


def test_digital_twin_manager_delete_twin():
    """Test deleting twin."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    success = manager.delete_twin("device1")
    assert success == True
    assert manager.get_twin("device1") is None


def test_digital_twin_manager_sync_from_hardware():
    """Test syncing state from hardware."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    hardware_state = {
        "pin_states": {13: True, 12: False},
        "analog_values": {5: 512},
        "connected": True,
    }
    
    success = manager.sync_from_hardware("device1", hardware_state)
    assert success == True
    
    twin = manager.get_twin("device1")
    state = twin.get_current_state()
    assert state["pin_states"][13] == True
    assert state["analog_values"][5] == 512
    assert state["connected"] == True


def test_digital_twin_manager_health():
    """Test manager health status."""
    from accelerapp.digital_twin import DigitalTwinManager
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    manager.create_twin("device2")
    
    twin1 = manager.get_twin("device1")
    twin1.set_connection_status(True)
    
    health = manager.get_health_status()
    assert health["total_twins"] == 2
    assert health["connected_twins"] == 1


def test_blockchain_logger_creation():
    """Test creating blockchain logger."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    
    assert logger.device_id == "device1"
    assert len(logger.chain) == 1  # Genesis block


def test_blockchain_logger_log_event():
    """Test logging events to blockchain."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    block_hash = logger.log_event("test_event", {"data": "test"})
    
    assert block_hash is not None
    assert len(logger.chain) == 2


def test_blockchain_logger_state_change():
    """Test logging state changes."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    hash1 = logger.log_state_change(13, True, "digital")
    hash2 = logger.log_state_change(5, 512, "analog")
    
    assert hash1 != hash2
    assert len(logger.chain) == 3


def test_blockchain_logger_verify():
    """Test blockchain verification."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    logger.log_event("event1", {"data": "test1"})
    logger.log_event("event2", {"data": "test2"})
    
    assert logger.verify_chain() == True


def test_blockchain_logger_get_chain():
    """Test getting blockchain."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    logger.log_event("test_event", {"data": "test"})
    
    chain = logger.get_chain()
    assert len(chain) == 2
    assert chain[0]["index"] == 0
    assert chain[1]["index"] == 1


def test_blockchain_logger_stats():
    """Test blockchain statistics."""
    from accelerapp.digital_twin import BlockchainLogger
    
    logger = BlockchainLogger("device1")
    logger.log_event("event1", {"data": "test"})
    logger.log_state_change(13, True, "digital")
    
    stats = logger.get_chain_stats()
    assert stats["total_blocks"] == 3
    assert stats["is_valid"] == True
    assert "event1" in stats["event_types"]


def test_visualizer_creation():
    """Test creating visualizer."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    
    assert visualizer.twin_manager == manager


def test_visualizer_device_dashboard():
    """Test device dashboard generation."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    twin = manager.get_twin("device1")
    twin.update_pin_state(13, True)
    twin.set_connection_status(True)
    
    visualizer = TwinVisualizer(manager)
    dashboard = visualizer.get_device_dashboard("device1")
    
    assert dashboard is not None
    assert dashboard["device_id"] == "device1"
    assert dashboard["connection_status"] == True
    assert dashboard["pin_states"][13] == True


def test_visualizer_overview_dashboard():
    """Test overview dashboard."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    manager.create_twin("device2")
    
    manager.get_twin("device1").set_connection_status(True)
    
    visualizer = TwinVisualizer(manager)
    overview = visualizer.get_overview_dashboard()
    
    assert overview["total_devices"] == 2
    assert overview["connected_devices"] == 1


def test_visualizer_status_report():
    """Test status report generation."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    twin = manager.get_twin("device1")
    twin.update_pin_state(13, True)
    
    visualizer = TwinVisualizer(manager)
    report = visualizer.generate_status_report("device1")
    
    assert report is not None
    assert "device1" in report
    assert "Pin 13" in report


def test_api_creation():
    """Test creating API handler."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    assert api.twin_manager == manager
    assert api.visualizer == visualizer


def test_api_health_check():
    """Test API health check endpoint."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    response = api.handle_request("GET", "/health")
    
    assert response["status"] == "ok"
    assert response["status_code"] == 200


def test_api_list_twins():
    """Test listing twins via API."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    manager.create_twin("device2")
    
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    response = api.handle_request("GET", "/twins")
    
    assert response["status_code"] == 200
    assert response["count"] == 2
    assert "device1" in response["twins"]


def test_api_create_twin():
    """Test creating twin via API."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    response = api.handle_request(
        "POST",
        "/twins",
        data={"device_id": "device1", "device_info": {"type": "arduino"}},
    )
    
    assert response["status_code"] == 201
    assert response["device_id"] == "device1"
    assert manager.get_twin("device1") is not None


def test_api_get_twin():
    """Test getting twin via API."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    response = api.handle_request("GET", "/twins/device1")
    
    assert response["status_code"] == 200
    assert response["device_id"] == "device1"


def test_api_delete_twin():
    """Test deleting twin via API."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, DigitalTwinAPI
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    visualizer = TwinVisualizer(manager)
    api = DigitalTwinAPI(manager, visualizer)
    
    response = api.handle_request("DELETE", "/twins/device1")
    
    assert response["status_code"] == 200
    assert manager.get_twin("device1") is None


def test_arvr_interface_creation():
    """Test creating AR/VR interface."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, ARVRInterface
    
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    assert arvr.twin_manager == manager
    assert arvr.visualizer == visualizer


def test_arvr_create_session():
    """Test creating AR/VR session."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, ARVRInterface
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    session = arvr.create_session("session1", "device1", "vr")
    
    assert session["session_id"] == "session1"
    assert session["device_id"] == "device1"
    assert session["interface_type"] == "vr"


def test_arvr_get_3d_model():
    """Test getting 3D model."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, ARVRInterface
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    twin = manager.get_twin("device1")
    twin.update_pin_state(13, True)
    
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    model = arvr.get_3d_model("device1")
    
    assert model["device_id"] == "device1"
    assert len(model["components"]) > 0


def test_arvr_send_control_command():
    """Test sending control command via AR/VR."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, ARVRInterface
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    arvr.create_session("session1", "device1", "vr")
    
    result = arvr.send_control_command(
        "session1",
        {"type": "digital_write", "pin": 13, "value": True}
    )
    
    assert result["success"] == True
    assert result["command"] == "digital_write"
    
    twin = manager.get_twin("device1")
    assert twin.current_state["pin_states"][13] == True


def test_arvr_session_management():
    """Test AR/VR session management."""
    from accelerapp.digital_twin import DigitalTwinManager, TwinVisualizer, ARVRInterface
    
    manager = DigitalTwinManager()
    manager.create_twin("device1")
    manager.create_twin("device2")
    
    visualizer = TwinVisualizer(manager)
    arvr = ARVRInterface(manager, visualizer)
    
    arvr.create_session("session1", "device1", "vr")
    arvr.create_session("session2", "device2", "ar")
    
    sessions = arvr.list_active_sessions()
    assert len(sessions) == 2
    
    arvr.close_session("session1")
    sessions = arvr.list_active_sessions()
    assert len(sessions) == 1


def test_integration_full_workflow():
    """Test full digital twin workflow integration."""
    from accelerapp.digital_twin import (
        DigitalTwinManager,
        TwinVisualizer,
        BlockchainLogger,
        DigitalTwinAPI,
        ARVRInterface,
    )
    
    # Setup
    manager = DigitalTwinManager()
    visualizer = TwinVisualizer(manager)
    blockchain_loggers = {"device1": BlockchainLogger("device1")}
    api = DigitalTwinAPI(manager, visualizer, blockchain_loggers)
    arvr = ARVRInterface(manager, visualizer)
    
    # Create twin via API
    response = api.handle_request(
        "POST",
        "/twins",
        data={"device_id": "device1"}
    )
    assert response["status_code"] == 201
    
    # Update state
    twin = manager.get_twin("device1")
    twin.update_pin_state(13, True)
    twin.set_connection_status(True)
    
    # Log to blockchain
    blockchain_loggers["device1"].log_state_change(13, True, "digital")
    
    # Get dashboard
    dashboard = visualizer.get_device_dashboard("device1")
    assert dashboard["connection_status"] == True
    
    # Create AR/VR session
    session = arvr.create_session("session1", "device1", "vr")
    assert session["device_id"] == "device1"
    
    # Send command via AR/VR
    result = arvr.send_control_command(
        "session1",
        {"type": "analog_write", "pin": 5, "value": 512}
    )
    assert result["success"] == True
    
    # Verify blockchain
    assert blockchain_loggers["device1"].verify_chain() == True
    
    # Get overview
    overview = visualizer.get_overview_dashboard()
    assert overview["total_devices"] == 1
    assert overview["connected_devices"] == 1
