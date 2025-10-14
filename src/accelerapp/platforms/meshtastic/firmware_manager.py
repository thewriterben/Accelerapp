"""
Meshtastic firmware management module.
Handles firmware versions, downloads, and flashing.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HardwareModel(Enum):
    """Supported Meshtastic hardware models."""
    TBEAM = "tbeam"
    TLORA_V2 = "tlora-v2"
    TLORA_V1 = "tlora-v1"
    HELTEC_V3 = "heltec-v3"
    HELTEC_V2 = "heltec-v2"
    RAK4631 = "rak4631"
    STATION_G1 = "station-g1"
    NANO_G1 = "nano-g1"
    NRF52840_DK = "nrf52840-dk"
    CUSTOM = "custom"


@dataclass
class FirmwareVersion:
    """Represents a firmware version."""
    version: str
    hardware_model: HardwareModel
    release_date: Optional[str] = None
    download_url: Optional[str] = None
    file_path: Optional[Path] = None
    checksum: Optional[str] = None
    changelog: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "hardware_model": self.hardware_model.value,
            "release_date": self.release_date,
            "download_url": self.download_url,
            "file_path": str(self.file_path) if self.file_path else None,
            "checksum": self.checksum,
            "changelog": self.changelog,
        }


class FirmwareManager:
    """
    Manages Meshtastic firmware versions and flashing.
    Supports both online and air-gapped (offline) modes.
    """
    
    def __init__(self, offline_mode: bool = False, firmware_dir: Optional[Path] = None):
        """
        Initialize firmware manager.
        
        Args:
            offline_mode: If True, only use local firmware repository
            firmware_dir: Directory for local firmware storage
        """
        self.offline_mode = offline_mode
        self.firmware_dir = firmware_dir or Path.home() / ".accelerapp" / "meshtastic_firmware"
        self.firmware_dir.mkdir(parents=True, exist_ok=True)
        self._firmware_cache: Dict[str, FirmwareVersion] = {}
        
    def list_available_versions(self, hardware_model: HardwareModel) -> List[FirmwareVersion]:
        """
        List available firmware versions for a hardware model.
        
        Args:
            hardware_model: Target hardware model
            
        Returns:
            List of available firmware versions
        """
        versions = []
        
        if self.offline_mode:
            # Scan local firmware directory
            versions = self._scan_local_firmware(hardware_model)
        else:
            # Check online repository (placeholder)
            logger.info("Online firmware listing not yet implemented")
            # Would query GitHub releases API or Meshtastic firmware repo
            # Also check local cache
            versions.extend(self._scan_local_firmware(hardware_model))
            
        return versions
    
    def _scan_local_firmware(self, hardware_model: HardwareModel) -> List[FirmwareVersion]:
        """Scan local firmware directory for available versions."""
        versions = []
        
        # Look for firmware files in local directory
        pattern = f"*{hardware_model.value}*.bin"
        for firmware_file in self.firmware_dir.glob(pattern):
            # Try to extract version from filename
            version_str = self._extract_version_from_filename(firmware_file.name)
            version = FirmwareVersion(
                version=version_str,
                hardware_model=hardware_model,
                file_path=firmware_file,
            )
            versions.append(version)
            
        return versions
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """Extract version string from firmware filename."""
        # Simple extraction - could be enhanced
        import re
        match = re.search(r'v?(\d+\.\d+\.\d+)', filename)
        if match:
            return match.group(1)
        return "unknown"
    
    def download_firmware(
        self,
        version: str,
        hardware_model: HardwareModel,
        force: bool = False
    ) -> Optional[Path]:
        """
        Download firmware version.
        
        Args:
            version: Firmware version to download
            hardware_model: Target hardware model
            force: Force re-download if already cached
            
        Returns:
            Path to downloaded firmware file, or None if failed
        """
        if self.offline_mode:
            logger.error("Cannot download firmware in offline mode")
            return None
            
        # Check cache first
        cache_key = f"{hardware_model.value}_{version}"
        if cache_key in self._firmware_cache and not force:
            cached_version = self._firmware_cache[cache_key]
            if cached_version.file_path and cached_version.file_path.exists():
                return cached_version.file_path
                
        # Placeholder for actual download implementation
        logger.warning(f"Firmware download not yet implemented for {version} on {hardware_model.value}")
        # Would download from GitHub releases or Meshtastic CDN
        
        return None
    
    def flash_firmware(
        self,
        device_port: str,
        firmware_path: Path,
        erase_flash: bool = False
    ) -> bool:
        """
        Flash firmware to a device.
        
        Args:
            device_port: Serial port of the device
            firmware_path: Path to firmware binary
            erase_flash: Whether to erase flash before flashing
            
        Returns:
            True if flashing successful
        """
        if not firmware_path.exists():
            logger.error(f"Firmware file not found: {firmware_path}")
            return False
            
        logger.info(f"Flashing firmware to {device_port}")
        logger.info(f"Firmware: {firmware_path}")
        logger.info(f"Erase flash: {erase_flash}")
        
        # Placeholder for actual flashing implementation
        # Would use esptool.py for ESP32 or nrfutil for nRF52
        # Example: esptool.py --port {device_port} write_flash 0x10000 {firmware_path}
        
        logger.warning("Firmware flashing not yet fully implemented")
        return True
    
    def verify_firmware(self, firmware_path: Path, expected_checksum: Optional[str] = None) -> bool:
        """
        Verify firmware integrity.
        
        Args:
            firmware_path: Path to firmware file
            expected_checksum: Expected checksum (SHA256)
            
        Returns:
            True if firmware is valid
        """
        if not firmware_path.exists():
            logger.error(f"Firmware file not found: {firmware_path}")
            return False
            
        if expected_checksum:
            import hashlib
            # Calculate SHA256
            sha256 = hashlib.sha256()
            with open(firmware_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            actual_checksum = sha256.hexdigest()
            
            if actual_checksum != expected_checksum:
                logger.error(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                return False
                
        return True
    
    def get_device_firmware_version(self, device_port: str) -> Optional[str]:
        """
        Get current firmware version from device.
        
        Args:
            device_port: Serial port of the device
            
        Returns:
            Firmware version string, or None if failed
        """
        logger.info(f"Querying firmware version from {device_port}")
        # Placeholder - would query device using meshtastic library
        return None
    
    def create_custom_firmware(
        self,
        base_version: str,
        hardware_model: HardwareModel,
        config: Dict[str, Any],
        output_path: Path
    ) -> bool:
        """
        Create custom firmware build.
        
        Args:
            base_version: Base firmware version
            hardware_model: Target hardware model
            config: Custom configuration
            output_path: Output path for custom firmware
            
        Returns:
            True if build successful
        """
        logger.info(f"Creating custom firmware for {hardware_model.value}")
        logger.info(f"Base version: {base_version}")
        logger.info(f"Custom config: {config}")
        
        # Placeholder for custom firmware building
        # Would integrate with PlatformIO or Meshtastic build system
        logger.warning("Custom firmware building not yet implemented")
        
        return False
