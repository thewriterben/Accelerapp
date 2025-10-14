"""
Tests for economics/cost analysis module.
"""

import pytest


def test_economics_import():
    """Test economics module can be imported."""
    from accelerapp.economics import CostAnalyzer, CostAnalysis, DeploymentRegion
    assert CostAnalyzer is not None
    assert CostAnalysis is not None
    assert DeploymentRegion is not None


def test_cost_analyzer_initialization():
    """Test cost analyzer initialization."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    assert analyzer is not None


def test_analyze_single_unit():
    """Test analyzing cost for single unit."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(
        design=design,
        quantity=1,
        region="north_america",
    )
    
    assert analysis is not None
    assert analysis.quantity == 1
    assert analysis.unit_cost > 0


def test_analyze_bulk_order():
    """Test analyzing cost for bulk order."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(
        design=design,
        quantity=50,
        region="north_america",
    )
    
    assert analysis.quantity == 50
    assert analysis.total_cost > 0


def test_economies_of_scale():
    """Test that bulk orders benefit from economies of scale (discount applied)."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    single_analysis = analyzer.analyze_deployment(design, 1, "north_america")
    bulk_analysis = analyzer.analyze_deployment(design, 50, "north_america")
    
    # Bulk should have discount percent > 0
    assert bulk_analysis.economies_of_scale["discount_percent"] > 0
    # Base unit cost before scaling should be same or similar
    assert bulk_analysis.economies_of_scale["base_unit_cost"] > 0


def test_regional_differences():
    """Test that different regions have different costs."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    na_analysis = analyzer.analyze_deployment(design, 10, "north_america")
    asia_analysis = analyzer.analyze_deployment(design, 10, "asia_pacific")
    
    # Asia Pacific should generally be cheaper due to lower labor costs
    assert asia_analysis.unit_cost != na_analysis.unit_cost


def test_cost_breakdown():
    """Test that cost breakdown is provided."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(design, 1, "north_america")
    
    assert "material" in analysis.breakdown
    assert "electricity" in analysis.breakdown
    assert "labor" in analysis.breakdown
    assert "total" in analysis.breakdown


def test_economies_of_scale_info():
    """Test that economies of scale information is provided."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(design, 50, "north_america")
    
    assert "base_unit_cost" in analysis.economies_of_scale
    assert "scaled_unit_cost" in analysis.economies_of_scale
    assert "discount_percent" in analysis.economies_of_scale
    assert "total_savings" in analysis.economies_of_scale


def test_optimization_opportunities():
    """Test that optimization opportunities are identified."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        },
        "material": "asa",
        "wall_thickness": 4.0,
    }
    
    analysis = analyzer.analyze_deployment(design, 1, "north_america")
    
    assert len(analysis.optimization_opportunities) > 0


def test_commercial_comparison():
    """Test comparison to commercial alternatives."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        },
        "ip_rating": "IP65",
    }
    
    analysis = analyzer.analyze_deployment(design, 1, "north_america")
    
    assert analysis.comparison_to_commercial is not None
    assert "commercial_price" in analysis.comparison_to_commercial
    assert "our_price" in analysis.comparison_to_commercial
    assert "savings" in analysis.comparison_to_commercial


def test_cost_analysis_to_dict():
    """Test converting cost analysis to dictionary."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(design, 1, "north_america")
    analysis_dict = analysis.to_dict()
    
    assert isinstance(analysis_dict, dict)
    assert "quantity" in analysis_dict
    assert "total_cost" in analysis_dict


def test_optimize_for_budget():
    """Test optimizing design for budget."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 15.0,
            "electricity": 2.0,
            "labor": 5.0,
        },
        "material": "asa",
        "wall_thickness": 4.0,
        "print_settings": {
            "infill": 35,
        }
    }
    
    result = analyzer.optimize_for_budget(
        design=design,
        target_budget=15.0,
        quantity=1,
        region="north_america",
    )
    
    assert result is not None
    assert "optimized" in result


def test_budget_already_met():
    """Test when budget is already met."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 5.0,
            "electricity": 1.0,
            "labor": 2.0,
        }
    }
    
    result = analyzer.optimize_for_budget(
        design=design,
        target_budget=15.0,
        quantity=1,
        region="north_america",
    )
    
    assert result["optimized"] is False
    assert "Already within budget" in result["reason"]


def test_quantity_discount_recommendation():
    """Test that quantity discount is recommended for small orders."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(design, 5, "north_america")
    
    # Should have quantity optimization opportunity
    quantity_opps = [
        opp for opp in analysis.optimization_opportunities
        if opp["category"] == "quantity"
    ]
    assert len(quantity_opps) > 0


def test_material_optimization_opportunity():
    """Test material optimization opportunity for expensive materials."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 15.0,
            "electricity": 1.5,
            "labor": 3.0,
        },
        "material": "nylon",
    }
    
    analysis = analyzer.analyze_deployment(design, 1, "north_america")
    
    # Should have material optimization opportunity
    material_opps = [
        opp for opp in analysis.optimization_opportunities
        if opp["category"] == "material"
    ]
    assert len(material_opps) > 0


def test_community_bulk_ordering():
    """Test community bulk ordering recommendation."""
    from accelerapp.economics import CostAnalyzer
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    analysis = analyzer.analyze_deployment(design, 5, "north_america")
    
    # Should have community bulk ordering opportunity
    community_opps = [
        opp for opp in analysis.optimization_opportunities
        if opp["category"] == "community"
    ]
    assert len(community_opps) > 0


def test_all_regions():
    """Test that all regions can be analyzed."""
    from accelerapp.economics import CostAnalyzer, DeploymentRegion
    
    analyzer = CostAnalyzer()
    
    design = {
        "cost_estimate": {
            "material": 8.0,
            "electricity": 1.5,
            "labor": 3.0,
        }
    }
    
    for region in DeploymentRegion:
        analysis = analyzer.analyze_deployment(design, 1, region.value)
        assert analysis is not None
        assert analysis.unit_cost > 0
