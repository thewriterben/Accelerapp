"""
Firmware management system for Meshtastic devices.
Handles firmware versioning, storage, and deployment.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import hashlib


class FirmwareUpdateStatus(Enum):
    """Status of firmware update operation."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    FLASHING = "flashing"
    VERIFYING = "verifying"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class FirmwareVersion:
    """Represents a Meshtastic firmware version."""
    
    version: str
    hardware_model: str
    platform: str  # esp32, nrf52, etc.
    build_date: datetime
    file_path: Optional[Path] = None
    file_size: int = 0
    checksum: str = ""
    is_official: bool = True
    release_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "hardware_model": self.hardware_model,
            "platform": self.platform,
            "build_date": self.build_date.isoformat(),
            "file_path": str(self.file_path) if self.file_path else None,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "is_official": self.is_official,
            "release_notes": self.release_notes,
        }


class FirmwareManager:
    """
    Manages Meshtastic firmware versions and deployment.
    Supports both online and air-gapped environments.
    """
    
    def __init__(self, firmware_dir: Optional[Path] = None):
        """
        Initialize firmware manager.
        
        Args:
            firmware_dir: Directory for firmware storage (for air-gapped mode)
        """
        self.firmware_dir = firmware_dir or Path.home() / ".accelerapp" / "meshtastic_firmware"
        self.firmware_dir.mkdir(parents=True, exist_ok=True)
        self.firmware_cache: Dict[str, FirmwareVersion] = {}
        self._load_local_firmware()
    
    def _load_local_firmware(self) -> None:
        """Load firmware from local storage."""
        if not self.firmware_dir.exists():
            return
        
        for firmware_file in self.firmware_dir.glob("*.bin"):
            # Parse firmware filename to extract metadata
            # Format: meshtastic-{version}-{hardware}-{platform}.bin
            parts = firmware_file.stem.split("-")
            if len(parts) >= 4:
                version = parts[1]
                hardware = parts[2]
                platform = parts[3]
                
                checksum = self._calculate_checksum(firmware_file)
                firmware = FirmwareVersion(
                    version=version,
                    hardware_model=hardware,
                    platform=platform,
                    build_date=datetime.fromtimestamp(firmware_file.stat().st_mtime),
                    file_path=firmware_file,
                    file_size=firmware_file.stat().st_size,
                    checksum=checksum,
                )
                
                key = f"{hardware}_{platform}_{version}"
                self.firmware_cache[key] = firmware
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of firmware file.
        
        Args:
            file_path: Path to firmware file
            
        Returns:
            Hex string of checksum
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def list_firmware(
        self,
        hardware_model: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[FirmwareVersion]:
        """
        List available firmware versions.
        
        Args:
            hardware_model: Filter by hardware model
            platform: Filter by platform
            
        Returns:
            List of firmware versions
        """
        firmware_list = list(self.firmware_cache.values())
        
        if hardware_model:
            firmware_list = [f for f in firmware_list if f.hardware_model == hardware_model]
        
        if platform:
            firmware_list = [f for f in firmware_list if f.platform == platform]
        
        # Sort by version (newest first)
        firmware_list.sort(key=lambda f: f.build_date, reverse=True)
        
        return firmware_list
    
    def get_latest_firmware(
        self,
        hardware_model: str,
        platform: str
    ) -> Optional[FirmwareVersion]:
        """
        Get the latest firmware for a specific hardware/platform.
        
        Args:
            hardware_model: Hardware model
            platform: Platform (esp32, nrf52, etc.)
            
        Returns:
            Latest firmware version or None
        """
        firmware_list = self.list_firmware(hardware_model, platform)
        return firmware_list[0] if firmware_list else None
    
    def add_firmware(
        self,
        firmware_file: Path,
        version: str,
        hardware_model: str,
        platform: str,
        is_official: bool = True
    ) -> FirmwareVersion:
        """
        Add firmware to local repository.
        
        Args:
            firmware_file: Path to firmware file
            version: Firmware version
            hardware_model: Hardware model
            platform: Platform
            is_official: Whether this is official firmware
            
        Returns:
            FirmwareVersion object
        """
        # Copy to firmware directory with standard naming
        dest_filename = f"meshtastic-{version}-{hardware_model}-{platform}.bin"
        dest_path = self.firmware_dir / dest_filename
        
        if firmware_file != dest_path:
            import shutil
            shutil.copy2(firmware_file, dest_path)
        
        checksum = self._calculate_checksum(dest_path)
        
        firmware = FirmwareVersion(
            version=version,
            hardware_model=hardware_model,
            platform=platform,
            build_date=datetime.now(),
            file_path=dest_path,
            file_size=dest_path.stat().st_size,
            checksum=checksum,
            is_official=is_official,
        )
        
        key = f"{hardware_model}_{platform}_{version}"
        self.firmware_cache[key] = firmware
        
        return firmware
    
    def verify_firmware(self, firmware: FirmwareVersion) -> bool:
        """
        Verify firmware integrity.
        
        Args:
            firmware: Firmware to verify
            
        Returns:
            True if valid, False otherwise
        """
        if not firmware.file_path or not firmware.file_path.exists():
            return False
        
        current_checksum = self._calculate_checksum(firmware.file_path)
        return current_checksum == firmware.checksum
    
    def delete_firmware(self, firmware: FirmwareVersion) -> bool:
        """
        Delete firmware from local repository.
        
        Args:
            firmware: Firmware to delete
            
        Returns:
            True if successful, False otherwise
        """
        key = f"{firmware.hardware_model}_{firmware.platform}_{firmware.version}"
        
        if firmware.file_path and firmware.file_path.exists():
            try:
                firmware.file_path.unlink()
            except Exception:
                return False
        
        if key in self.firmware_cache:
            del self.firmware_cache[key]
        
        return True
    
    def get_firmware_info(self, firmware: FirmwareVersion) -> Dict[str, Any]:
        """
        Get detailed firmware information.
        
        Args:
            firmware: Firmware version
            
        Returns:
            Dictionary with firmware details
        """
        info = firmware.to_dict()
        info["is_valid"] = self.verify_firmware(firmware)
        return info
    
    def export_firmware_list(self, output_file: Path) -> None:
        """
        Export firmware list for air-gapped transfer.
        
        Args:
            output_file: Output JSON file path
        """
        import json
        
        firmware_list = [f.to_dict() for f in self.firmware_cache.values()]
        
        with open(output_file, "w") as f:
            json.dump(firmware_list, f, indent=2)
