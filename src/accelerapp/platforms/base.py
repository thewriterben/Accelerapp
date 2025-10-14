"""
Base platform abstraction for Accelerapp.
Defines the interface that all platform implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class BasePlatform(ABC):
    """
    Abstract base class for hardware platforms.
    All platform implementations must inherit from this class.
    """

    def __init__(self):
        """Initialize platform."""
        self.name = "base"
        self.supported_languages = []
        self.capabilities = []
        self.peripherals = []

    @abstractmethod
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform information and capabilities.

        Returns:
            Dictionary containing platform details
        """
        pass

    @abstractmethod
    def generate_code(self, spec: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Generate platform-specific code.

        Args:
            spec: Hardware specification dictionary
            output_dir: Directory to write generated code

        Returns:
            Dictionary with generation results
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate platform-specific configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        pass

    def get_supported_peripherals(self) -> List[str]:
        """
        Get list of supported peripheral types.

        Returns:
            List of peripheral type names
        """
        return self.peripherals.copy()

    def supports_capability(self, capability: str) -> bool:
        """
        Check if platform supports a specific capability.

        Args:
            capability: Capability name to check

        Returns:
            True if supported, False otherwise
        """
        return capability in self.capabilities

    def get_build_config(self) -> Dict[str, Any]:
        """
        Get platform-specific build configuration.

        Returns:
            Build configuration dictionary
        """
        return {
            "platform": self.name,
            "build_system": "generic",
            "toolchain": "gcc",
        }

    def get_pin_mapping(self, logical_pin: str) -> Optional[str]:
        """
        Map logical pin name to physical pin.

        Args:
            logical_pin: Logical pin identifier

        Returns:
            Physical pin identifier or None if not mapped
        """
        return logical_pin
