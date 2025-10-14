"""
Tests for Meshtastic integration module.
"""

import pytest
from pathlib import Path
from datetime import datetime

from accelerapp.meshtastic.device_interface import (
    MeshtasticDevice,
    DeviceDiscovery,
    ConnectionType,
    DeviceInfo,
)
from accelerapp.meshtastic.firmware_manager import (
    FirmwareManager,
    FirmwareVersion,
    FirmwareUpdateStatus,
)
from accelerapp.meshtastic.network_manager import (
    MeshNetworkManager,
    MeshNode,
    NodeStatus,
    NetworkTopology,
)
from accelerapp.meshtastic.ota_controller import (
    OTAController,
    OTAMethod,
    UpdateProgress,
)
from accelerapp.agents.meshtastic_agent import MeshtasticAgent
from accelerapp.platforms.meshtastic import MeshtasticESP32Platform, MeshtasticNRF52Platform


class TestDeviceInterface:
    """Test device interface functionality."""
    
    def test_device_info_creation(self):
        """Test DeviceInfo creation."""
        device_info = DeviceInfo(
            device_id="test_device",
            connection_type=ConnectionType.SERIAL,
            port="/dev/ttyUSB0",
            hardware_model="TTGO T-Beam",
        )
        
        assert device_info.device_id == "test_device"
        assert device_info.connection_type == ConnectionType.SERIAL
        assert device_info.port == "/dev/ttyUSB0"
    
    def test_device_info_to_dict(self):
        """Test DeviceInfo conversion to dictionary."""
        device_info = DeviceInfo(
            device_id="test_device",
            connection_type=ConnectionType.WIFI,
            ip_address="192.168.1.100",
        )
        
        result = device_info.to_dict()
        assert result["device_id"] == "test_device"
        assert result["connection_type"] == "wifi"
        assert result["ip_address"] == "192.168.1.100"
    
    def test_meshtastic_device_creation(self):
        """Test MeshtasticDevice creation."""
        device_info = DeviceInfo(
            device_id="test_device",
            connection_type=ConnectionType.SERIAL,
            port="/dev/ttyUSB0",
        )
        
        device = MeshtasticDevice(device_info)
        assert device.device_info == device_info
        assert not device.is_connected
    
    def test_device_discovery_serial(self):
        """Test serial device discovery."""
        devices = DeviceDiscovery.discover_serial()
        assert isinstance(devices, list)
    
    def test_device_discovery_all(self):
        """Test discovery of all device types."""
        devices = DeviceDiscovery.discover_all()
        assert isinstance(devices, list)


