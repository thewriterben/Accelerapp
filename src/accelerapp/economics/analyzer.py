"""
Cost analysis and optimization for hardware deployments.
Based on WildCAM_ESP32 budget optimization strategies.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DeploymentRegion(Enum):
    """Geographic regions for cost analysis."""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"


@dataclass
class CostAnalysis:
    """Result of cost analysis."""
    region: DeploymentRegion
    quantity: int
    unit_cost: float
    total_cost: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    economies_of_scale: Dict[str, float] = field(default_factory=dict)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    comparison_to_commercial: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "region": self.region.value,
            "quantity": self.quantity,
            "unit_cost": self.unit_cost,
            "total_cost": self.total_cost,
            "breakdown": self.breakdown,
            "economies_of_scale": self.economies_of_scale,
            "optimization_opportunities": self.optimization_opportunities,
            "comparison_to_commercial": self.comparison_to_commercial,
        }


class CostAnalyzer:
    """
    Analyze and optimize hardware deployment costs.
    Implements WildCAM_ESP32 cost optimization strategies.
    """
    
    def __init__(self):
        """Initialize cost analyzer."""
        self._region_multipliers = self._initialize_region_multipliers()
        self._commercial_prices = self._initialize_commercial_prices()
    
    def _initialize_region_multipliers(self) -> Dict[DeploymentRegion, Dict[str, float]]:
        """Initialize regional cost multipliers."""
        return {
            DeploymentRegion.NORTH_AMERICA: {
                "material": 1.0,
                "labor": 1.2,
                "shipping": 1.0,
                "electricity": 0.12,  # USD per kWh
            },
            DeploymentRegion.EUROPE: {
                "material": 1.1,
                "labor": 1.5,
                "shipping": 1.2,
                "electricity": 0.18,
            },
            DeploymentRegion.ASIA_PACIFIC: {
                "material": 0.8,
                "labor": 0.6,
                "shipping": 0.9,
                "electricity": 0.10,
            },
            DeploymentRegion.LATIN_AMERICA: {
                "material": 0.9,
                "labor": 0.7,
                "shipping": 1.1,
                "electricity": 0.15,
            },
            DeploymentRegion.AFRICA: {
                "material": 1.2,
                "labor": 0.5,
                "shipping": 1.5,
                "electricity": 0.20,
            },
            DeploymentRegion.MIDDLE_EAST: {
                "material": 1.1,
                "labor": 0.8,
                "shipping": 1.3,
                "electricity": 0.08,
            },
        }
    
    def _initialize_commercial_prices(self) -> Dict[str, float]:
        """Initialize commercial equivalent prices for comparison."""
        return {
            "generic_outdoor_enclosure": 45.0,
            "professional_outdoor_enclosure": 120.0,
            "ip65_enclosure": 85.0,
            "ip67_enclosure": 150.0,
            "custom_enclosure": 200.0,
        }
    
    def analyze_deployment(
        self,
        design: Dict[str, Any],
        quantity: int = 1,
        region: str = "north_america",
    ) -> CostAnalysis:
        """
        Analyze deployment cost.
        
        Args:
            design: Enclosure design dictionary
            quantity: Number of units to produce
            region: Deployment region
            
        Returns:
            Cost analysis with breakdown and optimization opportunities
        """
        region_enum = DeploymentRegion(region.lower())
        multipliers = self._region_multipliers[region_enum]
        
        # Get base costs from design
        base_cost = design.get("cost_estimate", {})
        
        # Apply regional multipliers
        material_cost = base_cost.get("material", 0) * multipliers["material"]
        electricity_cost = base_cost.get("electricity", 0) * multipliers["electricity"]
        labor_cost = base_cost.get("labor", 0) * multipliers["labor"]
        
        # Calculate shipping (if applicable)
        shipping_cost = 0
        if quantity > 1:
            shipping_cost = self._calculate_shipping(quantity, region_enum)
        
        # Calculate unit cost before economies of scale
        base_unit_cost = material_cost + electricity_cost + labor_cost
        
        # Apply economies of scale
        scale_discount = self._calculate_scale_discount(quantity)
        unit_cost = base_unit_cost * (1 - scale_discount)
        
        # Add per-unit shipping
        unit_cost += shipping_cost / quantity if quantity > 0 else 0
        
        # Calculate total
        total_cost = unit_cost * quantity
        
        # Create breakdown
        breakdown = {
            "material": round(material_cost * quantity, 2),
            "electricity": round(electricity_cost * quantity, 2),
            "labor": round(labor_cost * quantity, 2),
            "shipping": round(shipping_cost, 2),
            "unit_cost": round(unit_cost, 2),
            "total": round(total_cost, 2),
        }
        
        # Calculate economies of scale
        economies = {
            "base_unit_cost": round(base_unit_cost, 2),
            "scaled_unit_cost": round(unit_cost, 2),
            "discount_percent": round(scale_discount * 100, 2),
            "savings_per_unit": round(base_unit_cost - unit_cost, 2),
            "total_savings": round((base_unit_cost - unit_cost) * quantity, 2),
        }
        
        # Find optimization opportunities
        opportunities = self._find_optimization_opportunities(design, quantity, region_enum)
        
        # Compare to commercial alternatives
        comparison = self._compare_to_commercial(design, unit_cost)
        
        return CostAnalysis(
            region=region_enum,
            quantity=quantity,
            unit_cost=round(unit_cost, 2),
            total_cost=round(total_cost, 2),
            breakdown=breakdown,
            economies_of_scale=economies,
            optimization_opportunities=opportunities,
            comparison_to_commercial=comparison,
        )
    
    def _calculate_shipping(self, quantity: int, region: DeploymentRegion) -> float:
        """Calculate shipping cost."""
        multipliers = self._region_multipliers[region]
        base_shipping = 10.0  # Base shipping cost
        
        # Volume discount
        if quantity > 10:
            base_shipping *= 0.8
        if quantity > 50:
            base_shipping *= 0.7
        if quantity > 100:
            base_shipping *= 0.6
        
        return base_shipping * multipliers["shipping"] * (quantity ** 0.7)
    
    def _calculate_scale_discount(self, quantity: int) -> float:
        """Calculate economies of scale discount."""
        if quantity == 1:
            return 0.0
        elif quantity <= 10:
            return 0.05
        elif quantity <= 50:
            return 0.15
        elif quantity <= 100:
            return 0.25
        else:
            return 0.35
    
    def _find_optimization_opportunities(
        self,
        design: Dict[str, Any],
        quantity: int,
        region: DeploymentRegion,
    ) -> List[Dict[str, Any]]:
        """Identify cost optimization opportunities."""
        opportunities = []
        
        # Material optimization
        material = design.get("material", "").lower()
        if material in ["asa", "nylon"]:
            opportunities.append({
                "category": "material",
                "description": "Consider PETG for non-harsh environments",
                "potential_savings": 8.0,
                "impact": "medium",
                "trade_off": "Reduced UV resistance and durability",
            })
        
        # Quantity optimization
        if quantity < 10:
            opportunities.append({
                "category": "quantity",
                "description": "Increase order to 10+ units for volume discount",
                "potential_savings": 2.0,
                "impact": "low",
                "trade_off": "Higher upfront investment",
            })
        
        # Wall thickness optimization
        wall_thickness = design.get("wall_thickness", 0)
        if wall_thickness > 3.0:
            opportunities.append({
                "category": "design",
                "description": "Reduce wall thickness if environment permits",
                "potential_savings": 3.0,
                "impact": "medium",
                "trade_off": "Slightly reduced structural strength",
            })
        
        # Infill optimization
        print_settings = design.get("print_settings", {})
        infill = print_settings.get("infill", 0)
        if infill > 25:
            opportunities.append({
                "category": "printing",
                "description": "Reduce infill percentage",
                "potential_savings": 2.5,
                "impact": "low",
                "trade_off": "Slightly reduced strength",
            })
        
        # Regional sourcing
        if region in [DeploymentRegion.EUROPE, DeploymentRegion.AFRICA]:
            opportunities.append({
                "category": "sourcing",
                "description": "Source materials locally to reduce costs",
                "potential_savings": 5.0,
                "impact": "medium",
                "trade_off": "May require longer lead times",
            })
        
        # Community bulk ordering
        if quantity >= 5:
            opportunities.append({
                "category": "community",
                "description": "Coordinate with community for bulk ordering",
                "potential_savings": 4.0,
                "impact": "medium",
                "trade_off": "Requires coordination effort",
            })
        
        return opportunities
    
    def _compare_to_commercial(
        self,
        design: Dict[str, Any],
        unit_cost: float,
    ) -> Dict[str, float]:
        """Compare cost to commercial alternatives."""
        ip_rating = design.get("ip_rating", "IP00")
        
        # Select commercial equivalent
        if ip_rating >= "IP67":
            commercial_price = self._commercial_prices["ip67_enclosure"]
        elif ip_rating >= "IP65":
            commercial_price = self._commercial_prices["ip65_enclosure"]
        else:
            commercial_price = self._commercial_prices["generic_outdoor_enclosure"]
        
        savings = commercial_price - unit_cost
        savings_percent = (savings / commercial_price * 100) if commercial_price > 0 else 0
        
        return {
            "commercial_price": commercial_price,
            "our_price": unit_cost,
            "savings": round(savings, 2),
            "savings_percent": round(savings_percent, 1),
            "recommendation": "DIY cost-effective" if savings > 0 else "Consider commercial",
        }
    
    def optimize_for_budget(
        self,
        design: Dict[str, Any],
        target_budget: float,
        quantity: int = 1,
        region: str = "north_america",
    ) -> Dict[str, Any]:
        """
        Optimize design to meet budget target.
        
        Args:
            design: Original design
            target_budget: Target budget per unit
            quantity: Number of units
            region: Deployment region
            
        Returns:
            Optimized design with cost breakdown
        """
        analysis = self.analyze_deployment(design, quantity, region)
        
        if analysis.unit_cost <= target_budget:
            return {
                "optimized": False,
                "reason": "Already within budget",
                "design": design,
                "analysis": analysis.to_dict(),
            }
        
        # Apply optimization opportunities
        optimized_design = design.copy()
        applied_optimizations = []
        
        for opp in analysis.optimization_opportunities:
            if opp["category"] == "material":
                optimized_design["material"] = "petg"
                applied_optimizations.append(opp["description"])
            elif opp["category"] == "design":
                optimized_design["wall_thickness"] = 2.5
                applied_optimizations.append(opp["description"])
            elif opp["category"] == "printing":
                if "print_settings" not in optimized_design:
                    optimized_design["print_settings"] = {}
                optimized_design["print_settings"]["infill"] = 20
                applied_optimizations.append(opp["description"])
        
        # Recalculate with optimizations
        new_analysis = self.analyze_deployment(optimized_design, quantity, region)
        
        return {
            "optimized": True,
            "original_cost": analysis.unit_cost,
            "optimized_cost": new_analysis.unit_cost,
            "target_budget": target_budget,
            "within_budget": new_analysis.unit_cost <= target_budget,
            "applied_optimizations": applied_optimizations,
            "design": optimized_design,
            "analysis": new_analysis.to_dict(),
        }
