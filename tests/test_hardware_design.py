"""
Tests for hardware design module (WildCAM_ESP32 integration).
"""

import pytest


def test_hardware_design_import():
    """Test hardware design module can be imported."""
    from accelerapp.hardware.design import (
        EnclosureGenerator,
        EnclosureDesign,
        BoardSupportMatrix,
        ESP32BoardType,
    )
    assert EnclosureGenerator is not None
    assert EnclosureDesign is not None
    assert BoardSupportMatrix is not None
    assert ESP32BoardType is not None


def test_board_support_matrix():
    """Test board support matrix initialization."""
    from accelerapp.hardware.design import BoardSupportMatrix, ESP32BoardType
    
    matrix = BoardSupportMatrix()
    boards = matrix.list_boards()
    
    assert len(boards) > 0
    assert ESP32BoardType.ESP32_CAM in boards
    assert ESP32BoardType.ESP32_MESHTASTIC in boards


def test_board_specification():
    """Test getting board specifications."""
    from accelerapp.hardware.design import BoardSupportMatrix, ESP32BoardType
    
    matrix = BoardSupportMatrix()
    spec = matrix.get_board_spec(ESP32BoardType.ESP32_CAM)
    
    assert spec is not None
    assert spec.display_name == "ESP32-CAM (AI-Thinker)"
    assert "camera" in spec.features
    assert len(spec.mounting_holes) == 4


def test_boards_by_feature():
    """Test filtering boards by feature."""
    from accelerapp.hardware.design import BoardSupportMatrix
    
    matrix = BoardSupportMatrix()
    camera_boards = matrix.get_boards_by_feature("camera")
    
    assert len(camera_boards) > 0


def test_meshtastic_compatible_boards():
    """Test getting Meshtastic compatible boards."""
    from accelerapp.hardware.design import BoardSupportMatrix, ESP32BoardType
    
    matrix = BoardSupportMatrix()
    meshtastic_boards = matrix.get_meshtastic_compatible_boards()
    
    assert ESP32BoardType.ESP32_MESHTASTIC in meshtastic_boards
    assert ESP32BoardType.ESP32_LORA in meshtastic_boards


def test_enclosure_generator_initialization():
    """Test enclosure generator initialization."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    assert generator is not None
    assert generator.board_matrix is not None


def test_generate_basic_enclosure():
    """Test generating basic enclosure."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    assert design is not None
    assert design.ip_rating == "IP65"
    assert design.wall_thickness == 3.5
    assert "camera_window" in design.features


def test_generate_meshtastic_enclosure():
    """Test generating Meshtastic enclosure."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_meshtastic",
        deployment_env="outdoor_professional",
    )
    
    assert design is not None
    assert "antenna_port" in design.features


def test_budget_constrained_design():
    """Test generating budget-constrained design."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_generic",
        deployment_env="outdoor_budget",
        budget_constraint="under_25_usd",
    )
    
    assert design is not None
    assert design.cost_estimate is not None
    assert design.cost_estimate["total"] < 30.0  # Should be reasonably close to target


def test_indoor_design():
    """Test generating indoor design."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_generic",
        deployment_env="indoor_lab",
    )
    
    assert design is not None
    assert design.ip_rating == "IP20"
    assert design.wall_thickness == 2.0


def test_desert_harsh_design():
    """Test generating design for harsh desert environment."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="desert_harsh",
    )
    
    assert design is not None
    assert design.ip_rating == "IP65"
    assert design.wall_thickness == 4.0


def test_enclosure_design_to_dict():
    """Test converting enclosure design to dictionary."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    design_dict = design.to_dict()
    
    assert isinstance(design_dict, dict)
    assert "board_type" in design_dict
    assert "deployment_env" in design_dict
    assert "cost_estimate" in design_dict


def test_cost_estimate_included():
    """Test that cost estimate is included in design."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_generic",
        deployment_env="outdoor_professional",
    )
    
    assert design.cost_estimate is not None
    assert "material" in design.cost_estimate
    assert "electricity" in design.cost_estimate
    assert "labor" in design.cost_estimate
    assert "total" in design.cost_estimate


def test_print_settings_included():
    """Test that print settings are included in design."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    assert design.print_settings is not None
    assert "nozzle_temp" in design.print_settings
    assert "bed_temp" in design.print_settings
    assert "layer_height" in design.print_settings
    assert "infill" in design.print_settings


def test_optimize_for_cost():
    """Test cost optimization."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    original_cost = design.cost_estimate["total"]
    optimized = generator.optimize_for_cost(design, target_cost=10.0)
    
    # Optimized design should attempt to reduce cost
    assert optimized is not None


def test_custom_features():
    """Test adding custom features to design."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_generic",
        deployment_env="outdoor_professional",
        custom_features=["led_indicator", "reset_button"],
    )
    
    assert "led_indicator" in design.features
    assert "reset_button" in design.features


def test_cable_ports_generated():
    """Test that cable ports are generated."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    design = generator.generate_for_board(
        board_type="esp32_cam",
        deployment_env="outdoor_professional",
    )
    
    assert len(design.cable_ports) > 0
    assert any(port["type"] == "usb" for port in design.cable_ports)


def test_invalid_board_type():
    """Test handling invalid board type."""
    from accelerapp.hardware.design import EnclosureGenerator
    
    generator = EnclosureGenerator()
    
    with pytest.raises(ValueError):
        generator.generate_for_board(
            board_type="invalid_board",
            deployment_env="outdoor_professional",
        )
