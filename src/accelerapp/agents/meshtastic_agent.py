"""
Meshtastic Agent specialized in mesh network operations.
Handles device discovery, configuration, firmware management, and mesh networking.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class MeshtasticAgent(BaseAgent):
    """
    Specialized agent for Meshtastic mesh communication operations.
    Expert in LoRa mesh networks, device programming, and OTA updates.
    """
    
    def __init__(self):
        """Initialize Meshtastic agent."""
        capabilities = [
            "device_discovery",
            "device_configuration",
            "firmware_management",
            "ota_updates",
            "mesh_networking",
            "air_gapped_deployment",
        ]
        super().__init__("MeshtasticAgent", capabilities)
        self.description = "Specialist in Meshtastic mesh networking and device management"
        
    def can_handle(self, task: str) -> bool:
        """
        Check if agent can handle the task.
        
        Args:
            task: Task description
            
        Returns:
            True if agent can handle the task
        """
        meshtastic_keywords = [
            "meshtastic",
            "mesh",
            "lora",
            "mesh network",
            "mesh communication",
            "ota update",
            "device discovery",
            "air-gapped",
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in meshtastic_keywords)
    
    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute Meshtastic operations.
        
        Args:
            spec: Operation specification
            context: Optional context
            
        Returns:
            Operation results
        """
        operation = spec.get("operation", "info")
        
        if operation == "discover":
            return self._discover_devices(spec)
        elif operation == "configure":
            return self._configure_device(spec)
        elif operation == "flash_firmware":
            return self._flash_firmware(spec)
        elif operation == "ota_update":
            return self._perform_ota_update(spec)
        elif operation == "generate_config":
            return self._generate_configuration(spec)
        elif operation == "mesh_status":
            return self._get_mesh_status(spec)
        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}",
                "agent": self.name,
            }
    
    def _discover_devices(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Discover Meshtastic devices."""
        try:
            from ..platforms.meshtastic import MeshtasticPlatform
            
            air_gapped = spec.get("air_gapped", False)
            platform = MeshtasticPlatform(air_gapped=air_gapped)
            
            devices = platform.discover_devices()
            
            return {
                "status": "success",
                "operation": "discover",
                "devices": [device.to_dict() for device in devices],
                "count": len(devices),
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _configure_device(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Configure a Meshtastic device."""
        try:
            from ..platforms.meshtastic import MeshtasticPlatform
            
            platform = MeshtasticPlatform(air_gapped=spec.get("air_gapped", False))
            
            # Generate configuration
            output_dir = Path(spec.get("output_dir", "/tmp/meshtastic_config"))
            result = platform.generate_code(spec, output_dir)
            
            return {
                "status": "success",
                "operation": "configure",
                "result": result,
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"Device configuration failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _flash_firmware(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Flash firmware to a device."""
        try:
            from ..platforms.meshtastic import MeshtasticPlatform
            from ..platforms.meshtastic.firmware_manager import HardwareModel
            
            platform = MeshtasticPlatform(air_gapped=spec.get("air_gapped", False))
            
            device_port = spec.get("device_port")
            hardware_model_str = spec.get("hardware_model", "esp32")
            version = spec.get("version")
            
            if not device_port:
                return {
                    "status": "error",
                    "message": "device_port is required",
                    "agent": self.name,
                }
            
            # Map hardware model
            hardware_model = HardwareModel.CUSTOM
            if "tbeam" in hardware_model_str.lower():
                hardware_model = HardwareModel.TBEAM
            elif "tlora" in hardware_model_str.lower():
                hardware_model = HardwareModel.TLORA_V2
            elif "rak4631" in hardware_model_str.lower():
                hardware_model = HardwareModel.RAK4631
            
            success = platform.flash_firmware(device_port, hardware_model, version)
            
            return {
                "status": "success" if success else "error",
                "operation": "flash_firmware",
                "device_port": device_port,
                "hardware_model": hardware_model.value,
                "version": version,
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"Firmware flashing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _perform_ota_update(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform OTA firmware update."""
        try:
            from ..platforms.meshtastic import MeshtasticPlatform, OTAMethod
            
            platform = MeshtasticPlatform(air_gapped=spec.get("air_gapped", False))
            
            device_id = spec.get("device_id")
            firmware_path = Path(spec.get("firmware_path"))
            method_str = spec.get("method", "wifi")
            
            if not device_id:
                return {
                    "status": "error",
                    "message": "device_id is required",
                    "agent": self.name,
                }
            
            if not firmware_path.exists():
                return {
                    "status": "error",
                    "message": f"Firmware file not found: {firmware_path}",
                    "agent": self.name,
                }
            
            # Map OTA method
            method = OTAMethod.WIFI
            if method_str.lower() == "ble":
                method = OTAMethod.BLE
            
            success = platform.perform_ota_update(device_id, firmware_path, method)
            
            return {
                "status": "success" if success else "error",
                "operation": "ota_update",
                "device_id": device_id,
                "method": method.value,
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"OTA update failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _generate_configuration(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Meshtastic configuration files."""
        try:
            from ..platforms.meshtastic import MeshtasticPlatform
            
            platform = MeshtasticPlatform(air_gapped=spec.get("air_gapped", False))
            
            output_dir = Path(spec.get("output_dir", "/tmp/meshtastic_config"))
            spec["task"] = "configure"
            
            result = platform.generate_code(spec, output_dir)
            
            return {
                "status": "success",
                "operation": "generate_config",
                "result": result,
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"Configuration generation failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _get_mesh_status(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get mesh network status."""
        # Placeholder for mesh status retrieval
        return {
            "status": "success",
            "operation": "mesh_status",
            "message": "Mesh status retrieval not yet implemented",
            "agent": self.name,
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.capabilities.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_operations": [
                "discover",
                "configure",
                "flash_firmware",
                "ota_update",
                "generate_config",
                "mesh_status",
            ],
            "platforms": ["ESP32", "nRF52"],
            "features": {
                "device_discovery": True,
                "firmware_management": True,
                "ota_updates": True,
                "air_gapped_support": True,
                "mesh_networking": True,
            },
        }
