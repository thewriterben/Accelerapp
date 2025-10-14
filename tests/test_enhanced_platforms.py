"""
Tests for enhanced platform support (STM32, Nordic nRF).
"""

import pytest
from pathlib import Path
import tempfile


def test_stm32f4_platform_import():
    """Test STM32F4 platform can be imported."""
    from accelerapp.platforms.stm32 import STM32F4Platform
    platform = STM32F4Platform()
    assert platform.name == "stm32f4"
    assert platform.series == "F4"


def test_stm32h7_platform_import():
    """Test STM32H7 platform can be imported."""
    from accelerapp.platforms.stm32 import STM32H7Platform
    platform = STM32H7Platform()
    assert platform.name == "stm32h7"
    assert platform.series == "H7"


def test_stm32f4_platform_info():
    """Test STM32F4 platform information."""
    from accelerapp.platforms.stm32 import STM32F4Platform
    platform = STM32F4Platform()
    info = platform.get_platform_info()
    
    assert info["name"] == "stm32f4"
    assert info["series"] == "STM32F4"
    assert info["core"] == "ARM Cortex-M4"
    assert "fpu" in platform.capabilities
    assert "dsp" in platform.capabilities


def test_stm32h7_platform_info():
    """Test STM32H7 platform information."""
    from accelerapp.platforms.stm32 import STM32H7Platform
    platform = STM32H7Platform()
    info = platform.get_platform_info()
    
    assert info["name"] == "stm32h7"
    assert info["series"] == "STM32H7"
    assert info["max_clock"] == 480
    assert "cache" in platform.capabilities
    assert "dual_core" in platform.capabilities


def test_stm32f4_code_generation():
    """Test STM32F4 code generation."""
    from accelerapp.platforms.stm32 import STM32F4Platform
    
    platform = STM32F4Platform()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        spec = {
            "device_name": "TestDevice",
            "peripherals": [
                {"type": "led", "pin": 13},
                {"type": "button", "pin": 2},
            ]
        }
        
        result = platform.generate_code(spec, output_dir)
        
        assert result["status"] == "success"
        assert result["platform"] == "stm32f4"
        assert len(result["files_generated"]) > 0
        
        # Check main file was created
        main_file = output_dir / "main.c"
        assert main_file.exists()
        content = main_file.read_text()
        assert "STM32" in content
        assert "HAL_Init" in content


def test_nrf52_platform_import():
    """Test nRF52 platform can be imported."""
    from accelerapp.platforms.nordic import NRF52Platform
    platform = NRF52Platform()
    assert platform.name == "nrf52"


def test_nrf53_platform_import():
    """Test nRF53 platform can be imported."""
    from accelerapp.platforms.nordic import NRF53Platform
    platform = NRF53Platform()
    assert platform.name == "nrf53"


def test_nrf52_platform_info():
    """Test nRF52 platform information."""
    from accelerapp.platforms.nordic import NRF52Platform
    platform = NRF52Platform()
    info = platform.get_platform_info()
    
    assert info["name"] == "nrf52"
    assert "ble" in platform.capabilities
    assert "nfc" in platform.capabilities
    assert info["mcu_family"] == "ARM Cortex-M4F"


def test_nrf53_platform_info():
    """Test nRF53 platform information."""
    from accelerapp.platforms.nordic import NRF53Platform
    platform = NRF53Platform()
    info = platform.get_platform_info()
    
    assert info["name"] == "nrf53"
    assert "dual_core" in platform.capabilities
    assert "trustzone" in platform.capabilities
    assert "bluetooth_le_audio" in platform.capabilities


def test_nrf52_code_generation():
    """Test nRF52 code generation."""
    from accelerapp.platforms.nordic import NRF52Platform
    
    platform = NRF52Platform()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        spec = {
            "device_name": "NordicDevice",
            "peripherals": [
                {"type": "led", "pin": 13},
                {"type": "ble_peripheral"},
            ]
        }
        
        result = platform.generate_code(spec, output_dir)
        
        assert result["status"] == "success"
        assert result["platform"] == "nrf52"
        assert len(result["files_generated"]) >= 2
        
        # Check main file was created
        main_file = output_dir / "main.c"
        assert main_file.exists()
        content = main_file.read_text()
        assert "nrf52" in content.lower() or "nordic" in content.lower()


