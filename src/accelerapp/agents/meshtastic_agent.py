"""
Meshtastic Agent specialized in mesh communication systems.
Handles device programming, network management, and firmware operations.
"""

from typing import Dict, Any, List
from pathlib import Path
from .base_agent import BaseAgent


class MeshtasticAgent(BaseAgent):
    """
    Specialized agent for Meshtastic mesh communication systems.
    Expert in mesh networking, device programming, and firmware management.
    """
    
    def __init__(self):
        """Initialize Meshtastic agent."""
        super().__init__(
            name="meshtastic_agent",
            capabilities=[
                "meshtastic",
                "mesh_network",
                "device_programming",
                "firmware_management",
                "ota_updates",
                "network_topology",
                "mesh_routing",
            ]
        )
        self.supported_platforms = ["esp32", "nrf52", "nrf52840", "rp2040"]
    
    def can_handle(self, task: str) -> bool:
        """
        Check if this agent can handle a specific task type.
        
        Args:
            task: Task identifier
            
        Returns:
            True if agent can handle task
        """
        task_lower = task.lower()
        meshtastic_keywords = [
            "meshtastic",
            "mesh",
            "lora",
            "mesh network",
            "mesh node",
            "mesh device",
        ]
        return any(keyword in task_lower for keyword in meshtastic_keywords)
    
    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate Meshtastic-related code or configuration.
        
        Args:
            spec: Meshtastic specification
            context: Additional context
            
        Returns:
            Generated output
        """
        task_type = spec.get("task_type", "generate")
        
        if task_type == "discover":
            return self._discover_devices(spec)
        elif task_type == "configure":
            return self._configure_device(spec)
        elif task_type == "firmware":
            return self._manage_firmware(spec)
        elif task_type == "network":
            return self._manage_network(spec)
        elif task_type == "ota":
            return self._perform_ota(spec)
        elif task_type == "generate":
            return self._generate_meshtastic_code(spec)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
    
    def _discover_devices(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover Meshtastic devices.
        
        Args:
            spec: Discovery specification
            
        Returns:
            List of discovered devices
        """
        from ..meshtastic.device_interface import DeviceDiscovery
        
        connection_type = spec.get("connection_type", "all")
        
        if connection_type == "serial":
            devices = DeviceDiscovery.discover_serial()
        elif connection_type == "wifi":
            devices = DeviceDiscovery.discover_wifi()
        elif connection_type == "bluetooth":
            devices = DeviceDiscovery.discover_bluetooth()
        else:
            devices = DeviceDiscovery.discover_all()
        
        return {
            "status": "success",
            "devices": [d.to_dict() for d in devices],
            "count": len(devices),
            "agent": self.name,
        }
    
    def _configure_device(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure Meshtastic device.
        
        Args:
            spec: Configuration specification
            
        Returns:
            Configuration result
        """
        device_id = spec.get("device_id")
        config = spec.get("config", {})
        
        if not device_id:
            return {"status": "error", "message": "device_id required"}
        
        # Configuration items
        region = config.get("region", "US")
        channels = config.get("channels", [])
        lora_config = config.get("lora", {})
        
        return {
            "status": "success",
            "device_id": device_id,
            "configured": {
                "region": region,
                "channels": len(channels),
                "lora_settings": lora_config,
            },
            "agent": self.name,
        }
    
    def _manage_firmware(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage firmware operations.
        
        Args:
            spec: Firmware specification
            
        Returns:
            Firmware operation result
        """
        from ..meshtastic.firmware_manager import FirmwareManager
        
        operation = spec.get("operation", "list")
        hardware_model = spec.get("hardware_model")
        platform = spec.get("platform")
        
        manager = FirmwareManager()
        
        if operation == "list":
            firmware_list = manager.list_firmware(hardware_model, platform)
            return {
                "status": "success",
                "firmware": [f.to_dict() for f in firmware_list],
                "count": len(firmware_list),
                "agent": self.name,
            }
        
        elif operation == "latest":
            if not hardware_model or not platform:
                return {"status": "error", "message": "hardware_model and platform required"}
            
            latest = manager.get_latest_firmware(hardware_model, platform)
            if latest:
                return {
                    "status": "success",
                    "firmware": latest.to_dict(),
                    "agent": self.name,
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No firmware found for specified hardware",
                    "agent": self.name,
                }
        
        elif operation == "add":
            firmware_path = spec.get("firmware_path")
            version = spec.get("version")
            
            if not all([firmware_path, version, hardware_model, platform]):
                return {"status": "error", "message": "Missing required parameters"}
            
            firmware = manager.add_firmware(
                Path(firmware_path),
                version,
                hardware_model,
                platform
            )
            
            return {
                "status": "success",
                "firmware": firmware.to_dict(),
                "agent": self.name,
            }
        
        return {"status": "error", "message": f"Unknown operation: {operation}"}
    
    def _manage_network(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage mesh network operations.
        
        Args:
            spec: Network specification
            
        Returns:
            Network operation result
        """
        from ..meshtastic.network_manager import MeshNetworkManager, MeshNode, NodeStatus
        
        operation = spec.get("operation", "stats")
        
        manager = MeshNetworkManager()
        
        if operation == "stats":
            stats = manager.get_network_stats()
            return {
                "status": "success",
                "stats": stats,
                "agent": self.name,
            }
        
        elif operation == "topology":
            topology = manager.get_topology()
            return {
                "status": "success",
                "topology": topology.to_dict(),
                "agent": self.name,
            }
        
        elif operation == "route":
            source_id = spec.get("source_id")
            dest_id = spec.get("dest_id")
            
            if not source_id or not dest_id:
                return {"status": "error", "message": "source_id and dest_id required"}
            
            route = manager.find_route(source_id, dest_id)
            
            if route:
                return {
                    "status": "success",
                    "route": route,
                    "hop_count": len(route) - 1,
                    "agent": self.name,
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No route found",
                    "agent": self.name,
                }
        
        return {"status": "error", "message": f"Unknown operation: {operation}"}
    
    def _perform_ota(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform OTA firmware update.
        
        Args:
            spec: OTA specification
            
        Returns:
            OTA operation result
        """
        from ..meshtastic.ota_controller import OTAController, OTAMethod
        
        device_id = spec.get("device_id")
        firmware_path = spec.get("firmware_path")
        method = spec.get("method", "wifi")
        
        if not device_id or not firmware_path:
            return {"status": "error", "message": "device_id and firmware_path required"}
        
        controller = OTAController()
        
        # Convert method string to enum
        ota_method = OTAMethod[method.upper()]
        
        try:
            progress = controller.start_update(
                device_id,
                Path(firmware_path),
                ota_method,
                spec.get("device_info")
            )
            
            return {
                "status": "success",
                "update": progress.to_dict(),
                "agent": self.name,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "agent": self.name,
            }
    
    def _generate_meshtastic_code(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Meshtastic firmware code.
        
        Args:
            spec: Code generation specification
            
        Returns:
            Generated code
        """
        platform = spec.get("platform", "esp32")
        device_name = spec.get("device_name", "MeshtasticNode")
        features = spec.get("features", [])
        
        if platform not in self.supported_platforms:
            return {
                "status": "error",
                "message": f"Platform {platform} not supported",
                "supported_platforms": self.supported_platforms,
            }
        
        # Generate basic Meshtastic node code
        code = self._generate_node_code(platform, device_name, features)
        config = self._generate_node_config(platform, device_name, features)
        
        return {
            "status": "success",
            "platform": platform,
            "files": {
                "main.cpp": code,
                "config.h": config,
            },
            "features": features,
            "agent": self.name,
        }
    
    def _generate_node_code(
        self,
        platform: str,
        device_name: str,
        features: List[str]
    ) -> str:
        """Generate Meshtastic node main code."""
        
        if platform == "esp32":
            return f'''// Meshtastic Node - {device_name}
// Platform: ESP32
// Generated by: Accelerapp Meshtastic Agent

#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"

// LoRa radio configuration
SX1276 radio = new Module(LORA_CS, LORA_DIO0, LORA_RST, LORA_DIO1);

void setup() {{
    Serial.begin(115200);
    Serial.println("{device_name} starting...");
    
    // Initialize LoRa radio
    int state = radio.begin();
    if (state == RADIOLIB_ERR_NONE) {{
        Serial.println("LoRa radio initialized");
    }} else {{
        Serial.print("LoRa init failed: ");
        Serial.println(state);
    }}
    
    // Configure radio parameters
    radio.setFrequency(LORA_FREQUENCY);
    radio.setBandwidth(LORA_BANDWIDTH);
    radio.setSpreadingFactor(LORA_SPREADING_FACTOR);
    radio.setCodingRate(LORA_CODING_RATE);
    radio.setSyncWord(LORA_SYNC_WORD);
    radio.setOutputPower(LORA_POWER);
    
    Serial.println("Meshtastic node ready");
}}

void loop() {{
    // Check for incoming messages
    String message;
    int state = radio.receive(message);
    
    if (state == RADIOLIB_ERR_NONE) {{
        Serial.print("Received: ");
        Serial.println(message);
        
        // Process message
        handleMeshMessage(message);
    }}
    
    delay(100);
}}

void handleMeshMessage(String message) {{
    // Message handling logic
    Serial.println("Processing mesh message...");
}}

void sendMeshMessage(String message, uint32_t destination) {{
    int state = radio.transmit(message);
    if (state == RADIOLIB_ERR_NONE) {{
        Serial.println("Message sent successfully");
    }} else {{
        Serial.print("Send failed: ");
        Serial.println(state);
    }}
}}
'''
        
        elif platform in ["nrf52", "nrf52840"]:
            return f'''// Meshtastic Node - {device_name}
// Platform: {platform.upper()}
// Generated by: Accelerapp Meshtastic Agent

#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"

// LoRa radio configuration
SX1262 radio = new Module(LORA_CS, LORA_DIO1, LORA_RST, LORA_BUSY);

void setup() {{
    Serial.begin(115200);
    Serial.println("{device_name} starting...");
    
    // Initialize LoRa radio
    int state = radio.begin();
    if (state == RADIOLIB_ERR_NONE) {{
        Serial.println("LoRa radio initialized");
    }} else {{
        Serial.print("LoRa init failed: ");
        Serial.println(state);
    }}
    
    // Configure radio
    radio.setFrequency(LORA_FREQUENCY);
    radio.setBandwidth(LORA_BANDWIDTH);
    radio.setSpreadingFactor(LORA_SPREADING_FACTOR);
    
    Serial.println("Meshtastic node ready");
}}

void loop() {{
    // Nordic-specific mesh operations
    delay(100);
}}
'''
        
        return "// Platform not implemented"
    
    def _generate_node_config(
        self,
        platform: str,
        device_name: str,
        features: List[str]
    ) -> str:
        """Generate Meshtastic node configuration."""
        
        return f'''// Meshtastic Node Configuration
// Device: {device_name}
// Platform: {platform}

#ifndef CONFIG_H
#define CONFIG_H

// Device Configuration
#define DEVICE_NAME "{device_name}"
#define NODE_ID 0x{hash(device_name) & 0xFFFFFFFF:08X}

// LoRa Radio Configuration
#define LORA_FREQUENCY 915.0    // MHz (US frequency)
#define LORA_BANDWIDTH 125.0    // kHz
#define LORA_SPREADING_FACTOR 7
#define LORA_CODING_RATE 5
#define LORA_SYNC_WORD 0x12
#define LORA_POWER 20           // dBm

// Pin Configuration
{"#define LORA_CS 18" if platform == "esp32" else "#define LORA_CS 8"}
{"#define LORA_DIO0 26" if platform == "esp32" else "#define LORA_DIO1 3"}
{"#define LORA_RST 23" if platform == "esp32" else "#define LORA_RST 2"}
{"#define LORA_DIO1 33" if platform == "esp32" else "#define LORA_BUSY 4"}

// Mesh Configuration
#define MAX_HOPS 3
#define MESH_TIMEOUT_MS 30000
#define BEACON_INTERVAL_MS 60000

// Feature Flags
{"#define FEATURE_GPS" if "gps" in features else "// GPS disabled"}
{"#define FEATURE_ENVIRONMENT" if "environment" in features else "// Environment sensors disabled"}
{"#define FEATURE_DISPLAY" if "display" in features else "// Display disabled"}

#endif // CONFIG_H
'''
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.capabilities
    
    def get_platform_support(self) -> Dict[str, str]:
        """Get supported platforms."""
        return {
            "esp32": "ESP32 (SX1276/SX1262 LoRa)",
            "nrf52": "Nordic nRF52 (SX1262 LoRa)",
            "nrf52840": "Nordic nRF52840 (SX1262 LoRa)",
            "rp2040": "Raspberry Pi Pico (SX1276 LoRa)",
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": self.name,
            "type": "meshtastic_agent",
            "capabilities": self.capabilities,
            "supported_platforms": self.get_platform_support(),
            "description": "Specialized agent for Meshtastic mesh communication systems",
            "features": [
                "Device discovery (Serial, WiFi, Bluetooth)",
                "Firmware management and OTA updates",
                "Mesh network topology and routing",
                "LoRa radio configuration",
                "Multi-platform code generation",
                "Air-gapped deployment support",
            ],
        }
