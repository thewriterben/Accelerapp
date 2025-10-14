"""
Tests for Firmware Generator ML Integration.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


def test_firmware_generator_with_ml():
    """Test firmware generation with ML integration."""
    from accelerapp.firmware.generator import FirmwareGenerator

    # Create hardware spec with ML configuration
    hardware_spec = {
        "platform": "arduino",
        "device_name": "SmartDevice",
        "peripherals": [
            {"type": "sensor", "pin": 2},
        ],
        "ml_config": {
            "task_type": "inference",
            "model_type": "classification",
            "input_shape": [1, 28, 28, 1],
            "num_classes": 10,
        },
    }

    generator = FirmwareGenerator(hardware_spec)

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Generate firmware with ML
        result = generator.generate(output_dir)

        assert result["status"] == "success"
        assert result["platform"] == "arduino"
        assert result["ml_enabled"] is True
        assert len(result["files_generated"]) > 0

        # Check that ML files were generated
        ml_inference_h = output_dir / "ml_inference.h"
        ml_inference_c = output_dir / "ml_inference.c"

        assert ml_inference_h.exists()
        assert ml_inference_c.exists()

        # Check main file includes ML
        main_file = output_dir / "main.ino"
        assert main_file.exists()
        main_content = main_file.read_text()
        assert '#include "ml_inference.h"' in main_content
        assert "ml_inference_init();" in main_content


def test_firmware_generator_without_ml():
    """Test firmware generation without ML integration."""
    from accelerapp.firmware.generator import FirmwareGenerator

    # Create hardware spec without ML configuration
    hardware_spec = {
        "platform": "arduino",
        "device_name": "SimpleDevice",
        "peripherals": [
            {"type": "led", "pin": 13},
        ],
    }

    generator = FirmwareGenerator(hardware_spec)

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Generate firmware without ML
        result = generator.generate(output_dir)

        assert result["status"] == "success"
        assert result["platform"] == "arduino"
        assert result["ml_enabled"] is False

        # Check that ML files were NOT generated
        ml_inference_h = output_dir / "ml_inference.h"
        ml_inference_c = output_dir / "ml_inference.c"

        assert not ml_inference_h.exists()
        assert not ml_inference_c.exists()

        # Check main file doesn't include ML
        main_file = output_dir / "main.ino"
        assert main_file.exists()
        main_content = main_file.read_text()
        assert '#include "ml_inference.h"' not in main_content
        assert "ml_inference_init();" not in main_content


def test_firmware_generator_ml_config_validation():
    """Test ML config is properly passed to TinyML agent."""
    from accelerapp.firmware.generator import FirmwareGenerator

    hardware_spec = {
        "platform": "esp32",
        "device_name": "SmartSensor",
        "ml_config": {
            "task_type": "inference",
            "model_type": "classification",
            "input_shape": [1, 96, 96, 1],
            "num_classes": 5,
        },
    }

    generator = FirmwareGenerator(hardware_spec)

    # Verify ML config is stored
    assert generator.ml_config is not None
    assert generator.ml_config["model_type"] == "classification"
    assert generator.ml_config["num_classes"] == 5


@pytest.mark.integration
def test_firmware_generator_multiple_platforms_with_ml():
    """Test firmware generation with ML on multiple platforms."""
    from accelerapp.firmware.generator import FirmwareGenerator

    platforms = ["arduino", "esp32", "stm32"]

    for platform in platforms:
        hardware_spec = {
            "platform": platform,
            "device_name": f"SmartDevice_{platform}",
            "ml_config": {
                "task_type": "inference",
                "model_type": "classification",
                "num_classes": 3,
            },
        }

        generator = FirmwareGenerator(hardware_spec)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = generator.generate(output_dir)

            assert result["status"] == "success"
            assert result["platform"] == platform
            assert result["ml_enabled"] is True

            # Verify ML files exist
            ml_inference_h = output_dir / "ml_inference.h"
            assert ml_inference_h.exists()
