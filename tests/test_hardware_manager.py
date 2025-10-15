"""
Tests for Unified Hardware Manager.
"""

import pytest
from accelerapp.managers import HardwareManager, DeviceCapability, DeviceStatus
from accelerapp.managers.hardware_manager import (
    DeviceType,
    ManagedDevice,
    ScanResults,
)


def test_device_type_enum():
    """Test DeviceType enum values."""
    assert DeviceType.ESP32_MARAUDER.value == "esp32_marauder"
    assert DeviceType.FLIPPER_ZERO.value == "flipper_zero"
    assert DeviceType.MESHTASTIC.value == "meshtastic"


def test_device_capability_enum():
    """Test DeviceCapability enum values."""
    assert DeviceCapability.WIFI_SCAN.value == "wifi_scan"
    assert DeviceCapability.BLUETOOTH_SCAN.value == "bluetooth_scan"
    assert DeviceCapability.RFID_125KHZ.value == "rfid_125khz"
    assert DeviceCapability.NFC.value == "nfc"
    assert DeviceCapability.SUBGHZ.value == "subghz"
    assert DeviceCapability.INFRARED.value == "infrared"
    assert DeviceCapability.GPIO.value == "gpio"


def test_device_status_enum():
    """Test DeviceStatus enum values."""
    assert DeviceStatus.DISCONNECTED.value == "disconnected"
    assert DeviceStatus.CONNECTED.value == "connected"
    assert DeviceStatus.BUSY.value == "busy"
    assert DeviceStatus.ERROR.value == "error"


def test_managed_device_creation():
    """Test ManagedDevice dataclass."""
    device = ManagedDevice(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN, DeviceCapability.BLUETOOTH_SCAN},
        port="/dev/ttyUSB0",
    )
    
    assert device.device_id == "test_device"
    assert device.device_type == DeviceType.ESP32_MARAUDER
    assert device.status == DeviceStatus.DISCONNECTED
    assert DeviceCapability.WIFI_SCAN in device.capabilities
    assert DeviceCapability.BLUETOOTH_SCAN in device.capabilities


def test_managed_device_to_dict():
    """Test ManagedDevice to_dict conversion."""
    device = ManagedDevice(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
        port="/dev/ttyUSB0",
        metadata={"test": "data"},
    )
    
    data = device.to_dict()
    
    assert data["device_id"] == "test_device"
    assert data["device_type"] == "esp32_marauder"
    assert "wifi_scan" in data["capabilities"]
    assert data["status"] == "disconnected"
    assert data["port"] == "/dev/ttyUSB0"
    assert "last_seen" in data
    assert data["metadata"]["test"] == "data"


def test_scan_results_creation():
    """Test ScanResults dataclass."""
    results = ScanResults()
    
    assert len(results.wifi_networks) == 0
    assert len(results.bluetooth_devices) == 0
    assert len(results.rfid_tags) == 0
    assert len(results.nfc_tags) == 0
    assert len(results.devices_used) == 0


def test_scan_results_to_dict():
    """Test ScanResults to_dict conversion."""
    results = ScanResults(devices_used=["device1", "device2"])
    
    data = results.to_dict()
    
    assert isinstance(data["wifi_networks"], list)
    assert isinstance(data["bluetooth_devices"], list)
    assert "scan_time" in data
    assert "device1" in data["devices_used"]
    assert "device2" in data["devices_used"]


def test_hardware_manager_initialization():
    """Test HardwareManager initialization."""
    manager = HardwareManager()
    
    assert len(manager.devices) == 0
    assert manager._auto_discovery_enabled is True


@pytest.mark.asyncio
async def test_hardware_manager_discover_devices():
    """Test device discovery."""
    manager = HardwareManager()
    
    devices = await manager.discover_devices()
    
    # Should return list (may be empty in test environment)
    assert isinstance(devices, list)


def test_hardware_manager_register_device():
    """Test device registration."""
    manager = HardwareManager()
    
    result = manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
        port="/dev/ttyUSB0",
        metadata={"test": "data"},
    )
    
    assert result is True
    assert "test_device" in manager.devices
    assert manager.devices["test_device"].device_type == DeviceType.ESP32_MARAUDER


def test_hardware_manager_register_device_duplicate():
    """Test duplicate device registration."""
    manager = HardwareManager()
    
    # Register first time
    manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    # Try to register again
    result = manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    assert result is False


