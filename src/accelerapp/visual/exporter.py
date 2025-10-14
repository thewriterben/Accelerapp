"""
Export visual specifications to various formats.
"""

from typing import Dict, Any
import json
import yaml
from pathlib import Path
from .specification import VisualSpecification


class SpecificationExporter:
    """
    Exports visual specifications to different formats.
    """

    def __init__(self, specification: VisualSpecification):
        """
        Initialize exporter.

        Args:
            specification: Visual specification to export
        """
        self.specification = specification

    def to_json(self, indent: int = 2) -> str:
        """
        Export to JSON format.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.specification.to_dict(), indent=indent)

    def to_yaml(self) -> str:
        """
        Export to YAML format.

        Returns:
            YAML string
        """
        return yaml.dump(self.specification.to_dict(), default_flow_style=False, sort_keys=False)

    def to_accelerapp_config(self) -> Dict[str, Any]:
        """
        Convert to Accelerapp hardware configuration format.

        Returns:
            Configuration dictionary
        """
        config = {
            "device_name": self.specification.name,
            "description": self.specification.description,
            "peripherals": [],
        }

        # Convert components to peripherals
        for component in self.specification.components.values():
            peripheral = {"type": component.type, "name": component.name, **component.properties}
            config["peripherals"].append(peripheral)

        # Add platform info if microcontroller is present
        for component in self.specification.components.values():
            if component.type == "microcontroller":
                config["platform"] = component.properties.get("platform", "arduino")
                break

        return config

    def save_json(self, filepath: Path):
        """
        Save specification as JSON file.

        Args:
            filepath: Output file path
        """
        filepath.write_text(self.to_json())

    def save_yaml(self, filepath: Path):
        """
        Save specification as YAML file.

        Args:
            filepath: Output file path
        """
        filepath.write_text(self.to_yaml())

    def save_accelerapp_config(self, filepath: Path):
        """
        Save as Accelerapp configuration YAML.

        Args:
            filepath: Output file path
        """
        config = self.to_accelerapp_config()
        with open(filepath, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def from_json(json_str: str) -> VisualSpecification:
        """
        Import specification from JSON.

        Args:
            json_str: JSON string

        Returns:
            VisualSpecification instance
        """
        data = json.loads(json_str)
        return VisualSpecification.from_dict(data)

    @staticmethod
    def from_yaml(yaml_str: str) -> VisualSpecification:
        """
        Import specification from YAML.

        Args:
            yaml_str: YAML string

        Returns:
            VisualSpecification instance
        """
        data = yaml.safe_load(yaml_str)
        return VisualSpecification.from_dict(data)

    @staticmethod
    def load_json(filepath: Path) -> VisualSpecification:
        """
        Load specification from JSON file.

        Args:
            filepath: Input file path

        Returns:
            VisualSpecification instance
        """
        return SpecificationExporter.from_json(filepath.read_text())

    @staticmethod
    def load_yaml(filepath: Path) -> VisualSpecification:
        """
        Load specification from YAML file.

        Args:
            filepath: Input file path

        Returns:
            VisualSpecification instance
        """
        return SpecificationExporter.from_yaml(filepath.read_text())
