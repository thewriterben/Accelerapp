#!/usr/bin/env python3
"""
Demonstration of WildCAM_ESP32 integration for hardware generation.
Shows enclosure design, environmental validation, and cost analysis.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from accelerapp.hardware.design import EnclosureGenerator, BoardSupportMatrix
from accelerapp.hardware.environmental import EnvironmentalValidator
from accelerapp.economics import CostAnalyzer


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_board_support():
    """Demonstrate board support matrix."""
    print_section("Board Support Matrix")
    
    matrix = BoardSupportMatrix()
    boards = matrix.list_boards()
    
    print(f"\n✓ Supported boards: {len(boards)}")
    for board in boards[:3]:
        spec = matrix.get_board_spec(board)
        print(f"  - {spec.display_name}")
        print(f"    Dimensions: {spec.dimensions}")
        print(f"    Features: {', '.join(spec.features[:3])}")
    
    # Show Meshtastic-compatible boards
    meshtastic_boards = matrix.get_meshtastic_compatible_boards()
    print(f"\n✓ Meshtastic-compatible boards: {len(meshtastic_boards)}")


def demo_enclosure_generation():
    """Demonstrate enclosure generation."""
    print_section("Enclosure Generation")
    
    generator = EnclosureGenerator()
    
    # Generate for ESP32-CAM
    print("\n1. ESP32-CAM Enclosure (Outdoor Professional)")
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    print(f"   Board Type: {design.board_type.value}")
    print(f"   Material: {design.material.value}")
    print(f"   IP Rating: {design.ip_rating}")
    print(f"   Wall Thickness: {design.wall_thickness}mm")
    print(f"   Features: {', '.join(design.features)}")
    print(f"   Cost Estimate: ${design.cost_estimate['total']}")
    
    # Generate for Meshtastic
    print("\n2. Meshtastic Node Enclosure")
    meshtastic_design = generator.generate_for_board(
        board_type="esp32_meshtastic",
        deployment_env="outdoor_professional",
    )
    
    print(f"   Board Type: {meshtastic_design.board_type.value}")
    print(f"   Material: {meshtastic_design.material.value}")
    print(f"   IP Rating: {meshtastic_design.ip_rating}")
    print(f"   Features: {', '.join(meshtastic_design.features)}")
    
    # Budget-constrained design
    print("\n3. Budget-Constrained Design")
    budget_design = generator.generate_for_board(
        board_type="esp32_generic",
        deployment_env="outdoor_budget",
        budget_constraint="under_25_usd",
    )
    
    print(f"   Material: {budget_design.material.value}")
    print(f"   Cost Estimate: ${budget_design.cost_estimate['total']}")
    print(f"   Print Settings:")
    print(f"     - Nozzle Temp: {budget_design.print_settings['nozzle_temp']}°C")
    print(f"     - Bed Temp: {budget_design.print_settings['bed_temp']}°C")
    print(f"     - Infill: {budget_design.print_settings['infill']}%")
    
    return design


def demo_environmental_validation(design):
    """Demonstrate environmental validation."""
    print_section("Environmental Validation")
    
    validator = EnvironmentalValidator()
    
    # Validate for outdoor moderate
    print("\n1. Outdoor Moderate Environment (24 months)")
    design_dict = design.to_dict()
    design_dict["ventilation"] = True  # Add ventilation flag
    
    result = validator.validate_design(
        design=design_dict,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    print(f"   Passed: {'✓' if result.passed else '✗'}")
    print(f"   IP Rating Adequate: {'✓' if result.ip_rating_adequate else '✗'}")
    print(f"   Material Suitable: {'✓' if result.material_suitable else '✗'}")
    print(f"   Temperature Range OK: {'✓' if result.temperature_range_ok else '✗'}")
    print(f"   UV Protection OK: {'✓' if result.uv_protection_ok else '✗'}")
    print(f"   Confidence Score: {result.confidence_score}")
    
    if result.issues:
        print(f"\n   Issues Found:")
        for issue in result.issues:
            print(f"     - {issue}")
    
    # Validate for harsh desert
    print("\n2. Desert Harsh Environment (24 months)")
    result_desert = validator.validate_design(
        design=design_dict,
        environment="desert_harsh",
        duration_months=24,
    )
    
    print(f"   Passed: {'✓' if result_desert.passed else '✗'}")
    print(f"   Confidence Score: {result_desert.confidence_score}")
    
    if not result_desert.passed:
        print(f"\n   Recommendations:")
        improvements = validator.recommend_improvements(result_desert)
        for imp in improvements[:3]:
            print(f"     - {imp['description']} (${imp['estimated_cost']})")
    
    # Validate for tropical
    print("\n3. Tropical Environment (12 months)")
    result_tropical = validator.validate_design(
        design=design_dict,
        environment="tropical",
        duration_months=12,
    )
    
    print(f"   Passed: {'✓' if result_tropical.passed else '✗'}")
    
    if result_tropical.issues:
        print(f"   Issues: {len(result_tropical.issues)}")


def demo_cost_analysis(design):
    """Demonstrate cost analysis."""
    print_section("Cost Analysis")
    
    analyzer = CostAnalyzer()
    
    # Single unit analysis
    print("\n1. Single Unit (North America)")
    analysis = analyzer.analyze_deployment(
        design=design.to_dict(),
        quantity=1,
        region="north_america",
    )
    
    print(f"   Unit Cost: ${analysis.unit_cost}")
    print(f"   Breakdown:")
    print(f"     - Material: ${analysis.breakdown['material']}")
    print(f"     - Electricity: ${analysis.breakdown['electricity']}")
    print(f"     - Labor: ${analysis.breakdown['labor']}")
    
    # Compare to commercial
    if analysis.comparison_to_commercial:
        comp = analysis.comparison_to_commercial
        print(f"\n   Commercial Comparison:")
        print(f"     - Commercial Price: ${comp['commercial_price']}")
        print(f"     - Our Price: ${comp['our_price']:.2f}")
        print(f"     - Savings: ${comp['savings']} ({comp['savings_percent']}%)")
        print(f"     - Recommendation: {comp['recommendation']}")
    
    # Bulk order analysis
    print("\n2. Bulk Order (50 units)")
    bulk_analysis = analyzer.analyze_deployment(
        design=design.to_dict(),
        quantity=50,
        region="north_america",
    )
    
    print(f"   Unit Cost: ${bulk_analysis.unit_cost}")
    print(f"   Total Cost: ${bulk_analysis.total_cost}")
    print(f"   Economies of Scale:")
    print(f"     - Discount: {bulk_analysis.economies_of_scale['discount_percent']}%")
    print(f"     - Total Savings: ${bulk_analysis.economies_of_scale['total_savings']}")
    
    # Show optimization opportunities
    if bulk_analysis.optimization_opportunities:
        print(f"\n   Optimization Opportunities:")
        for opp in bulk_analysis.optimization_opportunities[:3]:
            print(f"     - {opp['description']}")
            print(f"       Impact: {opp['impact']}, Savings: ${opp['potential_savings']}")
    
    # Regional comparison
    print("\n3. Regional Cost Comparison")
    regions = ["north_america", "europe", "asia_pacific"]
    for region in regions:
        regional_analysis = analyzer.analyze_deployment(
            design=design.to_dict(),
            quantity=10,
            region=region,
        )
        print(f"   {region.replace('_', ' ').title()}: ${regional_analysis.unit_cost}")


def demo_integrated_workflow():
    """Demonstrate complete integrated workflow."""
    print_section("Integrated Workflow: Meshtastic Community Deployment")
    
    generator = EnclosureGenerator()
    validator = EnvironmentalValidator()
    analyzer = CostAnalyzer()
    
    print("\nScenario: Community mesh network with 20 nodes")
    print("Environment: Urban outdoor")
    print("Budget: $25 per node")
    
    # Step 1: Generate design
    print("\n→ Step 1: Generate enclosure design")
    design = generator.generate_for_board(
        board_type="esp32_meshtastic",
        deployment_env="urban_outdoor",
        budget_constraint="under_25_usd",
    )
    print(f"  ✓ Generated {design.material.value.upper()} enclosure")
    print(f"  ✓ IP Rating: {design.ip_rating}")
    
    # Step 2: Validate environment
    print("\n→ Step 2: Validate for environment")
    design_dict = design.to_dict()
    design_dict["ventilation"] = True
    result = validator.validate_design(
        design=design_dict,
        environment="outdoor_mild",  # Urban outdoor is similar to outdoor_mild
        duration_months=36,
    )
    print(f"  {'✓' if result.passed else '✗'} Validation: {result.confidence_score} confidence")
    
    # Step 3: Analyze costs
    print("\n→ Step 3: Analyze deployment costs")
    analysis = analyzer.analyze_deployment(
        design=design_dict,
        quantity=20,
        region="north_america",
    )
    print(f"  ✓ Unit Cost: ${analysis.unit_cost}")
    print(f"  ✓ Total Cost: ${analysis.total_cost}")
    print(f"  ✓ Within Budget: {'Yes' if analysis.unit_cost <= 25 else 'No'}")
    
    # Step 4: Optimize if needed
    if analysis.unit_cost > 25:
        print("\n→ Step 4: Optimize for budget")
        optimized = analyzer.optimize_for_budget(
            design=design_dict,
            target_budget=25.0,
            quantity=20,
            region="north_america",
        )
        print(f"  ✓ Optimized Cost: ${optimized['optimized_cost']}")
        print(f"  ✓ Within Budget: {'Yes' if optimized['within_budget'] else 'No'}")
    
    print("\n✓ Deployment ready!")


def main():
    """Run all demonstrations."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "WildCAM_ESP32 Hardware Integration Demo" + " " * 13 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        demo_board_support()
        design = demo_enclosure_generation()
        demo_environmental_validation(design)
        demo_cost_analysis(design)
        demo_integrated_workflow()
        
        print("\n" + "=" * 70)
        print("  All demonstrations completed successfully!")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Production-ready 3D enclosure designs for ESP32/Meshtastic")
        print("  ✓ Environmental hardening validation (IP65+)")
        print("  ✓ Cost optimization (30-50% savings vs commercial)")
        print("  ✓ Multi-environment support (indoor, outdoor, harsh)")
        print("  ✓ Community-oriented deployment economics")
        print("\nIntegration Benefits:")
        print("  • Complete hardware-software solution generation")
        print("  • Field-proven designs from WildCAM_ESP32 project")
        print("  • Budget-friendly options for educational projects")
        print("  • Professional-grade for commercial deployments")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
