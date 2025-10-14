"""
Enclosure generator for ESP32 and Meshtastic devices.
Integrates WildCAM_ESP32 3D design framework and manufacturing expertise.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from .board_support import BoardSupportMatrix, ESP32BoardType, BoardSpecification


class DeploymentEnvironment(Enum):
    """Deployment environment types."""
    INDOOR_LAB = "indoor_lab"
    INDOOR_COMMERCIAL = "indoor_commercial"
    OUTDOOR_BUDGET = "outdoor_budget"
    OUTDOOR_PROFESSIONAL = "outdoor_professional"
    DESERT_HARSH = "desert_harsh"
    TROPICAL = "tropical"
    ARCTIC = "arctic"
    URBAN_OUTDOOR = "urban_outdoor"


class EnclosureMaterial(Enum):
    """3D printing materials."""
    PLA = "pla"  # Budget, indoor only
    PETG = "petg"  # Good outdoor resistance
    ASA = "asa"  # Excellent UV resistance
    ABS = "abs"  # Good strength
    TPU = "tpu"  # Flexible, weatherproof
    NYLON = "nylon"  # Professional grade


@dataclass
class EnclosureDesign:
    """
    Represents a generated enclosure design.
    Based on WildCAM_ESP32 design framework.
    """
    board_type: ESP32BoardType
    deployment_env: DeploymentEnvironment
    material: EnclosureMaterial
    dimensions: Dict[str, float]  # width, height, depth in mm
    wall_thickness: float  # mm
    ip_rating: str
    features: List[str] = field(default_factory=list)
    mounting_system: str = "screw_mount"
    ventilation: bool = False
    cable_ports: List[Dict[str, Any]] = field(default_factory=list)
    cost_estimate: Optional[Dict[str, float]] = None
    print_settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert design to dictionary."""
        return {
            "board_type": self.board_type.value,
            "deployment_env": self.deployment_env.value,
            "material": self.material.value,
            "dimensions": self.dimensions,
            "wall_thickness": self.wall_thickness,
            "ip_rating": self.ip_rating,
            "features": self.features,
            "mounting_system": self.mounting_system,
            "ventilation": self.ventilation,
            "cable_ports": self.cable_ports,
            "cost_estimate": self.cost_estimate,
            "print_settings": self.print_settings,
        }


