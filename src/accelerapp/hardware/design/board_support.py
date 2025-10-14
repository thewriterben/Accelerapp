"""
Board support matrix for ESP32 and Meshtastic devices.
Defines compatible boards and their specifications.
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass, field


class ESP32BoardType(Enum):
    """Supported ESP32 board types."""
    ESP32_GENERIC = "esp32_generic"
    ESP32_CAM = "esp32_cam"
    ESP32_S3_CAM = "esp32_s3_cam"
    AI_THINKER = "ai_thinker"
    ESP32_MESHTASTIC = "esp32_meshtastic"
    ESP32_LORA = "esp32_lora"


@dataclass
class BoardSpecification:
    """Hardware specification for a board."""
    board_type: ESP32BoardType
    display_name: str
    dimensions: Dict[str, float]  # width, height, depth in mm
    mounting_holes: List[Dict[str, float]]  # x, y positions in mm
    power_requirements: Dict[str, Any]  # voltage, current
    environmental_rating: str = "IP54"  # Default rating
    features: List[str] = field(default_factory=list)
    camera_position: Dict[str, float] = field(default_factory=dict)
    antenna_position: Dict[str, float] = field(default_factory=dict)


class BoardSupportMatrix:
    """
    Matrix of supported boards with their specifications.
    Based on WildCAM_ESP32 compatibility framework.
    """
    
    def __init__(self):
        """Initialize board support matrix."""
        self._boards = self._initialize_boards()
    
    def _initialize_boards(self) -> Dict[ESP32BoardType, BoardSpecification]:
        """Initialize supported board specifications."""
        return {
            ESP32BoardType.ESP32_GENERIC: BoardSpecification(
                board_type=ESP32BoardType.ESP32_GENERIC,
                display_name="ESP32 Generic",
                dimensions={"width": 51.0, "height": 28.0, "depth": 12.0},
                mounting_holes=[
                    {"x": 2.5, "y": 2.5},
                    {"x": 48.5, "y": 2.5},
                    {"x": 2.5, "y": 25.5},
                    {"x": 48.5, "y": 25.5},
                ],
                power_requirements={"voltage": "3.3V", "current": "500mA"},
                features=["wifi", "bluetooth", "gpio"],
            ),
            ESP32BoardType.ESP32_CAM: BoardSpecification(
                board_type=ESP32BoardType.ESP32_CAM,
                display_name="ESP32-CAM (AI-Thinker)",
                dimensions={"width": 27.0, "height": 40.5, "depth": 15.0},
                mounting_holes=[
                    {"x": 2.0, "y": 2.0},
                    {"x": 25.0, "y": 2.0},
                    {"x": 2.0, "y": 38.5},
                    {"x": 25.0, "y": 38.5},
                ],
                power_requirements={"voltage": "5V", "current": "800mA"},
                camera_position={"x": 13.5, "y": 35.0, "z": 10.0},
                features=["wifi", "camera", "microsd", "gpio"],
            ),
            ESP32BoardType.ESP32_S3_CAM: BoardSpecification(
                board_type=ESP32BoardType.ESP32_S3_CAM,
                display_name="ESP32-S3-CAM",
                dimensions={"width": 25.4, "height": 40.0, "depth": 14.0},
                mounting_holes=[
                    {"x": 2.0, "y": 2.0},
                    {"x": 23.4, "y": 2.0},
                    {"x": 2.0, "y": 38.0},
                    {"x": 23.4, "y": 38.0},
                ],
                power_requirements={"voltage": "5V", "current": "1000mA"},
                camera_position={"x": 12.7, "y": 35.0, "z": 9.0},
                features=["wifi", "camera", "microsd", "usb", "gpio"],
            ),
            ESP32BoardType.AI_THINKER: BoardSpecification(
                board_type=ESP32BoardType.AI_THINKER,
                display_name="AI-Thinker ESP32-CAM",
                dimensions={"width": 27.0, "height": 40.5, "depth": 15.0},
                mounting_holes=[
                    {"x": 2.0, "y": 2.0},
                    {"x": 25.0, "y": 2.0},
                    {"x": 2.0, "y": 38.5},
                    {"x": 25.0, "y": 38.5},
                ],
                power_requirements={"voltage": "5V", "current": "800mA"},
                camera_position={"x": 13.5, "y": 35.0, "z": 10.0},
                features=["wifi", "camera", "microsd", "gpio", "flash_led"],
            ),
            ESP32BoardType.ESP32_MESHTASTIC: BoardSpecification(
                board_type=ESP32BoardType.ESP32_MESHTASTIC,
                display_name="ESP32 Meshtastic Node",
                dimensions={"width": 65.0, "height": 30.0, "depth": 15.0},
                mounting_holes=[
                    {"x": 3.0, "y": 3.0},
                    {"x": 62.0, "y": 3.0},
                    {"x": 3.0, "y": 27.0},
                    {"x": 62.0, "y": 27.0},
                ],
                power_requirements={"voltage": "3.7V", "current": "200mA"},
                antenna_position={"x": 60.0, "y": 15.0, "z": 12.0},
                features=["wifi", "lora", "bluetooth", "gps", "oled"],
            ),
            ESP32BoardType.ESP32_LORA: BoardSpecification(
                board_type=ESP32BoardType.ESP32_LORA,
                display_name="ESP32 with LoRa",
                dimensions={"width": 52.0, "height": 28.0, "depth": 12.0},
                mounting_holes=[
                    {"x": 2.5, "y": 2.5},
                    {"x": 49.5, "y": 2.5},
                    {"x": 2.5, "y": 25.5},
                    {"x": 49.5, "y": 25.5},
                ],
                power_requirements={"voltage": "3.3V", "current": "120mA"},
                antenna_position={"x": 50.0, "y": 14.0, "z": 10.0},
                features=["wifi", "lora", "bluetooth", "gpio"],
            ),
        }
    
    def get_board_spec(self, board_type: ESP32BoardType) -> BoardSpecification:
        """
        Get board specification.
        
        Args:
            board_type: Board type to get
            
        Returns:
            Board specification
        """
        return self._boards.get(board_type)
    
    def list_boards(self) -> List[ESP32BoardType]:
        """Get list of supported boards."""
        return list(self._boards.keys())
    
    def get_boards_by_feature(self, feature: str) -> List[ESP32BoardType]:
        """
        Get boards that support a specific feature.
        
        Args:
            feature: Feature to filter by
            
        Returns:
            List of board types with the feature
        """
        return [
            board_type
            for board_type, spec in self._boards.items()
            if feature in spec.features
        ]
    
    def get_meshtastic_compatible_boards(self) -> List[ESP32BoardType]:
        """Get boards compatible with Meshtastic."""
        return [
            board_type
            for board_type, spec in self._boards.items()
            if "lora" in spec.features or board_type == ESP32BoardType.ESP32_MESHTASTIC
        ]