def test_hardware_manager_get_device():
    """Test get_device method."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    device = manager.get_device("test_device")
    
    assert device is not None
    assert device.device_id == "test_device"


def test_hardware_manager_get_device_not_found():
    """Test get_device with non-existent device."""
    manager = HardwareManager()
    
    device = manager.get_device("nonexistent")
    
    assert device is None


def test_hardware_manager_list_devices():
    """Test list_devices method."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="device1",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    manager.register_device(
        device_id="device2",
        device_type=DeviceType.FLIPPER_ZERO,
        device=None,
        capabilities={DeviceCapability.NFC},
    )
    
    all_devices = manager.list_devices()
    assert len(all_devices) == 2
    
    # Filter by device type
    marauder_devices = manager.list_devices(device_type=DeviceType.ESP32_MARAUDER)
    assert len(marauder_devices) == 1
    assert marauder_devices[0].device_id == "device1"
    
    # Filter by capability
    wifi_devices = manager.list_devices(capability=DeviceCapability.WIFI_SCAN)
    assert len(wifi_devices) == 1
    assert wifi_devices[0].device_id == "device1"


def test_hardware_manager_get_capabilities():
    """Test get_capabilities method."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="device1",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN, DeviceCapability.BLUETOOTH_SCAN},
    )
    
    manager.register_device(
        device_id="device2",
        device_type=DeviceType.FLIPPER_ZERO,
        device=None,
        capabilities={DeviceCapability.NFC, DeviceCapability.RFID_125KHZ},
    )
    
    capabilities = manager.get_capabilities()
    
    assert DeviceCapability.WIFI_SCAN in capabilities
    assert DeviceCapability.BLUETOOTH_SCAN in capabilities
    assert DeviceCapability.NFC in capabilities
    assert DeviceCapability.RFID_125KHZ in capabilities


def test_hardware_manager_unregister_device():
    """Test unregister_device method."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    result = manager.unregister_device("test_device")
    
    assert result is True
    assert "test_device" not in manager.devices


def test_hardware_manager_unregister_device_not_found():
    """Test unregister non-existent device."""
    manager = HardwareManager()
    
    result = manager.unregister_device("nonexistent")
    
    assert result is False


def test_hardware_manager_add_callback():
    """Test callback registration."""
    manager = HardwareManager()
    
    callback_called = []
    
    def test_callback(data):
        callback_called.append(data)
    
    manager.add_callback("device_connected", test_callback)
    
    # Trigger callback
    manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    assert len(callback_called) == 1


def test_hardware_manager_remove_callback():
    """Test callback removal."""
    manager = HardwareManager()
    
    callback_called = []
    
    def test_callback(data):
        callback_called.append(data)
    
    manager.add_callback("device_connected", test_callback)
    manager.remove_callback("device_connected", test_callback)
    
    # Trigger callback
    manager.register_device(
        device_id="test_device",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    # Callback should not be called
    assert len(callback_called) == 0


def test_hardware_manager_get_status():
    """Test get_status method."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="device1",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    status = manager.get_status()
    
    assert status["total_devices"] == 1
    assert status["connected_devices"] == 0  # Not connected
    assert "wifi_scan" in status["capabilities"]
    assert "device1" in status["devices"]


@pytest.mark.asyncio
async def test_hardware_manager_connect_device_not_registered():
    """Test connecting non-existent device."""
    manager = HardwareManager()
    
    result = await manager.connect_device("nonexistent")
    
    assert result is False


def test_hardware_manager_disconnect_device_not_registered():
    """Test disconnecting non-existent device."""
    manager = HardwareManager()
    
    result = manager.disconnect_device("nonexistent")
    
    assert result is False


@pytest.mark.asyncio
async def test_hardware_manager_unified_scan():
    """Test unified scan across devices."""
    manager = HardwareManager()
    
    # Register devices but don't connect
    manager.register_device(
        device_id="device1",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    # Perform unified scan
    results = await manager.unified_scan(duration=1.0)
    
    assert isinstance(results, ScanResults)
    # No devices connected, so results should be empty
    assert len(results.devices_used) == 0


@pytest.mark.asyncio
async def test_hardware_manager_shutdown():
    """Test manager shutdown."""
    manager = HardwareManager()
    
    manager.register_device(
        device_id="device1",
        device_type=DeviceType.ESP32_MARAUDER,
        device=None,
        capabilities={DeviceCapability.WIFI_SCAN},
    )
    
    await manager.shutdown()
    
    # All devices should be removed
    assert len(manager.devices) == 0