class TestFirmwareManager:
    """Test firmware management functionality."""
    
    def test_firmware_version_creation(self):
        """Test FirmwareVersion creation."""
        firmware = FirmwareVersion(
            version="2.3.0",
            hardware_model="TTGO T-Beam",
            platform="esp32",
            build_date=datetime.now(),
        )
        
        assert firmware.version == "2.3.0"
        assert firmware.hardware_model == "TTGO T-Beam"
        assert firmware.platform == "esp32"
    
    def test_firmware_version_to_dict(self):
        """Test FirmwareVersion conversion to dictionary."""
        firmware = FirmwareVersion(
            version="2.3.0",
            hardware_model="TTGO T-Beam",
            platform="esp32",
            build_date=datetime.now(),
            is_official=True,
        )
        
        result = firmware.to_dict()
        assert result["version"] == "2.3.0"
        assert result["hardware_model"] == "TTGO T-Beam"
        assert result["platform"] == "esp32"
        assert result["is_official"] is True
    
    def test_firmware_manager_initialization(self, tmp_path):
        """Test FirmwareManager initialization."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        assert manager.firmware_dir == tmp_path
        assert manager.firmware_dir.exists()
    
    def test_list_firmware_empty(self, tmp_path):
        """Test listing firmware when none available."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        firmware_list = manager.list_firmware()
        assert firmware_list == []
    
    def test_add_firmware(self, tmp_path):
        """Test adding firmware to repository."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        
        # Create a test firmware file
        test_firmware = tmp_path / "test_firmware.bin"
        test_firmware.write_bytes(b"test firmware data")
        
        firmware = manager.add_firmware(
            firmware_file=test_firmware,
            version="2.3.0",
            hardware_model="TTGO T-Beam",
            platform="esp32",
        )
        
        assert firmware.version == "2.3.0"
        assert firmware.hardware_model == "TTGO T-Beam"
        assert firmware.file_size > 0
    
    def test_get_latest_firmware(self, tmp_path):
        """Test getting latest firmware."""
        manager = FirmwareManager(firmware_dir=tmp_path)
        
        # Add multiple firmware versions
        for version in ["2.1.0", "2.2.0", "2.3.0"]:
            test_firmware = tmp_path / f"test_{version}.bin"
            test_firmware.write_bytes(b"test data")
            manager.add_firmware(
                firmware_file=test_firmware,
                version=version,
                hardware_model="TTGO T-Beam",
                platform="esp32",
            )
        
        latest = manager.get_latest_firmware("TTGO T-Beam", "esp32")
        assert latest is not None
        assert latest.version in ["2.1.0", "2.2.0", "2.3.0"]


class TestNetworkManager:
    """Test mesh network management functionality."""
    
    def test_mesh_node_creation(self):
        """Test MeshNode creation."""
        node = MeshNode(
            node_id="node1",
            short_name="N1",
            long_name="Node 1",
            hardware_model="TTGO T-Beam",
            firmware_version="2.3.0",
        )
        
        assert node.node_id == "node1"
        assert node.short_name == "N1"
        assert node.status == NodeStatus.UNKNOWN
    
    def test_mesh_node_to_dict(self):
        """Test MeshNode conversion to dictionary."""
        node = MeshNode(
            node_id="node1",
            short_name="N1",
            long_name="Node 1",
            hardware_model="TTGO T-Beam",
            firmware_version="2.3.0",
            status=NodeStatus.ONLINE,
        )
        
        result = node.to_dict()
        assert result["node_id"] == "node1"
        assert result["status"] == "online"
    
    def test_network_topology_creation(self):
        """Test NetworkTopology creation."""
        topology = NetworkTopology()
        assert len(topology.nodes) == 0
        assert len(topology.edges) == 0
    
    def test_topology_add_node(self):
        """Test adding node to topology."""
        topology = NetworkTopology()
        node = MeshNode(
            node_id="node1",
            short_name="N1",
            long_name="Node 1",
            hardware_model="TTGO T-Beam",
            firmware_version="2.3.0",
        )
        
        topology.add_node(node)
        assert len(topology.nodes) == 1
        assert "node1" in topology.nodes
    
    def test_topology_add_edge(self):
        """Test adding edge to topology."""
        topology = NetworkTopology()
        
        # Add two nodes
        node1 = MeshNode("node1", "N1", "Node 1", "TTGO", "2.3.0")
        node2 = MeshNode("node2", "N2", "Node 2", "TTGO", "2.3.0")
        topology.add_node(node1)
        topology.add_node(node2)
        
        # Add edge
        topology.add_edge("node1", "node2")
        assert len(topology.edges) == 1
        assert "node2" in topology.nodes["node1"].neighbors
        assert "node1" in topology.nodes["node2"].neighbors
    
    def test_network_manager_initialization(self):
        """Test MeshNetworkManager initialization."""
        manager = MeshNetworkManager()
        assert isinstance(manager.topology, NetworkTopology)
        assert len(manager.message_history) == 0
    
    def test_update_node(self):
        """Test updating node in network."""
        manager = MeshNetworkManager()
        node = MeshNode("node1", "N1", "Node 1", "TTGO", "2.3.0")
        
        manager.update_node(node)
        assert len(manager.topology.nodes) == 1
    
    def test_get_network_stats(self):
        """Test getting network statistics."""
        manager = MeshNetworkManager()
        
        # Add some nodes
        for i in range(3):
            node = MeshNode(
                f"node{i}",
                f"N{i}",
                f"Node {i}",
                "TTGO",
                "2.3.0",
                status=NodeStatus.ONLINE,
            )
            manager.update_node(node)
        
        stats = manager.get_network_stats()
        assert stats["total_nodes"] == 3
        assert stats["online_nodes"] == 3
    
    def test_find_route(self):
        """Test route finding."""
        manager = MeshNetworkManager()
        
        # Create a simple network: node1 -> node2 -> node3
        for i in range(1, 4):
            node = MeshNode(f"node{i}", f"N{i}", f"Node {i}", "TTGO", "2.3.0")
            manager.update_node(node)
        
        manager.update_connection("node1", "node2")
        manager.update_connection("node2", "node3")
        
        route = manager.find_route("node1", "node3")
        assert route is not None
        assert route[0] == "node1"
        assert route[-1] == "node3"
    
    def test_send_message(self):
        """Test sending message through network."""
        manager = MeshNetworkManager()
        
        # Create simple network
        node1 = MeshNode("node1", "N1", "Node 1", "TTGO", "2.3.0")
        node2 = MeshNode("node2", "N2", "Node 2", "TTGO", "2.3.0")
        manager.update_node(node1)
        manager.update_node(node2)
        manager.update_connection("node1", "node2")
        
        result = manager.send_message("node1", "node2", "Hello")
        assert result["status"] == "sent"
        assert len(manager.message_history) == 1


class TestOTAController:
    """Test OTA update functionality."""
    
    def test_update_progress_creation(self):
        """Test UpdateProgress creation."""
        progress = UpdateProgress(
            device_id="device1",
            firmware_version="2.3.0",
            method=OTAMethod.WIFI,
            status="pending",
        )
        
        assert progress.device_id == "device1"
        assert progress.firmware_version == "2.3.0"
        assert progress.method == OTAMethod.WIFI
    
    def test_update_progress_to_dict(self):
        """Test UpdateProgress conversion to dictionary."""
        progress = UpdateProgress(
            device_id="device1",
            firmware_version="2.3.0",
            method=OTAMethod.WIFI,
            status="pending",
        )
        
        result = progress.to_dict()
        assert result["device_id"] == "device1"
        assert result["method"] == "wifi"
        assert result["status"] == "pending"
    
    def test_ota_controller_initialization(self):
        """Test OTAController initialization."""
        controller = OTAController()
        assert len(controller.active_updates) == 0
        assert len(controller.update_history) == 0
    
    def test_get_active_updates(self):
        """Test getting active updates."""
        controller = OTAController()
        active = controller.get_active_updates()
        assert isinstance(active, dict)
        assert len(active) == 0
    
    def test_get_update_history(self):
        """Test getting update history."""
        controller = OTAController()
        history = controller.get_update_history()
        assert isinstance(history, list)
        assert len(history) == 0


class TestMeshtasticAgent:
    """Test Meshtastic agent functionality."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MeshtasticAgent()
        assert agent.name == "meshtastic_agent"
        assert "meshtastic" in agent.capabilities
    
    def test_can_handle_meshtastic(self):
        """Test agent can handle Meshtastic tasks."""
        agent = MeshtasticAgent()
        assert agent.can_handle("meshtastic device")
        assert agent.can_handle("mesh network")
        assert agent.can_handle("lora mesh")
    
    def test_discover_devices(self):
        """Test device discovery through agent."""
        agent = MeshtasticAgent()
        result = agent.generate({
            "task_type": "discover",
            "connection_type": "serial",
        })
        
        assert result["status"] == "success"
        assert "devices" in result
        assert "count" in result
    
    def test_firmware_list(self, tmp_path):
        """Test firmware listing through agent."""
        agent = MeshtasticAgent()
        result = agent.generate({
            "task_type": "firmware",
            "operation": "list",
        })
        
        assert result["status"] == "success"
        assert "firmware" in result
    
    def test_network_stats(self):
        """Test network statistics through agent."""
        agent = MeshtasticAgent()
        result = agent.generate({
            "task_type": "network",
            "operation": "stats",
        })
        
        assert result["status"] == "success"
        assert "stats" in result
    
    def test_generate_code(self):
        """Test code generation through agent."""
        agent = MeshtasticAgent()
        result = agent.generate({
            "task_type": "generate",
            "platform": "esp32",
            "device_name": "TestNode",
            "features": ["wifi", "gps"],
        })
        
        assert result["status"] == "success"
        assert "files" in result
        assert "main.cpp" in result["files"]
        assert "config.h" in result["files"]
    
    def test_get_platform_support(self):
        """Test getting supported platforms."""
        agent = MeshtasticAgent()
        platforms = agent.get_platform_support()
        
        assert "esp32" in platforms
        assert "nrf52" in platforms
    
    def test_get_info(self):
        """Test getting agent information."""
        agent = MeshtasticAgent()
        info = agent.get_info()
        
        assert info["name"] == "meshtastic_agent"
        assert "capabilities" in info
        assert "supported_platforms" in info


