"""
Tests for M5Stack platform implementation.
"""

import pytest
from pathlib import Path
import tempfile


def test_m5stack_platform_import():
    """Test M5Stack platform can be imported."""
    from accelerapp.platforms import M5StackPlatform
    assert M5StackPlatform is not None


def test_get_m5stack_platform():
    """Test getting M5Stack platform via factory."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('m5stack')
    assert platform is not None
    assert platform.name == 'm5stack'


def test_get_m5stack_core_platform():
    """Test getting M5Stack Core variant via factory."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('m5stack_core')
    assert platform is not None
    assert platform.name == 'm5stack'


def test_get_m5stack_core2_platform():
    """Test getting M5Stack Core2 variant via factory."""
    from accelerapp.platforms import get_platform
    
    platform = get_platform('m5stack_core2')
    assert platform is not None
    assert platform.name == 'm5stack'


def test_m5stack_platform_info():
    """Test M5Stack platform information."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    info = platform.get_platform_info()
    
    assert info['name'] == 'm5stack'
    assert info['display_name'] == 'M5Stack'
    assert 'gpio' in info['capabilities']
    assert 'display' in info['capabilities']
    assert 'wifi' in info['capabilities']
    assert 'bluetooth' in info['capabilities']
    assert 'tft' in info['capabilities']
    assert 'buttons' in info['capabilities']
    assert 'speaker' in info['capabilities']
    assert info['display'] == '320x240 TFT (ILI9341)'
    assert info['library'] == 'M5Stack Arduino Library'


def test_m5stack_capabilities():
    """Test M5Stack platform capabilities."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    # Test key M5Stack capabilities
    assert platform.supports_capability('display')
    assert platform.supports_capability('tft')
    assert platform.supports_capability('buttons')
    assert platform.supports_capability('speaker')
    assert platform.supports_capability('wifi')
    assert platform.supports_capability('bluetooth')
    assert platform.supports_capability('i2c')
    assert platform.supports_capability('sd_card')


def test_m5stack_peripherals():
    """Test M5Stack supported peripherals."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    peripherals = platform.get_supported_peripherals()
    
    assert 'display' in peripherals
    assert 'button' in peripherals
    assert 'speaker' in peripherals
    assert 'sensor' in peripherals
    assert 'accelerometer' in peripherals
    assert 'wifi_module' in peripherals


def test_m5stack_build_config():
    """Test M5Stack build configuration."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    config = platform.get_build_config()
    
    assert config['platform'] == 'm5stack'
    assert config['build_system'] == 'platformio'
    assert config['board'] == 'm5stack-core-esp32'
    assert config['framework'] == 'arduino'
    assert 'M5Stack' in config['lib_deps']


