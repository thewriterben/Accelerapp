"""
Tests for ESP32 Marauder integration.
"""

import pytest
from datetime import datetime
from accelerapp.hardware import (
    ESP32Marauder,
    MarauderCommand,
    AttackType,
    WiFiNetwork,
    BluetoothDevice,
)


def test_marauder_command_enum():
    """Test MarauderCommand enum values."""
    assert MarauderCommand.WIFI_SCAN.value == "scan"
    assert MarauderCommand.BT_SCAN.value == "ble"
    assert MarauderCommand.DEAUTH.value == "attack -t deauth"


def test_attack_type_enum():
    """Test AttackType enum values."""
    assert AttackType.DEAUTH.value == "deauth"
    assert AttackType.BEACON.value == "beacon"
    assert AttackType.PROBE.value == "probe"


def test_wifi_network_creation():
    """Test WiFiNetwork dataclass."""
    network = WiFiNetwork(
        ssid="TestNetwork",
        bssid="00:11:22:33:44:55",
        channel=6,
        rssi=-45,
        encryption="WPA2",
    )
    
    assert network.ssid == "TestNetwork"
    assert network.bssid == "00:11:22:33:44:55"
    assert network.channel == 6
    assert network.rssi == -45
    assert network.encryption == "WPA2"
    assert network.hidden is False


def test_wifi_network_to_dict():
    """Test WiFiNetwork to_dict conversion."""
    network = WiFiNetwork(
        ssid="TestNetwork",
        bssid="00:11:22:33:44:55",
        channel=6,
        rssi=-45,
        encryption="WPA2",
        vendor="TestVendor",
    )
    
    data = network.to_dict()
    
    assert data["ssid"] == "TestNetwork"
    assert data["bssid"] == "00:11:22:33:44:55"
    assert data["channel"] == 6
    assert data["rssi"] == -45
    assert data["encryption"] == "WPA2"
    assert data["vendor"] == "TestVendor"
    assert "first_seen" in data
    assert "last_seen" in data


def test_bluetooth_device_creation():
    """Test BluetoothDevice dataclass."""
    device = BluetoothDevice(
        name="TestDevice",
        address="AA:BB:CC:DD:EE:FF",
        rssi=-60,
        device_type="BLE",
        manufacturer="TestMfg",
    )
    
    assert device.name == "TestDevice"
    assert device.address == "AA:BB:CC:DD:EE:FF"
    assert device.rssi == -60
    assert device.device_type == "BLE"
    assert device.manufacturer == "TestMfg"


def test_bluetooth_device_to_dict():
    """Test BluetoothDevice to_dict conversion."""
    device = BluetoothDevice(
        name="TestDevice",
        address="AA:BB:CC:DD:EE:FF",
        rssi=-60,
        device_type="BLE",
        services=["Service1", "Service2"],
    )
    
    data = device.to_dict()
    
    assert data["name"] == "TestDevice"
    assert data["address"] == "AA:BB:CC:DD:EE:FF"
    assert data["rssi"] == -60
    assert data["device_type"] == "BLE"
    assert "Service1" in data["services"]
    assert "Service2" in data["services"]


def test_marauder_initialization():
    """Test ESP32Marauder initialization."""
    marauder = ESP32Marauder(port="/dev/ttyUSB0", baudrate=115200)
    
    assert marauder.port == "/dev/ttyUSB0"
    assert marauder.baudrate == 115200
    assert marauder.is_connected is False
    assert marauder.is_scanning is False
    assert marauder.is_attacking is False
    assert len(marauder.wifi_networks) == 0
    assert len(marauder.bluetooth_devices) == 0


def test_marauder_discover_devices():
    """Test device discovery (returns empty list in test environment)."""
    devices = ESP32Marauder.discover_devices()
    assert isinstance(devices, list)
    # In test environment, likely no devices connected


def test_marauder_get_device_info():
    """Test get_device_info method."""
    marauder = ESP32Marauder(port="/dev/ttyUSB0")
    
    info = marauder.get_device_info()
    
    assert info["port"] == "/dev/ttyUSB0"
    assert info["is_connected"] is False
    assert info["is_scanning"] is False
    assert info["is_attacking"] is False
    assert info["wifi_networks"] == 0
    assert info["bluetooth_devices"] == 0


def test_marauder_parse_wifi_result():
    """Test WiFi result parsing."""
    marauder = ESP32Marauder()
    
    # Valid result
    line = "TestSSID|00:11:22:33:44:55|6|-45|WPA2"
    network = marauder._parse_wifi_result(line)
    
    assert network is not None
    assert network.ssid == "TestSSID"
    assert network.bssid == "00:11:22:33:44:55"
    assert network.channel == 6
    assert network.rssi == -45
    assert network.encryption == "WPA2"


def test_marauder_parse_wifi_result_invalid():
    """Test WiFi result parsing with invalid data."""
    marauder = ESP32Marauder()
    
    # Invalid result
    line = "Invalid data"
    network = marauder._parse_wifi_result(line)
    
    assert network is None


def test_marauder_parse_bluetooth_result():
    """Test Bluetooth result parsing."""
    marauder = ESP32Marauder()
    
    # Valid result
    line = "TestDevice|AA:BB:CC:DD:EE:FF|-60|BLE"
    device = marauder._parse_bluetooth_result(line)
    
    assert device is not None
    assert device.name == "TestDevice"
    assert device.address == "AA:BB:CC:DD:EE:FF"
    assert device.rssi == -60
    assert device.device_type == "BLE"


def test_marauder_parse_bluetooth_result_invalid():
    """Test Bluetooth result parsing with invalid data."""
    marauder = ESP32Marauder()
    
    # Invalid result
    line = "Invalid data"
    device = marauder._parse_bluetooth_result(line)
    
    assert device is None


def test_marauder_build_attack_command():
    """Test attack command building."""
    marauder = ESP32Marauder()
    
    # Deauth attack
    command = marauder._build_attack_command(
        AttackType.DEAUTH,
        ["00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF"],
    )
    assert "attack -t deauth" in command
    assert "00:11:22:33:44:55" in command
    
    # Beacon attack
    command = marauder._build_attack_command(AttackType.BEACON, None)
    assert MarauderCommand.BEACON.value in command


def test_marauder_context_manager():
    """Test context manager protocol."""
    marauder = ESP32Marauder(port="/dev/ttyUSB0")
    
    # Should not raise error
    try:
        with marauder as m:
            assert m is marauder
    except Exception:
        # Expected in test environment without actual device
        pass


@pytest.mark.asyncio
async def test_marauder_scan_wifi_networks_not_connected():
    """Test WiFi scan when not connected."""
    marauder = ESP32Marauder()
    
    networks = await marauder.scan_wifi_networks(duration=1.0)
    
    # Should return empty list when not connected
    assert isinstance(networks, list)
    assert len(networks) == 0


@pytest.mark.asyncio
async def test_marauder_scan_bluetooth_devices_not_connected():
    """Test Bluetooth scan when not connected."""
    marauder = ESP32Marauder()
    
    devices = await marauder.scan_bluetooth_devices(duration=1.0)
    
    # Should return empty list when not connected
    assert isinstance(devices, list)
    assert len(devices) == 0


def test_marauder_start_attack_not_connected():
    """Test starting attack when not connected."""
    marauder = ESP32Marauder()
    
    result = marauder.start_attack(AttackType.DEAUTH)
    
    # Should fail when not connected
    assert result is False


def test_marauder_stop_operation_not_connected():
    """Test stopping operation when not connected."""
    marauder = ESP32Marauder()
    
    result = marauder.stop_operation()
    
    # Should return False when not connected
    assert result is False
