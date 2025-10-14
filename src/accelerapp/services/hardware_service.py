"""
Hardware abstraction service for Accelerapp.
Provides unified interface for hardware operations.
"""

from typing import Any, Dict, List, Optional

from ..core.interfaces import BaseService
from ..monitoring import get_logger


class HardwareService(BaseService):
    """Service for hardware abstraction and management."""

    def __init__(self):
        """Initialize hardware service."""
        super().__init__("HardwareService")
        self.logger = get_logger(__name__)
        self._devices: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize the hardware service."""
        await super().initialize()
        self.logger.info("Hardware service initialized")

    async def shutdown(self) -> None:
        """Shutdown the hardware service."""
        await super().shutdown()
        self.logger.info("Hardware service shutdown")

    def register_device(self, device_id: str, device_info: Dict[str, Any]) -> None:
        """
        Register a hardware device.

        Args:
            device_id: Device identifier
            device_info: Device information
        """
        self._devices[device_id] = device_info
        self.logger.info(f"Registered device: {device_id}")

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information.

        Args:
            device_id: Device identifier

        Returns:
            Device information or None
        """
        return self._devices.get(device_id)

    def list_devices(self) -> List[str]:
        """
        List all registered devices.

        Returns:
            List of device IDs
        """
        return list(self._devices.keys())

    def remove_device(self, device_id: str) -> bool:
        """
        Remove a registered device.

        Args:
            device_id: Device identifier

        Returns:
            True if device was removed
        """
        if device_id in self._devices:
            del self._devices[device_id]
            self.logger.info(f"Removed device: {device_id}")
            return True
        return False

    def get_health(self) -> Dict[str, Any]:
        """Get service health status."""
        health = super().get_health()
        health.update({
            "registered_devices": len(self._devices),
            "devices": list(self._devices.keys()),
        })
        return health