def test_m5stack_basic_code_generation():
    """Test basic M5Stack code generation."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'TestM5Stack',
        'peripherals': [
            {'type': 'display', 'description': 'Built-in display'},
            {'type': 'button', 'pin': 39, 'name': 'Button A'},
        ],
        'timing': {'BAUD_RATE': 115200},
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        assert result['platform'] == 'm5stack'
        assert len(result['files_generated']) >= 3
        
        # Check main.cpp exists and contains M5Stack code
        main_file = output_dir / "main.cpp"
        assert main_file.exists()
        main_content = main_file.read_text()
        assert '#include <M5Stack.h>' in main_content
        assert 'M5.begin()' in main_content
        assert 'M5.Lcd' in main_content
        assert 'M5.update()' in main_content
        
        # Check config.h exists
        config_file = output_dir / "config.h"
        assert config_file.exists()
        config_content = config_file.read_text()
        assert '#define DEVICE_NAME "TestM5Stack"' in config_content
        assert '#define M5_BUTTON_A 39' in config_content
        
        # Check platformio.ini exists
        platformio_file = output_dir / "platformio.ini"
        assert platformio_file.exists()
        platformio_content = platformio_file.read_text()
        assert 'platform = espressif32' in platformio_content
        assert 'M5Stack' in platformio_content


def test_m5stack_wifi_code_generation():
    """Test M5Stack WiFi code generation."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'M5Stack WiFi Device',
        'peripherals': [
            {'type': 'display'},
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
        
        # Check WiFi config file was generated
        wifi_files = [f for f in result['files_generated'] if 'wifi_config.h' in f]
        assert len(wifi_files) > 0
        
        # Check main.cpp has WiFi code
        main_file = output_dir / "main.cpp"
        main_content = main_file.read_text()
        assert '#include <WiFi.h>' in main_content
        assert 'WiFi.begin' in main_content
        assert 'WiFi Connected' in main_content
        
        # Check wifi_config.h
        wifi_file = output_dir / "wifi_config.h"
        assert wifi_file.exists()
        wifi_content = wifi_file.read_text()
        assert 'WIFI_SSID "TestSSID"' in wifi_content
        assert 'WIFI_PASSWORD "TestPassword"' in wifi_content


def test_m5stack_button_handling():
    """Test M5Stack button handling in generated code."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'M5Stack Buttons',
        'peripherals': [
            {'type': 'display'},
            {'type': 'button', 'pin': 39, 'name': 'Button A'},
            {'type': 'button', 'pin': 38, 'name': 'Button B'},
            {'type': 'button', 'pin': 37, 'name': 'Button C'},
        ],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        
        main_file = output_dir / "main.cpp"
        main_content = main_file.read_text()
        
        # Check button handling code
        assert 'M5.BtnA.wasPressed()' in main_content
        assert 'M5.BtnB.wasPressed()' in main_content
        assert 'M5.BtnC.wasPressed()' in main_content
        assert 'Button A pressed' in main_content


def test_m5stack_sensor_integration():
    """Test M5Stack sensor integration."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'M5Stack Sensor',
        'peripherals': [
            {'type': 'display'},
            {'type': 'sensor', 'pin': 36, 'description': 'Temperature sensor'},
        ],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        assert result['status'] == 'success'
        
        main_file = output_dir / "main.cpp"
        main_content = main_file.read_text()
        
        # Check sensor reading code
        assert 'analogRead(36)' in main_content
        assert 'Sensor' in main_content


def test_m5stack_config_validation():
    """Test M5Stack configuration validation."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    # Valid config
    valid_config = {
        'device_name': 'Test',
        'peripherals': [
            {'type': 'display'},
            {'type': 'button', 'pin': 39},
        ],
    }
    errors = platform.validate_config(valid_config)
    assert len(errors) == 0
    
    # Invalid config - missing device_name
    invalid_config1 = {
        'peripherals': [
            {'type': 'display'},
        ],
    }
    errors = platform.validate_config(invalid_config1)
    assert len(errors) > 0
    assert any('device_name' in err for err in errors)
    
    # Invalid config - unsupported peripheral
    invalid_config2 = {
        'device_name': 'Test',
        'peripherals': [
            {'type': 'invalid_peripheral'},
        ],
    }
    errors = platform.validate_config(invalid_config2)
    assert len(errors) > 0
    
    # Invalid config - peripheral missing type
    invalid_config3 = {
        'device_name': 'Test',
        'peripherals': [
            {'pin': 39},
        ],
    }
    errors = platform.validate_config(invalid_config3)
    assert len(errors) > 0


def test_m5stack_model_validation():
    """Test M5Stack model validation."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    # Valid models
    for model in ['core', 'core2', 'stickc', 'atom']:
        config = {
            'device_name': 'Test',
            'm5stack_model': model,
            'peripherals': [],
        }
        errors = platform.validate_config(config)
        assert len(errors) == 0
    
    # Invalid model
    invalid_config = {
        'device_name': 'Test',
        'm5stack_model': 'invalid_model',
        'peripherals': [],
    }
    errors = platform.validate_config(invalid_config)
    assert len(errors) > 0
    assert any('model' in err.lower() for err in errors)


def test_m5stack_wifi_validation():
    """Test M5Stack WiFi configuration validation."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    # Valid WiFi config
    valid_config = {
        'device_name': 'Test',
        'wifi': {
            'ssid': 'TestNetwork',
            'password': 'password123',
        },
        'peripherals': [],
    }
    errors = platform.validate_config(valid_config)
    assert len(errors) == 0
    
    # Invalid WiFi config - missing SSID
    invalid_config = {
        'device_name': 'Test',
        'wifi': {
            'password': 'password123',
        },
        'peripherals': [],
    }
    errors = platform.validate_config(invalid_config)
    assert len(errors) > 0
    assert any('ssid' in err.lower() for err in errors)


def test_m5stack_platformio_config_core():
    """Test PlatformIO config generation for M5Stack Core."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'Test',
        'm5stack_model': 'core',
        'peripherals': [{'type': 'display'}],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        platformio_file = output_dir / "platformio.ini"
        content = platformio_file.read_text()
        
        assert 'board = m5stack-core-esp32' in content
        assert 'M5Stack' in content


def test_m5stack_platformio_config_core2():
    """Test PlatformIO config generation for M5Stack Core2."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'Test',
        'm5stack_model': 'core2',
        'peripherals': [{'type': 'display'}],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        platformio_file = output_dir / "platformio.ini"
        content = platformio_file.read_text()
        
        assert 'board = m5stack-core2' in content
        assert 'M5Core2' in content


def test_m5stack_display_initialization():
    """Test M5Stack display initialization in generated code."""
    from accelerapp.platforms import M5StackPlatform
    
    platform = M5StackPlatform()
    
    spec = {
        'device_name': 'Display Test',
        'peripherals': [{'type': 'display'}],
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        result = platform.generate_code(spec, output_dir)
        
        main_file = output_dir / "main.cpp"
        main_content = main_file.read_text()
        
        # Check display initialization
        assert 'M5.Lcd.fillScreen(BLACK)' in main_content
        assert 'M5.Lcd.setTextColor(WHITE)' in main_content
        assert 'M5.Lcd.setTextSize(2)' in main_content
        assert 'M5.Lcd.setCursor' in main_content
        assert 'M5.Lcd.println' in main_content