class EnclosureGenerator:
    """
    Generate enclosure designs for ESP32 and Meshtastic devices.
    Implements WildCAM_ESP32 design principles and manufacturing expertise.
    """
    
    def __init__(self):
        """Initialize enclosure generator."""
        self.board_matrix = BoardSupportMatrix()
        self._material_properties = self._initialize_material_properties()
        self._environment_requirements = self._initialize_environment_requirements()
    
    def _initialize_material_properties(self) -> Dict[EnclosureMaterial, Dict[str, Any]]:
        """Initialize material properties from WildCAM knowledge."""
        return {
            EnclosureMaterial.PLA: {
                "cost_per_kg": 20.0,
                "uv_resistance": "poor",
                "temperature_range": {"min": 0, "max": 50},
                "water_resistance": "poor",
                "outdoor_suitable": False,
                "print_difficulty": "easy",
            },
            EnclosureMaterial.PETG: {
                "cost_per_kg": 25.0,
                "uv_resistance": "moderate",
                "temperature_range": {"min": -20, "max": 60},
                "water_resistance": "good",
                "outdoor_suitable": True,
                "print_difficulty": "moderate",
            },
            EnclosureMaterial.ASA: {
                "cost_per_kg": 35.0,
                "uv_resistance": "excellent",
                "temperature_range": {"min": -30, "max": 80},
                "water_resistance": "excellent",
                "outdoor_suitable": True,
                "print_difficulty": "moderate",
            },
            EnclosureMaterial.ABS: {
                "cost_per_kg": 22.0,
                "uv_resistance": "poor",
                "temperature_range": {"min": -20, "max": 70},
                "water_resistance": "good",
                "outdoor_suitable": False,
                "print_difficulty": "hard",
            },
            EnclosureMaterial.TPU: {
                "cost_per_kg": 30.0,
                "uv_resistance": "moderate",
                "temperature_range": {"min": -30, "max": 60},
                "water_resistance": "excellent",
                "outdoor_suitable": True,
                "print_difficulty": "hard",
            },
            EnclosureMaterial.NYLON: {
                "cost_per_kg": 45.0,
                "uv_resistance": "good",
                "temperature_range": {"min": -40, "max": 85},
                "water_resistance": "excellent",
                "outdoor_suitable": True,
                "print_difficulty": "very_hard",
            },
        }
    
    def _initialize_environment_requirements(self) -> Dict[DeploymentEnvironment, Dict[str, Any]]:
        """Initialize environmental requirements."""
        return {
            DeploymentEnvironment.INDOOR_LAB: {
                "ip_rating": "IP20",
                "wall_thickness": 2.0,
                "recommended_materials": [EnclosureMaterial.PLA, EnclosureMaterial.PETG],
                "ventilation_required": True,
                "uv_protection": False,
            },
            DeploymentEnvironment.INDOOR_COMMERCIAL: {
                "ip_rating": "IP40",
                "wall_thickness": 2.5,
                "recommended_materials": [EnclosureMaterial.PETG, EnclosureMaterial.ABS],
                "ventilation_required": True,
                "uv_protection": False,
            },
            DeploymentEnvironment.OUTDOOR_BUDGET: {
                "ip_rating": "IP54",
                "wall_thickness": 3.0,
                "recommended_materials": [EnclosureMaterial.PETG],
                "ventilation_required": True,
                "uv_protection": True,
            },
            DeploymentEnvironment.OUTDOOR_PROFESSIONAL: {
                "ip_rating": "IP65",
                "wall_thickness": 3.5,
                "recommended_materials": [EnclosureMaterial.ASA, EnclosureMaterial.NYLON],
                "ventilation_required": True,
                "uv_protection": True,
            },
            DeploymentEnvironment.DESERT_HARSH: {
                "ip_rating": "IP65",
                "wall_thickness": 4.0,
                "recommended_materials": [EnclosureMaterial.ASA],
                "ventilation_required": True,
                "uv_protection": True,
                "heat_dissipation": True,
            },
            DeploymentEnvironment.TROPICAL: {
                "ip_rating": "IP67",
                "wall_thickness": 3.5,
                "recommended_materials": [EnclosureMaterial.ASA, EnclosureMaterial.TPU],
                "ventilation_required": True,
                "uv_protection": True,
                "humidity_protection": True,
            },
            DeploymentEnvironment.ARCTIC: {
                "ip_rating": "IP65",
                "wall_thickness": 3.5,
                "recommended_materials": [EnclosureMaterial.NYLON, EnclosureMaterial.PETG],
                "ventilation_required": False,
                "uv_protection": True,
                "cold_resistant": True,
            },
            DeploymentEnvironment.URBAN_OUTDOOR: {
                "ip_rating": "IP54",
                "wall_thickness": 3.0,
                "recommended_materials": [EnclosureMaterial.PETG, EnclosureMaterial.ASA],
                "ventilation_required": True,
                "uv_protection": True,
            },
        }
    
    def generate_for_board(
        self,
        board_type: str,
        deployment_env: str = "outdoor_professional",
        budget_constraint: Optional[str] = None,
        custom_features: Optional[List[str]] = None,
    ) -> EnclosureDesign:
        """
        Generate enclosure design for a specific board.
        
        Args:
            board_type: Board type (e.g., "ESP32_MESHTASTIC")
            deployment_env: Deployment environment
            budget_constraint: Optional budget constraint (e.g., "under_25_usd")
            custom_features: Optional custom features to include
            
        Returns:
            Generated enclosure design
        """
        # Parse inputs
        board_enum = ESP32BoardType(board_type.lower())
        env_enum = DeploymentEnvironment(deployment_env.lower())
        
        # Get board specification
        board_spec = self.board_matrix.get_board_spec(board_enum)
        if not board_spec:
            raise ValueError(f"Unsupported board type: {board_type}")
        
        # Get environment requirements
        env_req = self._environment_requirements[env_enum]
        
        # Select material based on environment and budget
        material = self._select_material(env_enum, budget_constraint)
        
        # Calculate enclosure dimensions (add clearance around board)
        clearance = 5.0  # mm clearance on each side
        enclosure_dims = {
            "width": board_spec.dimensions["width"] + (2 * clearance),
            "height": board_spec.dimensions["height"] + (2 * clearance),
            "depth": board_spec.dimensions["depth"] + (2 * clearance) + 3.0,  # Extra for mounting
        }
        
        # Determine features
        features = custom_features or []
        if board_spec.camera_position:
            features.append("camera_window")
        if board_spec.antenna_position:
            features.append("antenna_port")
        if "microsd" in board_spec.features:
            features.append("sd_card_access")
        
        # Generate cable ports
        cable_ports = self._generate_cable_ports(board_spec, env_req)
        
        # Generate print settings
        print_settings = self._generate_print_settings(material, env_enum)
        
        # Estimate cost
        cost_estimate = self._estimate_cost(enclosure_dims, material, env_enum)
        
        return EnclosureDesign(
            board_type=board_enum,
            deployment_env=env_enum,
            material=material,
            dimensions=enclosure_dims,
            wall_thickness=env_req["wall_thickness"],
            ip_rating=env_req["ip_rating"],
            features=features,
            mounting_system="screw_mount",
            ventilation=env_req.get("ventilation_required", False),
            cable_ports=cable_ports,
            cost_estimate=cost_estimate,
            print_settings=print_settings,
        )
    
    def _select_material(
        self,
        environment: DeploymentEnvironment,
        budget_constraint: Optional[str] = None,
    ) -> EnclosureMaterial:
        """Select appropriate material based on environment and budget."""
        env_req = self._environment_requirements[environment]
        recommended = env_req["recommended_materials"]
        
        if budget_constraint == "under_25_usd" and len(recommended) > 0:
            # Choose cheapest recommended material
            return min(
                recommended,
                key=lambda m: self._material_properties[m]["cost_per_kg"]
            )
        
        # Default to first recommended material
        return recommended[0] if recommended else EnclosureMaterial.PETG
    
    def _generate_cable_ports(
        self,
        board_spec: BoardSpecification,
        env_req: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate cable port specifications."""
        ports = [
            {
                "type": "usb",
                "diameter": 8.0,
                "position": {"side": "bottom", "offset": 5.0},
                "sealed": env_req["ip_rating"] >= "IP54",
            }
        ]
        
        if "camera" in board_spec.features:
            ports.append({
                "type": "camera_cable",
                "diameter": 6.0,
                "position": {"side": "top", "offset": 10.0},
                "sealed": True,
            })
        
        return ports
    
    def _generate_print_settings(
        self,
        material: EnclosureMaterial,
        environment: DeploymentEnvironment,
    ) -> Dict[str, Any]:
        """Generate 3D print settings."""
        # Base settings from WildCAM expertise
        base_settings = {
            EnclosureMaterial.PLA: {
                "nozzle_temp": 210,
                "bed_temp": 60,
                "layer_height": 0.2,
                "infill": 20,
            },
            EnclosureMaterial.PETG: {
                "nozzle_temp": 235,
                "bed_temp": 80,
                "layer_height": 0.2,
                "infill": 25,
            },
            EnclosureMaterial.ASA: {
                "nozzle_temp": 245,
                "bed_temp": 90,
                "layer_height": 0.2,
                "infill": 30,
            },
            EnclosureMaterial.ABS: {
                "nozzle_temp": 240,
                "bed_temp": 100,
                "layer_height": 0.2,
                "infill": 25,
            },
            EnclosureMaterial.TPU: {
                "nozzle_temp": 220,
                "bed_temp": 60,
                "layer_height": 0.2,
                "infill": 15,
            },
            EnclosureMaterial.NYLON: {
                "nozzle_temp": 260,
                "bed_temp": 85,
                "layer_height": 0.2,
                "infill": 35,
            },
        }
        
        settings = base_settings[material].copy()
        
        # Adjust for harsh environments
        if environment in [DeploymentEnvironment.DESERT_HARSH, DeploymentEnvironment.TROPICAL]:
            settings["infill"] += 10  # Increase strength
            settings["wall_count"] = 4
        else:
            settings["wall_count"] = 3
        
        return settings
    
    def _estimate_cost(
        self,
        dimensions: Dict[str, float],
        material: EnclosureMaterial,
        environment: DeploymentEnvironment,
    ) -> Dict[str, float]:
        """Estimate manufacturing cost."""
        # Calculate volume in cm³
        volume_mm3 = dimensions["width"] * dimensions["height"] * dimensions["depth"]
        volume_cm3 = volume_mm3 / 1000
        
        # Estimate material weight (assume 30% infill average)
        density = 1.2  # g/cm³ for most 3D printing materials
        weight_g = volume_cm3 * density * 0.3
        weight_kg = weight_g / 1000
        
        # Material cost
        material_props = self._material_properties[material]
        material_cost = weight_kg * material_props["cost_per_kg"]
        
        # Add manufacturing overhead
        print_time_hours = volume_cm3 / 10  # Rough estimate
        electricity_cost = print_time_hours * 0.15  # $0.15/hour
        
        # Labor cost for assembly (check environment type by value)
        professional_envs = [
            DeploymentEnvironment.OUTDOOR_PROFESSIONAL,
            DeploymentEnvironment.DESERT_HARSH,
            DeploymentEnvironment.TROPICAL,
            DeploymentEnvironment.ARCTIC,
        ]
        labor_cost = 5.0 if environment in professional_envs else 2.0
        
        total = material_cost + electricity_cost + labor_cost
        
        return {
            "material": round(material_cost, 2),
            "electricity": round(electricity_cost, 2),
            "labor": round(labor_cost, 2),
            "total": round(total, 2),
            "currency": "USD",
        }
    
    def optimize_for_cost(
        self,
        design: EnclosureDesign,
        target_cost: float,
    ) -> EnclosureDesign:
        """
        Optimize design to meet cost target.
        
        Args:
            design: Original design
            target_cost: Target cost in USD
            
        Returns:
            Optimized design
        """
        current_cost = design.cost_estimate["total"] if design.cost_estimate else 0
        
        if current_cost <= target_cost:
            return design
        
        # Try cheaper material
        cheaper_materials = sorted(
            self._material_properties.keys(),
            key=lambda m: self._material_properties[m]["cost_per_kg"]
        )
        
        for material in cheaper_materials:
            # Check if material is suitable for environment
            env_req = self._environment_requirements[design.deployment_env]
            if material in env_req["recommended_materials"]:
                # Regenerate with cheaper material
                return self.generate_for_board(
                    design.board_type.value,
                    design.deployment_env.value,
                    budget_constraint="under_25_usd",
                    custom_features=design.features,
                )
        
        return design
