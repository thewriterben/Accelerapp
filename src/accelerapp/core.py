"""
Core orchestration module for Accelerapp.
Coordinates firmware, software, and UI generation.
"""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class AccelerappCore:
    """
    Main orchestrator for the Accelerapp platform.
    Manages hardware specifications and coordinates generation agents.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Accelerapp core.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = {}
        self.hardware_spec = {}
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.hardware_spec = self.config.get('hardware', {})

    def generate_firmware(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate firmware based on hardware specification.
        
        Args:
            output_dir: Directory to write generated firmware
            
        Returns:
            Dictionary containing generation results
        """
        from .firmware.generator import FirmwareGenerator
        
        generator = FirmwareGenerator(self.config)
        return generator.generate(output_dir)

    def generate_software(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate software/drivers based on hardware specification.
        
        Args:
            output_dir: Directory to write generated software
            
        Returns:
            Dictionary containing generation results
        """
        from .software.generator import SoftwareGenerator
        
        generator = SoftwareGenerator(self.config)
        return generator.generate(output_dir)

    def generate_ui(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate user interface based on hardware specification.
        
        Args:
            output_dir: Directory to write generated UI
            
        Returns:
            Dictionary containing generation results
        """
        from .ui.generator import UIGenerator
        
        generator = UIGenerator(self.config)
        return generator.generate(output_dir)

    def generate_all(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate complete stack: firmware, software, and UI.
        
        Args:
            output_dir: Base directory for all generated code
            
        Returns:
            Dictionary containing all generation results
        """
        results = {
            'firmware': self.generate_firmware(output_dir / 'firmware'),
            'software': self.generate_software(output_dir / 'software'),
            'ui': self.generate_ui(output_dir / 'ui')
        }
        return results
