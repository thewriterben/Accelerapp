"""
Storage management for ESP32-CAM.
Handles local SD card storage, file management, and cloud uploads.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class StorageType(Enum):
    """Storage location types."""
    SD_CARD = "sd_card"
    SPIFFS = "spiffs"
    RAM = "ram"


class FileFormat(Enum):
    """Supported file formats."""
    JPEG = "jpg"
    PNG = "png"
    AVI = "avi"
    MP4 = "mp4"


@dataclass
class StorageConfig:
    """Storage configuration."""
    storage_type: StorageType = StorageType.SD_CARD
    base_path: str = "/sdcard"
    max_file_size_mb: int = 10
    auto_cleanup: bool = True
    cleanup_threshold_percent: int = 80
    file_format: FileFormat = FileFormat.JPEG


class StorageManager:
    """
    Storage management for ESP32-CAM.
    Manages file storage, cleanup, and organization.
    """
    
    def __init__(self, camera, config: Optional[StorageConfig] = None):
        """
        Initialize storage manager.
        
        Args:
            camera: ESP32Camera instance
            config: Storage configuration
        """
        self.camera = camera
        self.config = config or StorageConfig()
        self._files: List[Dict[str, Any]] = []
        self._total_size = 0
        self._capacity = 1024 * 1024 * 1024  # 1GB simulated
    
    def initialize(self) -> bool:
        """
        Initialize storage system.
        
        Returns:
            True if initialized successfully
        """
        # In real implementation, would mount SD card and check filesystem
        return True
    
    def save_image(self, image_data: Dict[str, Any], filename: Optional[str] = None) -> Optional[str]:
        """
        Save image to storage.
        
        Args:
            image_data: Image data dictionary
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to saved file, or None if failed
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"IMG_{timestamp}.{self.config.file_format.value}"
        
        filepath = f"{self.config.base_path}/{filename}"
        
        # Simulate file storage
        file_info = {
            "filename": filename,
            "filepath": filepath,
            "size": image_data.get("size_bytes", 0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "format": self.config.file_format.value,
        }
        
        self._files.append(file_info)
        self._total_size += file_info["size"]
        
        # Check if cleanup is needed
        if self.config.auto_cleanup:
            self._check_cleanup()
        
        return filepath
    
    def save_video(self, video_data: Dict[str, Any], filename: Optional[str] = None) -> Optional[str]:
        """
        Save video recording to storage.
        
        Args:
            video_data: Video data dictionary
            filename: Optional filename
            
        Returns:
            Path to saved file, or None if failed
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"VID_{timestamp}.avi"
        
        filepath = f"{self.config.base_path}/{filename}"
        
        file_info = {
            "filename": filename,
            "filepath": filepath,
            "size": video_data.get("size_bytes", 0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "duration_sec": video_data.get("duration_sec", 0),
        }
        
        self._files.append(file_info)
        self._total_size += file_info["size"]
        
        return filepath
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            filename: Name of file to delete
            
        Returns:
            True if deleted successfully
        """
        for i, file_info in enumerate(self._files):
            if file_info["filename"] == filename:
                self._total_size -= file_info["size"]
                self._files.pop(i)
                return True
        return False
    
    def list_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List stored files.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        return self._files[-limit:]
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information and statistics.
        
        Returns:
            Storage info dictionary
        """
        used_percent = (self._total_size / self._capacity) * 100 if self._capacity > 0 else 0
        
        return {
            "storage_type": self.config.storage_type.value,
            "base_path": self.config.base_path,
            "total_capacity_mb": self._capacity / (1024 * 1024),
            "used_space_mb": self._total_size / (1024 * 1024),
            "free_space_mb": (self._capacity - self._total_size) / (1024 * 1024),
            "used_percent": used_percent,
            "file_count": len(self._files),
            "auto_cleanup_enabled": self.config.auto_cleanup,
        }
    
    def _check_cleanup(self) -> None:
        """Check if cleanup is needed and perform if necessary."""
        used_percent = (self._total_size / self._capacity) * 100
        
        if used_percent >= self.config.cleanup_threshold_percent:
            self._cleanup_old_files()
    
    def _cleanup_old_files(self, count: int = 10) -> int:
        """
        Delete oldest files to free space.
        
        Args:
            count: Number of files to delete
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        while deleted < count and self._files:
            file_info = self._files.pop(0)  # Remove oldest
            self._total_size -= file_info["size"]
            deleted += 1
        
        return deleted
    
    def format_storage(self) -> bool:
        """
        Format storage (delete all files).
        
        Returns:
            True if successful
        """
        self._files.clear()
        self._total_size = 0
        return True
    
    def upload_to_cloud(self, filename: str, destination: str) -> bool:
        """
        Upload file to cloud storage.
        
        Args:
            filename: Name of file to upload
            destination: Cloud destination URL or path
            
        Returns:
            True if upload successful
        """
        # Placeholder for cloud upload functionality
        # In real implementation, would upload via FTP, SFTP, or cloud API
        for file_info in self._files:
            if file_info["filename"] == filename:
                # Simulate successful upload
                return True
        return False
