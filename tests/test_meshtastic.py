"""
Tests for Meshtastic platform integration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from accelerapp.platforms.meshtastic import (
    MeshtasticPlatform,
    MeshtasticDeviceInterface,
    DeviceDiscovery,
    ConnectionType,
    MeshtasticDevice,
    FirmwareManager,
    HardwareModel,
    OTAController,
    OTAMethod,
)
from accelerapp.agents.meshtastic_agent import MeshtasticAgent


class TestMeshtasticPlatform:
    """Test Meshtastic platform."""
    
    def test_platform_initialization(self):
        """Test platform initialization."""
        platform = MeshtasticPlatform()
        
        assert platform.name == "meshtastic"
        assert "mesh_networking" in platform.capabilities
        assert "lora" in platform.capabilities
        
    def test_platform_info(self):
        """Test getting platform information."""
        platform = MeshtasticPlatform()
        info = platform.get_platform_info()
        
        assert info["name"] == "meshtastic"
        assert info["display_name"] == "Meshtastic Mesh Network"
        assert "LoRa" in info["protocols"]["wireless"]
        assert info["features"]["mesh_routing"] is True
        
    def test_air_gapped_mode(self):
        """Test air-gapped mode initialization."""
        platform = MeshtasticPlatform(air_gapped=True)
        
        assert platform.air_gapped is True
        assert platform.firmware_manager.offline_mode is True
        
    def test_generate_device_config(self, tmp_path):
        """Test device configuration generation."""
        platform = MeshtasticPlatform()
        
        spec = {
            "task": "configure",
            "hardware_model": "esp32",
            "region": "US",
            "gps_enabled": True,
        }
        
        result = platform.generate_code(spec, tmp_path)
        
        assert result["status"] == "success"
        assert result["platform"] == "meshtastic"
        assert len(result["files_generated"]) > 0
        
        # Check that config file was created
        config_file = tmp_path / "meshtastic_config.yaml"
        assert config_file.exists()
        
    def test_generate_firmware_config(self, tmp_path):
        """Test firmware configuration generation."""
        platform = MeshtasticPlatform()
        
        spec = {
            "task": "firmware",
            "hardware_model": "esp32",
            "enable_gps": True,
            "enable_bluetooth": True,
        }
        
        result = platform.generate_code(spec, tmp_path)
        
        assert result["status"] == "success"
        
        # Check that firmware config was created
        config_file = tmp_path / "firmware_build_config.json"
        assert config_file.exists()
        
    def test_generate_integration_code(self, tmp_path):
        """Test integration code generation."""
        platform = MeshtasticPlatform()
        
        spec = {
            "task": "integration",
            "language": "python",
        }
        
        result = platform.generate_code(spec, tmp_path)
        
        assert result["status"] == "success"
        
        # Check that integration code was created
        python_file = tmp_path / "meshtastic_integration.py"
        assert python_file.exists()
        
    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        platform = MeshtasticPlatform()
        
        config = {
            "hardware_model": "esp32",
            "region": "US",
            "channels": [{"index": 0, "name": "Primary"}],
        }
        
        errors = platform.validate_config(config)
        assert len(errors) == 0
        
    def test_validate_config_invalid_region(self):
        """Test configuration validation with invalid region."""
        platform = MeshtasticPlatform()
        
        config = {
            "region": "INVALID_REGION",
        }
        
        errors = platform.validate_config(config)
        assert len(errors) > 0
        assert "Invalid region" in errors[0]
        
    def test_validate_config_too_many_channels(self):
        """Test configuration validation with too many channels."""
        platform = MeshtasticPlatform()
        
        config = {
            "channels": [{"index": i} for i in range(10)],
        }
        
        errors = platform.validate_config(config)
        assert len(errors) > 0
        assert "Maximum 8 channels" in errors[0]


class TestDeviceDiscovery:
    """Test device discovery."""
    
    def test_discovery_initialization(self):
        """Test device discovery initialization."""
        discovery = DeviceDiscovery()
        assert discovery._discovered_devices == {}
        
    @patch('serial.tools.list_ports.comports')
    def test_discover_serial_devices(self, mock_comports):
        """Test serial device discovery."""
        # Mock serial port
        mock_port = Mock()
        mock_port.device = "/dev/ttyUSB0"
        mock_port.description = "ESP32 Device"
        mock_port.hwid = "USB VID:PID=10C4:EA60"
        mock_comports.return_value = [mock_port]
        
        discovery = DeviceDiscovery()
        devices = discovery.discover_serial_devices()
        
        assert len(devices) > 0
        assert devices[0].device_id == "/dev/ttyUSB0"
        assert devices[0].connection_type == ConnectionType.SERIAL
        
    def test_discover_all(self):
        """Test discovering all devices."""
        discovery = DeviceDiscovery()
        devices = discovery.discover_all()
        
        # Should return a list (even if empty)
        assert isinstance(devices, list)


class TestMeshtasticDeviceInterface:
    """Test device interface."""
    
    def test_interface_initialization(self):
        """Test interface initialization."""
        device = MeshtasticDevice(
            device_id="/dev/ttyUSB0",
            connection_type=ConnectionType.SERIAL,
        )
        interface = MeshtasticDeviceInterface(device)
        
        assert interface.device == device
        assert interface.connected is False
        
    def test_connect_serial(self):
        """Test serial connection."""
        device = MeshtasticDevice(
            device_id="/dev/ttyUSB0",
            connection_type=ConnectionType.SERIAL,
            connection_info={"port": "/dev/ttyUSB0"},
        )
        interface = MeshtasticDeviceInterface(device)
        
        # Connection should succeed (placeholder implementation)
        result = interface.connect()
        assert result is True
        assert interface.is_connected() is True
        
    def test_disconnect(self):
        """Test disconnection."""
        device = MeshtasticDevice(
            device_id="/dev/ttyUSB0",
            connection_type=ConnectionType.SERIAL,
        )
        interface = MeshtasticDeviceInterface(device)
        interface.connect()
        
        interface.disconnect()
        assert interface.connected is False


class TestFirmwareManager:
    """Test firmware manager."""
    
    def test_firmware_manager_initialization(self, tmp_path):
        """Test firmware manager initialization."""
        manager = FirmwareManager(offline_mode=True, firmware_dir=tmp_path)
        
        assert manager.offline_mode is True
        assert manager.firmware_dir == tmp_path
        assert manager.firmware_dir.exists()
        
    def test_list_available_versions(self, tmp_path):
        """Test listing available firmware versions."""
        manager = FirmwareManager(offline_mode=True, firmware_dir=tmp_path)
        
        # Create a fake firmware file
        firmware_file = tmp_path / "firmware_tbeam_v2.3.0.bin"
        firmware_file.write_bytes(b"fake firmware")
        
        versions = manager.list_available_versions(HardwareModel.TBEAM)
        
        assert len(versions) > 0
        assert versions[0].hardware_model == HardwareModel.TBEAM
        
    def test_verify_firmware(self, tmp_path):
        """Test firmware verification."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        
        # Create a test firmware file
        firmware_file = tmp_path / "test_firmware.bin"
        firmware_file.write_bytes(b"test data")
        
        # Verify without checksum
        result = manager.verify_firmware(firmware_file)
        assert result is True
        
    def test_verify_firmware_not_found(self, tmp_path):
        """Test firmware verification with missing file."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        
        result = manager.verify_firmware(tmp_path / "nonexistent.bin")
        assert result is False


class TestOTAController:
    """Test OTA controller."""
    
    def test_ota_controller_initialization(self):
        """Test OTA controller initialization."""
        controller = OTAController(air_gapped=True)
        assert controller.air_gapped is True
        
    def test_check_update_available_air_gapped(self):
        """Test update check in air-gapped mode."""
        controller = OTAController(air_gapped=True)
        
        result = controller.check_update_available("2.0.0", "esp32")
        assert result is None
        
    def test_perform_ota_update(self, tmp_path):
        """Test OTA update."""
        controller = OTAController()
        
        # Create fake firmware
        firmware = tmp_path / "firmware.bin"
        firmware.write_bytes(b"fake firmware")
        
        result = controller.perform_ota_update(
            "192.168.1.100",
            firmware,
            OTAMethod.WIFI
        )
        
        # Should return True (placeholder implementation)
        assert result is True


class TestMeshtasticAgent:
    """Test Meshtastic agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MeshtasticAgent()
        
        assert agent.name == "MeshtasticAgent"
        assert "device_discovery" in agent.capabilities
        
    def test_can_handle_meshtastic_task(self):
        """Test task detection."""
        agent = MeshtasticAgent()
        
        assert agent.can_handle("configure meshtastic device") is True
        assert agent.can_handle("mesh network setup") is True
        assert agent.can_handle("lora communication") is True
        assert agent.can_handle("unrelated task") is False
        
    def test_discover_devices_operation(self):
        """Test device discovery operation."""
        agent = MeshtasticAgent()
        
        spec = {
            "operation": "discover",
            "air_gapped": False,
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert result["operation"] == "discover"
        assert "devices" in result
        
    def test_generate_configuration_operation(self, tmp_path):
        """Test configuration generation operation."""
        agent = MeshtasticAgent()
        
        spec = {
            "operation": "generate_config",
            "output_dir": str(tmp_path),
            "hardware_model": "esp32",
            "region": "US",
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "success"
        assert result["operation"] == "generate_config"
        
    def test_unknown_operation(self):
        """Test handling of unknown operation."""
        agent = MeshtasticAgent()
        
        spec = {
            "operation": "unknown_operation",
        }
        
        result = agent.generate(spec)
        
        assert result["status"] == "error"
        assert "Unknown operation" in result["message"]
        
    def test_get_info(self):
        """Test getting agent information."""
        agent = MeshtasticAgent()
        info = agent.get_info()
        
        assert info["name"] == "MeshtasticAgent"
        assert "discover" in info["supported_operations"]
        assert info["features"]["mesh_networking"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
