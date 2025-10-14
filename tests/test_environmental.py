"""
Tests for environmental validation module.
"""

import pytest


def test_environmental_import():
    """Test environmental module can be imported."""
    from accelerapp.hardware.environmental import (
        EnvironmentalValidator,
        ValidationResult,
        EnvironmentType,
    )
    assert EnvironmentalValidator is not None
    assert ValidationResult is not None
    assert EnvironmentType is not None


def test_validator_initialization():
    """Test validator initialization."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    assert validator is not None


def test_validate_indoor_design():
    """Test validating indoor design."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP20",
        "material": "pla",
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="indoor_controlled",
        duration_months=6,  # PLA lasts up to 6 months
    )
    
    assert result is not None
    assert result.passed


def test_validate_outdoor_design():
    """Test validating outdoor design."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": ["ventilation", "cable_sealing", "uv_protection"],
        "ventilation": True,  # Add ventilation flag
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    assert result.passed
    assert result.ip_rating_adequate
    assert result.material_suitable


def test_validate_inadequate_ip_rating():
    """Test detecting inadequate IP rating."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP20",  # Too low for outdoor
        "material": "petg",
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    assert not result.passed
    assert not result.ip_rating_adequate
    assert len(result.issues) > 0


def test_validate_unsuitable_material():
    """Test detecting unsuitable material."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "pla",  # Not suitable for outdoor
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    assert not result.passed
    assert not result.material_suitable


def test_validate_missing_features():
    """Test detecting missing required features."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": [],  # Missing required features
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    assert not result.passed
    assert len(result.issues) > 0


def test_validate_desert_harsh():
    """Test validating design for harsh desert environment."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": ["ventilation", "uv_protection", "heat_dissipation"],
        "ventilation": True,
    }
    
    result = validator.validate_design(
        design=design,
        environment="desert_harsh",
        duration_months=24,
    )
    
    assert result.passed
    assert result.uv_protection_ok


def test_validate_tropical():
    """Test validating design for tropical environment."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP67",
        "material": "asa",
        "features": ["ventilation", "cable_sealing", "uv_protection", "anti_fungal"],
        "ventilation": True,
    }
    
    result = validator.validate_design(
        design=design,
        environment="tropical",
        duration_months=24,
    )
    
    assert result.passed


def test_validate_arctic():
    """Test validating design for arctic environment."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "nylon",
        "features": ["cable_sealing", "cold_resistant_material", "uv_protection"],  # Add UV protection
        "ventilation": False,  # No ventilation for arctic
    }
    
    result = validator.validate_design(
        design=design,
        environment="arctic",
        duration_months=24,
    )
    
    assert result.passed
    assert result.temperature_range_ok


def test_validation_result_to_dict():
    """Test converting validation result to dictionary."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": ["ventilation", "cable_sealing", "uv_protection"],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert "passed" in result_dict
    assert "environment" in result_dict
    assert "confidence_score" in result_dict


def test_confidence_score():
    """Test confidence score calculation."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": ["ventilation", "cable_sealing", "uv_protection"],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    assert 0.0 <= result.confidence_score <= 1.0


def test_long_duration_reduces_confidence():
    """Test that long deployment duration reduces confidence."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP65",
        "material": "asa",
        "features": ["ventilation", "cable_sealing", "uv_protection"],
    }
    
    result_short = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=12,
    )
    
    result_long = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=36,
    )
    
    # Longer duration should have lower confidence
    assert result_long.confidence_score < result_short.confidence_score


def test_recommend_improvements():
    """Test generating improvement recommendations."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP20",
        "material": "pla",
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    improvements = validator.recommend_improvements(result)
    
    assert len(improvements) > 0
    assert all("category" in imp for imp in improvements)
    assert all("description" in imp for imp in improvements)


def test_tropical_specific_improvements():
    """Test tropical environment specific improvements."""
    from accelerapp.hardware.environmental import EnvironmentalValidator, EnvironmentType
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP54",
        "material": "petg",
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="tropical",
        duration_months=24,
    )
    
    improvements = validator.recommend_improvements(result)
    
    # Should have moisture-related improvements for tropical
    moisture_improvements = [imp for imp in improvements if imp["category"] == "moisture"]
    assert len(moisture_improvements) > 0


def test_recommendations_include_cost():
    """Test that recommendations include cost estimates."""
    from accelerapp.hardware.environmental import EnvironmentalValidator
    
    validator = EnvironmentalValidator()
    
    design = {
        "ip_rating": "IP20",
        "material": "pla",
        "features": [],
    }
    
    result = validator.validate_design(
        design=design,
        environment="outdoor_moderate",
        duration_months=24,
    )
    
    improvements = validator.recommend_improvements(result)
    
    for improvement in improvements:
        assert "estimated_cost" in improvement
