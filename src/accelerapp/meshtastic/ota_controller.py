"""
OTA (Over-The-Air) firmware update controller for Meshtastic devices.
Supports WiFi-OTA and BLE-OTA update mechanisms.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import time


class OTAMethod(Enum):
    """OTA update methods."""
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    SERIAL = "serial"


@dataclass
class UpdateProgress:
    """Progress information for OTA update."""
    
    device_id: str
    firmware_version: str
    method: OTAMethod
    status: str
    progress_percent: float = 0.0
    bytes_transferred: int = 0
    total_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "device_id": self.device_id,
            "firmware_version": self.firmware_version,
            "method": self.method.value,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "bytes_transferred": self.bytes_transferred,
            "total_bytes": self.total_bytes,
            "elapsed_seconds": elapsed,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
        }


class OTAController:
    """
    Controls OTA firmware updates for Meshtastic devices.
    Supports WiFi, Bluetooth, and Serial update methods.
    """
    
    def __init__(self):
        """Initialize OTA controller."""
        self.active_updates: Dict[str, UpdateProgress] = {}
        self.update_history: list[UpdateProgress] = []
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def start_update(
        self,
        device_id: str,
        firmware_path: Path,
        method: OTAMethod,
        device_info: Optional[Dict[str, Any]] = None
    ) -> UpdateProgress:
        """
        Start OTA firmware update.
        
        Args:
            device_id: Device identifier
            firmware_path: Path to firmware file
            method: Update method (WiFi, Bluetooth, Serial)
            device_info: Optional device connection info
            
        Returns:
            UpdateProgress object
        """
        if device_id in self.active_updates:
            raise ValueError(f"Update already in progress for device {device_id}")
        
        if not firmware_path.exists():
            raise FileNotFoundError(f"Firmware file not found: {firmware_path}")
        
        # Extract version from filename
        firmware_version = firmware_path.stem.split("-")[1] if "-" in firmware_path.stem else "unknown"
        
        progress = UpdateProgress(
            device_id=device_id,
            firmware_version=firmware_version,
            method=method,
            status="starting",
            total_bytes=firmware_path.stat().st_size
        )
        
        self.active_updates[device_id] = progress
        
        # Start update based on method
        try:
            if method == OTAMethod.WIFI:
                self._update_via_wifi(device_id, firmware_path, device_info)
            elif method == OTAMethod.BLUETOOTH:
                self._update_via_bluetooth(device_id, firmware_path, device_info)
            elif method == OTAMethod.SERIAL:
                self._update_via_serial(device_id, firmware_path, device_info)
        except Exception as e:
            progress.status = "failed"
            progress.error_message = str(e)
            progress.end_time = datetime.now()
            self._finish_update(device_id)
        
        return progress
    
    def _update_via_wifi(
        self,
        device_id: str,
        firmware_path: Path,
        device_info: Optional[Dict[str, Any]]
    ) -> None:
        """
        Perform WiFi OTA update.
        
        Args:
            device_id: Device identifier
            firmware_path: Path to firmware file
            device_info: Device connection info
        """
        progress = self.active_updates[device_id]
        progress.status = "connecting"
        
        # Simulate WiFi OTA update process
        # In real implementation, would use HTTP POST to device
        
        ip_address = device_info.get("ip_address") if device_info else "192.168.1.100"
        
        # Simulate update steps
        steps = [
            ("connecting", 10),
            ("uploading", 60),
            ("flashing", 20),
            ("verifying", 10),
        ]
        
        total_bytes = progress.total_bytes
        
        for step_name, step_percent in steps:
            progress.status = step_name
            
            # Simulate progress within step
            for i in range(10):
                time.sleep(0.1)  # Simulate work
                progress.progress_percent = progress.progress_percent + (step_percent / 10)
                progress.bytes_transferred = int(total_bytes * progress.progress_percent / 100)
                self._notify_progress(device_id, progress)
        
        progress.status = "complete"
        progress.progress_percent = 100.0
        progress.end_time = datetime.now()
        self._finish_update(device_id)
    
    def _update_via_bluetooth(
        self,
        device_id: str,
        firmware_path: Path,
        device_info: Optional[Dict[str, Any]]
    ) -> None:
        """
        Perform Bluetooth OTA update.
        
        Args:
            device_id: Device identifier
            firmware_path: Path to firmware file
            device_info: Device connection info
        """
        progress = self.active_updates[device_id]
        progress.status = "connecting"
        
        # Simulate BLE OTA update process
        # In real implementation, would use BLE library
        
        mac_address = device_info.get("mac_address") if device_info else "00:00:00:00:00:00"
        
        # Simulate update
        progress.status = "uploading"
        total_bytes = progress.total_bytes
        
        for i in range(100):
            time.sleep(0.05)
            progress.progress_percent = i + 1
            progress.bytes_transferred = int(total_bytes * progress.progress_percent / 100)
            self._notify_progress(device_id, progress)
        
        progress.status = "complete"
        progress.end_time = datetime.now()
        self._finish_update(device_id)
    
    def _update_via_serial(
        self,
        device_id: str,
        firmware_path: Path,
        device_info: Optional[Dict[str, Any]]
    ) -> None:
        """
        Perform Serial OTA update.
        
        Args:
            device_id: Device identifier
            firmware_path: Path to firmware file
            device_info: Device connection info
        """
        progress = self.active_updates[device_id]
        progress.status = "flashing"
        
        # Simulate serial flashing
        # In real implementation, would use esptool or nrfutil
        
        port = device_info.get("port") if device_info else "/dev/ttyUSB0"
        
        # Simulate update
        total_bytes = progress.total_bytes
        
        for i in range(100):
            time.sleep(0.02)
            progress.progress_percent = i + 1
            progress.bytes_transferred = int(total_bytes * progress.progress_percent / 100)
            self._notify_progress(device_id, progress)
        
        progress.status = "complete"
        progress.end_time = datetime.now()
        self._finish_update(device_id)
    
    def _finish_update(self, device_id: str) -> None:
        """
        Finish update and move to history.
        
        Args:
            device_id: Device identifier
        """
        if device_id in self.active_updates:
            progress = self.active_updates[device_id]
            self.update_history.append(progress)
            del self.active_updates[device_id]
    
    def _notify_progress(self, device_id: str, progress: UpdateProgress) -> None:
        """
        Notify progress callback if registered.
        
        Args:
            device_id: Device identifier
            progress: Progress information
        """
        if device_id in self.progress_callbacks:
            callback = self.progress_callbacks[device_id]
            callback(progress)
    
    def register_progress_callback(
        self,
        device_id: str,
        callback: Callable[[UpdateProgress], None]
    ) -> None:
        """
        Register callback for progress updates.
        
        Args:
            device_id: Device identifier
            callback: Callback function
        """
        self.progress_callbacks[device_id] = callback
    
    def get_progress(self, device_id: str) -> Optional[UpdateProgress]:
        """
        Get current progress for device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            UpdateProgress or None if no active update
        """
        return self.active_updates.get(device_id)
    
    def cancel_update(self, device_id: str) -> bool:
        """
        Cancel ongoing update.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if cancelled, False if no active update
        """
        if device_id in self.active_updates:
            progress = self.active_updates[device_id]
            progress.status = "cancelled"
            progress.end_time = datetime.now()
            self._finish_update(device_id)
            return True
        return False
    
    def get_update_history(
        self,
        device_id: Optional[str] = None,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get update history.
        
        Args:
            device_id: Optional device filter
            limit: Maximum number of records
            
        Returns:
            List of update records
        """
        history = self.update_history
        
        if device_id:
            history = [h for h in history if h.device_id == device_id]
        
        # Return most recent first
        history = sorted(history, key=lambda h: h.start_time, reverse=True)
        
        return [h.to_dict() for h in history[:limit]]
    
    def get_active_updates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active updates.
        
        Returns:
            Dictionary of device_id to progress info
        """
        return {
            device_id: progress.to_dict()
            for device_id, progress in self.active_updates.items()
        }
