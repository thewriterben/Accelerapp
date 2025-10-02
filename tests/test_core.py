"""
Tests for core functionality.
"""

import pytest
from pathlib import Path
import tempfile
import yaml


def test_accelerapp_core_import():
    """Test that core module can be imported."""
    from accelerapp.core import AccelerappCore
    assert AccelerappCore is not None


def test_accelerapp_core_init():
    """Test core initialization."""
    from accelerapp.core import AccelerappCore
    
    core = AccelerappCore()
    assert core.config == {}
    assert core.hardware_spec == {}


def test_accelerapp_core_load_config():
    """Test configuration loading."""
    from accelerapp.core import AccelerappCore
    
    # Create a temporary config file
    config_data = {
        'device_name': 'Test Device',
        'platform': 'arduino',
        'hardware': {
            'mcu': 'ATmega328P'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        core = AccelerappCore(Path(config_path))
        assert core.config['device_name'] == 'Test Device'
        assert core.config['platform'] == 'arduino'
        assert core.hardware_spec == config_data.get('hardware', {})
    finally:
        Path(config_path).unlink()