def test_platform_factory_enhanced():
    """Test platform factory with enhanced platforms."""
    from accelerapp.platforms import get_platform
    
    # Test STM32 variants
    stm32f4 = get_platform("stm32f4")
    assert stm32f4.name == "stm32f4"
    
    stm32h7 = get_platform("stm32h7")
    assert stm32h7.name == "stm32h7"
    
    # Test Nordic variants
    nrf52 = get_platform("nrf52")
    assert nrf52.name == "nrf52"
    
    nrf53 = get_platform("nrf53")
    assert nrf53.name == "nrf53"


def test_hal_generator():
    """Test STM32 HAL generator."""
    from accelerapp.platforms.stm32.hal_generator import STM32HALGenerator
    
    generator = STM32HALGenerator("F4")
    
    # Test GPIO initialization
    gpio_config = {
        "ports": ["A", "B"],
        "pins": [
            {"port": "A", "pin": 5, "mode": "OUTPUT_PP", "pull": "NOPULL", "speed": "FREQ_LOW"}
        ]
    }
    
    gpio_code = generator.generate_gpio_init(gpio_config)
    assert "GPIO" in gpio_code
    assert "PA5" in gpio_code or "PIN_5" in gpio_code
    
    # Test UART initialization
    uart_config = {
        "instance": "USART2",
        "baudrate": 115200
    }
    
    uart_code = generator.generate_uart_init(uart_config)
    assert "USART2" in uart_code
    assert "115200" in uart_code


def test_ble_stack():
    """Test BLE stack generator."""
    from accelerapp.platforms.nordic.ble_stack import BLEStack
    
    stack = BLEStack("s140")
    
    # Test service generation
    service_config = {
        "name": "heart_rate",
        "uuid": "0x180D",
        "characteristics": [
            {"name": "hr_measurement", "uuid": "0x2A37"}
        ]
    }
    
    service_code = stack.generate_service(service_config)
    assert "heart_rate" in service_code
    assert "0x180D" in service_code
    
    # Test advertising generation
    adv_config = {
        "device_name": "MyDevice",
        "interval": 300,
        "timeout": 180
    }
    
    adv_code = stack.generate_advertising(adv_config)
    assert "advertising" in adv_code.lower()
    assert "300" in adv_code


def test_zephyr_integration():
    """Test Zephyr RTOS integration."""
    from accelerapp.platforms.nordic.zephyr_integration import ZephyrIntegration
    
    integration = ZephyrIntegration("nrf52840dk_nrf52840")
    
    # Test prj.conf generation
    config = {
        "ble_enabled": True,
        "device_name": "TestDevice",
        "logging_enabled": True,
        "gpio_enabled": True
    }
    
    prj_conf = integration.generate_prj_conf(config)
    assert "CONFIG_BT=y" in prj_conf
    assert "CONFIG_GPIO=y" in prj_conf
    
    # Test CMakeLists.txt generation
    cmake_config = {
        "project_name": "test_app",
        "source_files": ["src/custom.c"]
    }
    
    cmake = integration.generate_cmakelists(cmake_config)
    assert "test_app" in cmake
    assert "src/main.c" in cmake


def test_validation_errors():
    """Test platform configuration validation."""
    from accelerapp.platforms.stm32 import STM32F4Platform
    from accelerapp.platforms.nordic import NRF52Platform
    
    # Test STM32 validation
    stm32 = STM32F4Platform()
    errors = stm32.validate_config({})
    assert len(errors) > 0
    assert any("device_name" in e for e in errors)
    
    # Test with valid config
    valid_config = {
        "device_name": "Test",
        "peripherals": [{"type": "led"}]
    }
    errors = stm32.validate_config(valid_config)
    assert len(errors) == 0
    
    # Test nRF52 validation
    nrf52 = NRF52Platform()
    errors = nrf52.validate_config({})
    assert len(errors) > 0


def test_build_configs():
    """Test platform build configurations."""
    from accelerapp.platforms.stm32 import STM32F4Platform, STM32H7Platform
    from accelerapp.platforms.nordic import NRF52Platform
    
    # STM32F4 build config
    stm32f4 = STM32F4Platform()
    config = stm32f4.get_build_config()
    assert config["platform"] == "stm32"
    assert "cortex-m4" in str(config.get("cpu_flags", [])).lower()
    
    # STM32H7 build config
    stm32h7 = STM32H7Platform()
    config = stm32h7.get_build_config()
    assert "cortex-m7" in str(config.get("cpu_flags", [])).lower()
    
    # nRF52 build config
    nrf52 = NRF52Platform()
    config = nrf52.get_build_config()
    assert config["platform"] == "nordicnrf52"
    assert config["softdevice"] == "s140"
