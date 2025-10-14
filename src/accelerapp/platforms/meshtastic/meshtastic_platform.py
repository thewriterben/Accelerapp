"""
Meshtastic platform implementation.
Main platform class integrating all Meshtastic capabilities.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from ..base import BasePlatform
from .device_interface import (
    MeshtasticDeviceInterface,
    DeviceDiscovery,
    ConnectionType,
    MeshtasticDevice,
)
from .firmware_manager import FirmwareManager, HardwareModel, FirmwareVersion
from .ota_controller import OTAController, OTAMethod

logger = logging.getLogger(__name__)


class MeshtasticPlatform(BasePlatform):
    """
    Meshtastic mesh communication platform.
    Supports device programming, configuration, and mesh network management.
    """
    
    def __init__(self, air_gapped: bool = False):
        """
        Initialize Meshtastic platform.
        
        Args:
            air_gapped: If True, operate in air-gapped mode
        """
        super().__init__()
        self.name = "meshtastic"
        self.air_gapped = air_gapped
        self.supported_languages = ["c", "cpp", "python"]
        
        # Meshtastic capabilities
        self.capabilities = [
            "mesh_networking",
            "lora",
            "ble",
            "wifi",
            "gps",
            "encryption",
            "long_range",
            "offline_messaging",
            "position_sharing",
            "telemetry",
            "remote_config",
            "ota_updates",
        ]
        
        self.peripherals = [
            "lora_radio",
            "gps_module",
            "display",
            "bluetooth",
            "battery_monitor",
            "environmental_sensor",
        ]
        
        # Initialize subsystems
        self.device_discovery = DeviceDiscovery()
        self.firmware_manager = FirmwareManager(
            offline_mode=air_gapped,
            firmware_dir=Path.home() / ".accelerapp" / "meshtastic_firmware"
        )
        self.ota_controller = OTAController(air_gapped=air_gapped)
        
        # Hardware model support
        self.supported_hardware = [
            "ESP32-based (T-Beam, TTGO LoRa)",
            "nRF52-based (RAK4631, Nordic DK)",
            "Custom hardware builds",
        ]
        
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Meshtastic platform information."""
        return {
            "name": self.name,
            "display_name": "Meshtastic Mesh Network",
            "version": "1.0.0",
            "languages": self.supported_languages,
            "capabilities": self.capabilities,
            "peripherals": self.peripherals,
            "air_gapped_mode": self.air_gapped,
            "description": "Long-range mesh communication platform using LoRa",
            "protocols": {
                "wireless": ["LoRa", "BLE", "WiFi"],
                "mesh": "Meshtastic protocol",
                "encryption": "AES-256",
            },
            "supported_hardware": self.supported_hardware,
            "frequency_bands": ["433MHz", "868MHz", "915MHz"],
            "max_range": "10km+ (line of sight)",
            "features": {
                "offline_messaging": True,
                "position_sharing": True,
                "mesh_routing": True,
                "encryption": True,
                "ota_updates": True,
                "air_gapped_support": True,
            },
        }
    
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate Meshtastic configuration and integration code.
        
        Args:
            spec: Hardware specification
            output_dir: Output directory
            
        Returns:
            Generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        hardware_model = spec.get("hardware_model", "esp32")
        task = spec.get("task", "configure")
        
        generated_files = []
        
        if task == "configure":
            # Generate device configuration
            config_file = self._generate_device_config(spec, output_dir)
            generated_files.append(config_file)
            
        elif task == "firmware":
            # Generate custom firmware configuration
            firmware_config = self._generate_firmware_config(spec, output_dir)
            generated_files.append(firmware_config)
            
        elif task == "integration":
            # Generate integration code for other platforms
            integration_code = self._generate_integration_code(spec, output_dir)
            generated_files.extend(integration_code)
            
        return {
            "status": "success",
            "platform": self.name,
            "hardware_model": hardware_model,
            "files_generated": [str(f) for f in generated_files],
            "output_dir": str(output_dir),
        }
    
    def _generate_device_config(self, spec: Dict[str, Any], output_dir: Path) -> Path:
        """Generate Meshtastic device configuration file."""
        config = {
            "device": {
                "role": spec.get("role", "CLIENT"),
                "serial_enabled": spec.get("serial_enabled", True),
                "debug_log_enabled": spec.get("debug_enabled", False),
            },
            "position": {
                "gps_enabled": spec.get("gps_enabled", True),
                "position_broadcast_secs": spec.get("position_interval", 900),
            },
            "lora": {
                "region": spec.get("region", "US"),
                "modem_preset": spec.get("modem_preset", "LONG_FAST"),
                "hop_limit": spec.get("hop_limit", 3),
            },
            "bluetooth": {
                "enabled": spec.get("bluetooth_enabled", True),
                "mode": spec.get("bluetooth_mode", "RANDOM_PIN"),
            },
            "network": {
                "wifi_enabled": spec.get("wifi_enabled", False),
                "wifi_ssid": spec.get("wifi_ssid", ""),
                "ntp_server": spec.get("ntp_server", "pool.ntp.org"),
            },
            "channels": spec.get("channels", [
                {"index": 0, "name": "Primary", "psk": "AQ=="}
            ]),
        }
        
        # Write configuration
        import yaml
        config_file = output_dir / "meshtastic_config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
            
        logger.info(f"Generated device configuration: {config_file}")
        return config_file
    
    def _generate_firmware_config(self, spec: Dict[str, Any], output_dir: Path) -> Path:
        """Generate custom firmware build configuration."""
        config = {
            "hardware_model": spec.get("hardware_model", "esp32"),
            "build_options": {
                "debug": spec.get("debug_build", False),
                "optimize": spec.get("optimize", "size"),
            },
            "features": {
                "gps": spec.get("enable_gps", True),
                "bluetooth": spec.get("enable_bluetooth", True),
                "wifi": spec.get("enable_wifi", True),
                "display": spec.get("enable_display", True),
            },
            "custom_defines": spec.get("custom_defines", {}),
        }
        
        import json
        config_file = output_dir / "firmware_build_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Generated firmware configuration: {config_file}")
        return config_file
    
    def _generate_integration_code(self, spec: Dict[str, Any], output_dir: Path) -> List[Path]:
        """Generate code for integrating Meshtastic with other platforms."""
        files = []
        target_language = spec.get("language", "python")
        
        if target_language == "python":
            # Generate Python integration code
            python_file = output_dir / "meshtastic_integration.py"
            python_code = '''"""
Meshtastic integration module.
Generated by Accelerapp.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MeshtasticClient:
    """Client for Meshtastic device communication."""
    
    def __init__(self, device_port: str):
        """Initialize Meshtastic client."""
        self.device_port = device_port
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to Meshtastic device."""
        try:
            # Import meshtastic library
            # from meshtastic import SerialInterface
            # self.interface = SerialInterface(self.device_port)
            logger.info(f"Connected to Meshtastic device on {self.device_port}")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
            
    def send_message(self, message: str, channel: int = 0) -> bool:
        """Send text message."""
        if not self.connected:
            logger.error("Not connected to device")
            return False
        logger.info(f"Sending message: {message}")
        # Implement actual message sending
        return True
        
    def get_node_info(self) -> Optional[Dict[str, Any]]:
        """Get mesh network node information."""
        if not self.connected:
            return None
        # Implement node info retrieval
        return {"nodes": [], "count": 0}


if __name__ == "__main__":
    # Example usage
    client = MeshtasticClient("/dev/ttyUSB0")
    if client.connect():
        client.send_message("Hello from Accelerapp!")
        nodes = client.get_node_info()
        print(f"Mesh network nodes: {nodes}")
'''
            python_file.write_text(python_code)
            files.append(python_file)
            logger.info(f"Generated Python integration: {python_file}")
            
        elif target_language in ["c", "cpp"]:
            # Generate C/C++ integration code
            header_file = output_dir / "meshtastic_integration.h"
            header_code = '''/**
 * Meshtastic integration header.
 * Generated by Accelerapp.
 */

#ifndef MESHTASTIC_INTEGRATION_H
#define MESHTASTIC_INTEGRATION_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Initialize Meshtastic
bool meshtastic_init(const char* device_port);

// Send text message
bool meshtastic_send_message(const char* message, uint8_t channel);

// Get node count
int meshtastic_get_node_count(void);

// Shutdown Meshtastic
void meshtastic_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif // MESHTASTIC_INTEGRATION_H
'''
            header_file.write_text(header_code)
            files.append(header_file)
            logger.info(f"Generated C/C++ header: {header_file}")
            
        return files
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate Meshtastic configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate hardware model
        if "hardware_model" in config:
            model = config["hardware_model"]
            valid_models = ["esp32", "nrf52", "tbeam", "tlora", "rak4631"]
            if model not in valid_models:
                errors.append(f"Invalid hardware model: {model}. Must be one of {valid_models}")
        
        # Validate region
        if "region" in config:
            region = config["region"]
            valid_regions = ["US", "EU_433", "EU_868", "CN", "JP", "ANZ", "KR", "TW", "RU", "IN", "NZ_865", "TH", "UA_433", "UA_868"]
            if region not in valid_regions:
                errors.append(f"Invalid region: {region}")
        
        # Validate channels
        if "channels" in config:
            channels = config["channels"]
            if not isinstance(channels, list):
                errors.append("Channels must be a list")
            elif len(channels) > 8:
                errors.append("Maximum 8 channels supported")
                
        return errors
    
    def discover_devices(self) -> List[MeshtasticDevice]:
        """
        Discover available Meshtastic devices.
        
        Returns:
            List of discovered devices
        """
        return self.device_discovery.discover_all()
    
    def connect_device(self, device: MeshtasticDevice) -> Optional[MeshtasticDeviceInterface]:
        """
        Connect to a Meshtastic device.
        
        Args:
            device: Device to connect to
            
        Returns:
            Device interface if successful, None otherwise
        """
        interface = MeshtasticDeviceInterface(device)
        if interface.connect():
            return interface
        return None
    
    def flash_firmware(
        self,
        device_port: str,
        hardware_model: HardwareModel,
        version: Optional[str] = None
    ) -> bool:
        """
        Flash firmware to a device.
        
        Args:
            device_port: Serial port of device
            hardware_model: Hardware model
            version: Firmware version (latest if not specified)
            
        Returns:
            True if successful
        """
        # Get firmware
        if version:
            versions = self.firmware_manager.list_available_versions(hardware_model)
            firmware = next((v for v in versions if v.version == version), None)
            if not firmware or not firmware.file_path:
                logger.error(f"Firmware version {version} not found")
                return False
            firmware_path = firmware.file_path
        else:
            # Use latest available
            versions = self.firmware_manager.list_available_versions(hardware_model)
            if not versions:
                logger.error("No firmware versions available")
                return False
            firmware_path = versions[0].file_path
            
        if not firmware_path:
            logger.error("No firmware file available")
            return False
            
        # Flash firmware
        return self.firmware_manager.flash_firmware(device_port, firmware_path)
    
    def perform_ota_update(
        self,
        device_id: str,
        firmware_path: Path,
        method: OTAMethod = OTAMethod.WIFI
    ) -> bool:
        """
        Perform OTA firmware update.
        
        Args:
            device_id: Device identifier
            firmware_path: Path to firmware
            method: OTA method
            
        Returns:
            True if successful
        """
        return self.ota_controller.perform_ota_update(device_id, firmware_path, method)
