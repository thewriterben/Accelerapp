"""
Environmental validation for hardware designs.
Ensures designs meet environmental hardening requirements.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class EnvironmentType(Enum):
    """Environment types for validation."""
    INDOOR_CONTROLLED = "indoor_controlled"
    INDOOR_UNCONTROLLED = "indoor_uncontrolled"
    OUTDOOR_MILD = "outdoor_mild"
    OUTDOOR_MODERATE = "outdoor_moderate"
    DESERT_HARSH = "desert_harsh"
    TROPICAL = "tropical"
    ARCTIC = "arctic"
    MARINE = "marine"


@dataclass
class ValidationResult:
    """Result of environmental validation."""
    passed: bool
    environment: EnvironmentType
    duration_months: int
    ip_rating_adequate: bool
    material_suitable: bool
    temperature_range_ok: bool
    uv_protection_ok: bool
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "environment": self.environment.value,
            "duration_months": self.duration_months,
            "ip_rating_adequate": self.ip_rating_adequate,
            "material_suitable": self.material_suitable,
            "temperature_range_ok": self.temperature_range_ok,
            "uv_protection_ok": self.uv_protection_ok,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
        }


class EnvironmentalValidator:
    """
    Validate hardware designs for environmental conditions.
    Based on WildCAM_ESP32 field testing and durability standards.
    """
    
    def __init__(self):
        """Initialize environmental validator."""
        self._environment_specs = self._initialize_environment_specs()
    
    def _initialize_environment_specs(self) -> Dict[EnvironmentType, Dict[str, Any]]:
        """Initialize environment specifications and requirements."""
        return {
            EnvironmentType.INDOOR_CONTROLLED: {
                "temperature_range": {"min": 15, "max": 30},
                "humidity_range": {"min": 30, "max": 60},
                "min_ip_rating": "IP20",
                "uv_exposure": False,
                "condensation_risk": "low",
                "required_features": [],
            },
            EnvironmentType.INDOOR_UNCONTROLLED: {
                "temperature_range": {"min": 5, "max": 40},
                "humidity_range": {"min": 20, "max": 80},
                "min_ip_rating": "IP40",
                "uv_exposure": False,
                "condensation_risk": "moderate",
                "required_features": ["ventilation"],
            },
            EnvironmentType.OUTDOOR_MILD: {
                "temperature_range": {"min": -5, "max": 45},
                "humidity_range": {"min": 20, "max": 90},
                "min_ip_rating": "IP54",
                "uv_exposure": True,
                "condensation_risk": "moderate",
                "required_features": ["ventilation", "cable_sealing"],
            },
            EnvironmentType.OUTDOOR_MODERATE: {
                "temperature_range": {"min": -10, "max": 50},
                "humidity_range": {"min": 10, "max": 95},
                "min_ip_rating": "IP65",
                "uv_exposure": True,
                "condensation_risk": "high",
                "required_features": ["ventilation", "cable_sealing", "uv_protection"],
            },
            EnvironmentType.DESERT_HARSH: {
                "temperature_range": {"min": -10, "max": 70},
                "humidity_range": {"min": 5, "max": 40},
                "min_ip_rating": "IP65",
                "uv_exposure": True,
                "uv_intensity": "extreme",
                "condensation_risk": "low",
                "dust_protection": "required",
                "required_features": ["ventilation", "uv_protection", "heat_dissipation"],
            },
            EnvironmentType.TROPICAL: {
                "temperature_range": {"min": 15, "max": 45},
                "humidity_range": {"min": 60, "max": 100},
                "min_ip_rating": "IP67",
                "uv_exposure": True,
                "condensation_risk": "very_high",
                "fungal_growth_risk": True,
                "required_features": ["ventilation", "cable_sealing", "uv_protection", "anti_fungal"],
            },
            EnvironmentType.ARCTIC: {
                "temperature_range": {"min": -40, "max": 20},
                "humidity_range": {"min": 10, "max": 80},
                "min_ip_rating": "IP65",
                "uv_exposure": True,
                "condensation_risk": "high",
                "cold_brittle_risk": True,
                "required_features": ["cable_sealing", "cold_resistant_material"],
            },
            EnvironmentType.MARINE: {
                "temperature_range": {"min": -5, "max": 50},
                "humidity_range": {"min": 60, "max": 100},
                "min_ip_rating": "IP67",
                "uv_exposure": True,
                "salt_exposure": True,
                "condensation_risk": "very_high",
                "required_features": ["cable_sealing", "uv_protection", "corrosion_protection"],
            },
        }
    
    def validate_design(
        self,
        design: Dict[str, Any],
        environment: str,
        duration_months: int = 24,
    ) -> ValidationResult:
        """
        Validate design for environmental conditions.
        
        Args:
            design: Enclosure design dictionary
            environment: Target environment type
            duration_months: Expected deployment duration in months
            
        Returns:
            Validation result with issues and recommendations
        """
        env_enum = EnvironmentType(environment.lower())
        env_spec = self._environment_specs[env_enum]
        
        issues = []
        recommendations = []
        
        # Validate IP rating
        design_ip = design.get("ip_rating", "IP00")
        required_ip = env_spec["min_ip_rating"]
        ip_adequate = self._compare_ip_ratings(design_ip, required_ip)
        
        if not ip_adequate:
            issues.append(f"IP rating {design_ip} insufficient for {environment} (requires {required_ip})")
            recommendations.append(f"Upgrade enclosure to {required_ip} or higher")
        
        # Validate material
        material = design.get("material", "unknown")
        material_suitable = self._validate_material(material, env_spec, duration_months)
        
        if not material_suitable:
            issues.append(f"Material {material} may not be suitable for {duration_months} months in {environment}")
            recommendations.append("Consider using ASA or NYLON for better durability")
        
        # Validate temperature range
        temp_ok = self._validate_temperature_range(design, env_spec)
        if not temp_ok:
            issues.append(f"Design may not withstand temperature range: {env_spec['temperature_range']}")
            recommendations.append("Consider thermal insulation or material upgrade")
        
        # Validate UV protection
        uv_ok = True
        if env_spec.get("uv_exposure", False):
            if "uv_protection" not in design.get("features", []):
                uv_ok = False
                issues.append("UV protection not specified for outdoor deployment")
                recommendations.append("Add UV-resistant coating or use ASA material")
        
        # Validate required features
        design_features = set(design.get("features", []))
        required_features = set(env_spec.get("required_features", []))
        missing_features = required_features - design_features
        
        if missing_features:
            issues.append(f"Missing required features: {', '.join(missing_features)}")
            recommendations.append(f"Add features: {', '.join(missing_features)}")
        
        # Check condensation risk (only if ventilation is required by environment)
        if env_spec.get("ventilation_required", False):
            if env_spec.get("condensation_risk") in ["high", "very_high"]:
                if not design.get("ventilation", False):
                    issues.append("Ventilation required for high condensation risk environment")
                    recommendations.append("Add ventilation ports with moisture barriers")
        
        # Calculate confidence score
        checks = [ip_adequate, material_suitable, temp_ok, uv_ok, len(missing_features) == 0]
        confidence = sum(checks) / len(checks)
        
        # Adjust confidence for duration
        if duration_months > 24:
            confidence *= 0.9  # Reduce confidence for long deployments
        
        passed = len(issues) == 0
        
        return ValidationResult(
            passed=passed,
            environment=env_enum,
            duration_months=duration_months,
            ip_rating_adequate=ip_adequate,
            material_suitable=material_suitable,
            temperature_range_ok=temp_ok,
            uv_protection_ok=uv_ok,
            issues=issues,
            recommendations=recommendations,
            confidence_score=round(confidence, 2),
        )
    
    def _compare_ip_ratings(self, design_rating: str, required_rating: str) -> bool:
        """Compare IP ratings (simplified)."""
        # Extract numeric parts
        design_num = int(design_rating[2:]) if len(design_rating) >= 4 else 0
        required_num = int(required_rating[2:]) if len(required_rating) >= 4 else 0
        return design_num >= required_num
    
    def _validate_material(
        self,
        material: str,
        env_spec: Dict[str, Any],
        duration_months: int,
    ) -> bool:
        """Validate material suitability."""
        # Material durability matrix from WildCAM experience
        material_durability = {
            "pla": {"outdoor": False, "max_months": 6, "uv_resistant": False},
            "petg": {"outdoor": True, "max_months": 24, "uv_resistant": False},
            "asa": {"outdoor": True, "max_months": 60, "uv_resistant": True},
            "abs": {"outdoor": False, "max_months": 12, "uv_resistant": False},
            "tpu": {"outdoor": True, "max_months": 36, "uv_resistant": False},
            "nylon": {"outdoor": True, "max_months": 60, "uv_resistant": True},
        }
        
        mat_info = material_durability.get(material.lower(), {})
        
        # Check outdoor suitability
        if env_spec.get("uv_exposure") and not mat_info.get("outdoor", False):
            return False
        
        # Check duration
        if duration_months > mat_info.get("max_months", 0):
            return False
        
        # Check UV resistance
        if env_spec.get("uv_intensity") == "extreme" and not mat_info.get("uv_resistant", False):
            return False
        
        return True
    
    def _validate_temperature_range(
        self,
        design: Dict[str, Any],
        env_spec: Dict[str, Any],
    ) -> bool:
        """Validate design can handle temperature range."""
        # Material temperature limits
        material_limits = {
            "pla": {"min": 0, "max": 50},
            "petg": {"min": -20, "max": 60},
            "asa": {"min": -30, "max": 80},
            "abs": {"min": -20, "max": 70},
            "tpu": {"min": -30, "max": 60},
            "nylon": {"min": -40, "max": 85},
        }
        
        material = design.get("material", "").lower()
        limits = material_limits.get(material, {"min": -20, "max": 60})
        
        env_temp = env_spec["temperature_range"]
        
        return limits["min"] <= env_temp["min"] and limits["max"] >= env_temp["max"]
    
    def recommend_improvements(
        self,
        validation: ValidationResult,
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed improvement recommendations.
        
        Args:
            validation: Validation result
            
        Returns:
            List of improvement recommendations with details
        """
        improvements = []
        
        if not validation.ip_rating_adequate:
            improvements.append({
                "category": "sealing",
                "priority": "high",
                "description": "Improve IP rating with better sealing",
                "actions": [
                    "Add O-ring grooves for lid seal",
                    "Use cable glands for all port entries",
                    "Apply silicone sealant to seams",
                ],
                "estimated_cost": 5.0,
            })
        
        if not validation.material_suitable:
            improvements.append({
                "category": "material",
                "priority": "high",
                "description": "Upgrade to more durable material",
                "actions": [
                    "Switch from PLA/PETG to ASA for UV resistance",
                    "Consider NYLON for extreme environments",
                    "Apply UV-protective coating if material change not possible",
                ],
                "estimated_cost": 10.0,
            })
        
        if not validation.uv_protection_ok:
            improvements.append({
                "category": "uv_protection",
                "priority": "medium",
                "description": "Add UV protection",
                "actions": [
                    "Apply UV-resistant clear coat",
                    "Use UV-stable pigments in material",
                    "Add protective shroud or shield",
                ],
                "estimated_cost": 3.0,
            })
        
        if validation.environment == EnvironmentType.TROPICAL:
            improvements.append({
                "category": "moisture",
                "priority": "high",
                "description": "Enhanced moisture protection for tropical environment",
                "actions": [
                    "Add desiccant compartment",
                    "Install Gore-Tex vent for pressure equalization",
                    "Apply anti-fungal coating",
                ],
                "estimated_cost": 8.0,
            })
        
        return improvements
