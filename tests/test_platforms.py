"""
Tests for platform abstraction layer.
"""

import pytest
from pathlib import Path
import tempfile


def test_platform_module_import():
    """Test platform module can be imported."""
    from accelerapp.platforms import get_platform, BasePlatform
    assert get_platform is not None
    assert BasePlatform is not None


def test_get_platform_arduino():
    """Test getting Arduino platform."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('arduino')
    assert platform is not None
    assert platform.name == 'arduino'


def test_get_platform_esp32():
    """Test getting ESP32 platform."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('esp32')
    assert platform is not None
    assert platform.name == 'esp32'


def test_get_platform_stm32():
    """Test getting STM32 platform."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('stm32')
    assert platform is not None
    assert platform.name == 'stm32'


def test_get_platform_micropython():
    """Test getting MicroPython platform."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('micropython')
    assert platform is not None
    assert platform.name == 'micropython'


def test_get_platform_invalid():
    """Test getting invalid platform raises error."""
    from accelerapp.platforms import get_platform
    
    with pytest.raises(ValueError):
        get_platform('invalid_platform')


def test_arduino_platform_info():
    """Test Arduino platform information."""
    from accelerapp.platforms import ArduinoPlatform
    
    platform = ArduinoPlatform()
    info = platform.get_platform_info()
    
    assert info['name'] == 'arduino'
    assert 'gpio' in info['capabilities']
    assert 'led' in info['peripherals']


def test_arduino_code_generation():
    """Test Arduino code generation."""
    from accelerapp.platforms import ArduinoPlatform
    
    platform = ArduinoPlatform()
    
    spec = {
        'device_name': 'TestDevice',
        'peripherals': [
            {'type': 'led', 'pin': 13},
        ],
        'pins': {'LED_PIN': 13},
        'timing': {'BAUD_RATE': 9600},
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        assert result['platform'] == 'arduino'
        assert len(result['files_generated']) > 0


def test_esp32_platform_info():
    """Test ESP32 platform information."""
    from accelerapp.platforms import ESP32Platform
    
    platform = ESP32Platform()
    info = platform.get_platform_info()
    
    assert info['name'] == 'esp32'
    assert 'wifi' in info['capabilities']
    assert 'bluetooth' in info['capabilities']


def test_esp32_code_generation():
    """Test ESP32 code generation."""
    from accelerapp.platforms import ESP32Platform
    
    platform = ESP32Platform()
    
    spec = {
        'device_name': 'TestDevice',
        'peripherals': [
            {'type': 'led', 'pin': 2},
        ],
        'timing': {'BAUD_RATE': 115200},
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        assert result['platform'] == 'esp32'


def test_esp32_wifi_generation():
    """Test ESP32 WiFi code generation."""
    from accelerapp.platforms import ESP32Platform
    
    platform = ESP32Platform()
    
    spec = {
        'device_name': 'TestDevice',
        'peripherals': [
            {'type': 'wifi_module'},
        ],
        'wifi': {
            'ssid': 'TestSSID',
            'password': 'TestPassword',
        },
        'timing': {'BAUD_RATE': 115200},
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        # Should generate WiFi config file
        assert any('wifi_config.h' in f for f in result['files_generated'])


def test_stm32_platform_info():
    """Test STM32 platform information."""
    from accelerapp.platforms import STM32Platform
    
    platform = STM32Platform()
    info = platform.get_platform_info()
    
    assert info['name'] == 'stm32'
    assert 'can' in info['capabilities']


def test_micropython_platform_info():
    """Test MicroPython platform information."""
    from accelerapp.platforms import MicroPythonPlatform
    
    platform = MicroPythonPlatform()
    info = platform.get_platform_info()
    
    assert info['name'] == 'micropython'
    assert 'python' in info['languages']


def test_micropython_code_generation():
    """Test MicroPython code generation."""
    from accelerapp.platforms import MicroPythonPlatform
    
    platform = MicroPythonPlatform()
    
    spec = {
        'device_name': 'TestDevice',
        'peripherals': [
            {'type': 'led', 'pin': 2, 'name': 'led'},
        ],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        assert result['platform'] == 'micropython'


def test_platform_validation():
    """Test platform configuration validation."""
    from accelerapp.platforms import ArduinoPlatform
    
    platform = ArduinoPlatform()
    
    # Valid config
    valid_config = {
        'device_name': 'Test',
        'peripherals': [
            {'type': 'led', 'pin': 13},
        ],
    }
    errors = platform.validate_config(valid_config)
    assert len(errors) == 0
    
    # Invalid config - missing device_name
    invalid_config = {
        'peripherals': [
            {'type': 'led', 'pin': 13},
        ],
    }
    errors = platform.validate_config(invalid_config)
    assert len(errors) > 0
