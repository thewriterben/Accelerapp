"""
Tests for code generators.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


def test_firmware_generator_import():
    """Test firmware generator import."""
    from accelerapp.firmware.generator import FirmwareGenerator
    assert FirmwareGenerator is not None


def test_firmware_generator_init():
    """Test firmware generator initialization."""
    from accelerapp.firmware.generator import FirmwareGenerator
    
    spec = {
        'platform': 'arduino',
        'device_name': 'Test Device',
        'peripherals': []
    }
    
    generator = FirmwareGenerator(spec)
    assert generator.platform == 'arduino'
    assert generator.hardware_spec == spec


def test_firmware_generator_generate():
    """Test firmware generation."""
    from accelerapp.firmware.generator import FirmwareGenerator
    
    spec = {
        'platform': 'arduino',
        'device_name': 'Test Device',
        'peripherals': [
            {'type': 'led', 'pin': 13, 'description': 'Test LED'}
        ],
        'pins': {'LED_PIN': 13},
        'timing': {'BAUD_RATE': 9600}
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = FirmwareGenerator(spec)
        result = generator.generate(output_dir)
        
        assert result['status'] == 'success'
        assert result['platform'] == 'arduino'
        assert len(result['files_generated']) > 0
        
        # Check that files were created
        assert (output_dir / 'main.ino').exists()
        assert (output_dir / 'config.h').exists()


def test_software_generator_import():
    """Test software generator import."""
    from accelerapp.software.generator import SoftwareGenerator
    assert SoftwareGenerator is not None


def test_software_generator_python():
    """Test Python SDK generation."""
    from accelerapp.software.generator import SoftwareGenerator
    
    spec = {
        'device_name': 'Test Device',
        'software_language': 'python',
        'peripherals': [
            {'type': 'led', 'pin': 13}
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = SoftwareGenerator(spec)
        result = generator.generate(output_dir)
        
        assert result['status'] == 'success'
        assert result['language'] == 'python'
        assert len(result['files_generated']) > 0


def test_ui_generator_import():
    """Test UI generator import."""
    from accelerapp.ui.generator import UIGenerator
    assert UIGenerator is not None


def test_ui_generator_react():
    """Test React UI generation."""
    from accelerapp.ui.generator import UIGenerator
    
    spec = {
        'device_name': 'Test Device',
        'ui_framework': 'react',
        'peripherals': [
            {'type': 'led', 'pin': 13}
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        generator = UIGenerator(spec)
        result = generator.generate(output_dir)
        
        assert result['status'] == 'success'
        assert result['framework'] == 'react'
        assert len(result['files_generated']) > 0