class TestMeshtasticPlatforms:
    """Test Meshtastic platform implementations."""
    
    def test_esp32_platform_info(self):
        """Test ESP32 platform information."""
        platform = MeshtasticESP32Platform()
        info = platform.get_platform_info()
        
        assert info["name"] == "meshtastic-esp32"
        assert info["base_platform"] == "ESP32"
        assert "LoRa mesh networking" in info["capabilities"]
    
    def test_esp32_code_generation(self, tmp_path):
        """Test ESP32 code generation."""
        platform = MeshtasticESP32Platform()
        
        spec = {
            "device_name": "TestNode",
            "features": ["wifi", "gps"],
            "radio_config": {
                "frequency": 915.0,
                "bandwidth": 125.0,
                "spreading_factor": 7,
            },
        }
        
        result = platform.generate_code(spec, tmp_path)
        
        assert result["status"] == "success"
        assert result["platform"] == "meshtastic-esp32"
        assert len(result["files_generated"]) >= 2
        
        # Check files exist
        assert (tmp_path / "main.cpp").exists()
        assert (tmp_path / "config.h").exists()
    
    def test_nrf52_platform_info(self):
        """Test nRF52 platform information."""
        platform = MeshtasticNRF52Platform()
        info = platform.get_platform_info()
        
        assert info["name"] == "meshtastic-nrf52"
        assert info["base_platform"] == "nRF52"
        assert "LoRa mesh networking" in info["capabilities"]
    
    def test_nrf52_code_generation(self, tmp_path):
        """Test nRF52 code generation."""
        platform = MeshtasticNRF52Platform()
        
        spec = {
            "device_name": "TestNode",
            "features": ["bluetooth"],
        }
        
        result = platform.generate_code(spec, tmp_path)
        
        assert result["status"] == "success"
        assert result["platform"] == "meshtastic-nrf52"
        assert (tmp_path / "main.cpp").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
