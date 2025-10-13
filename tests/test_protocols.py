"""
Tests for hardware protocol support (I2C, SPI, CAN).
"""

import pytest
from accelerapp.hardware import (
    ProtocolType, I2CConfig, SPIConfig, CANConfig,
    ProtocolGenerator, DeviceDriverGenerator
)


def test_protocol_types():
    """Test protocol type enumeration."""
    assert ProtocolType.I2C.value == "i2c"
    assert ProtocolType.SPI.value == "spi"
    assert ProtocolType.CAN.value == "can"


def test_i2c_config():
    """Test I2C configuration."""
    config = I2CConfig(address=0x76, speed=400000)
    assert config.address == 0x76
    assert config.speed == 400000
    assert config.pullup_enabled is True
    
    errors = config.validate()
    assert len(errors) == 0


def test_i2c_config_validation():
    """Test I2C configuration validation."""
    # Invalid address
    config = I2CConfig(address=0xFF, speed=100000)
    errors = config.validate()
    assert len(errors) > 0
    assert any('address' in err.lower() for err in errors)


def test_spi_config():
    """Test SPI configuration."""
    config = SPIConfig(mode=0, speed=1000000, cs_pin=10)
    assert config.mode == 0
    assert config.speed == 1000000
    assert config.cs_pin == 10
    assert config.bit_order == "MSB"
    
    errors = config.validate()
    assert len(errors) == 0


def test_spi_config_validation():
    """Test SPI configuration validation."""
    # Invalid mode
    config = SPIConfig(mode=5, speed=1000000)
    errors = config.validate()
    assert len(errors) > 0
    assert any('mode' in err.lower() for err in errors)


def test_can_config():
    """Test CAN configuration."""
    config = CANConfig(baudrate=500000, tx_pin=5, rx_pin=4)
    assert config.baudrate == 500000
    assert config.tx_pin == 5
    assert config.rx_pin == 4
    assert config.mode == "normal"
    
    errors = config.validate()
    assert len(errors) == 0


def test_can_config_validation():
    """Test CAN configuration validation."""
    # Invalid baudrate
    config = CANConfig(baudrate=999, mode="normal")
    errors = config.validate()
    assert len(errors) > 0
    assert any('baudrate' in err.lower() for err in errors)


def test_i2c_code_generation_arduino():
    """Test I2C code generation for Arduino."""
    config = I2CConfig(address=0x76, speed=100000)
    code = ProtocolGenerator.generate_i2c_code(config, "arduino")
    
    assert "#include <Wire.h>" in code
    assert "0x76" in code
    assert "Wire.begin()" in code
    assert "i2cWrite" in code
    assert "i2cRead" in code


def test_i2c_code_generation_esp32():
    """Test I2C code generation for ESP32."""
    config = I2CConfig(address=0x68, speed=400000, sda_pin=21, scl_pin=22)
    code = ProtocolGenerator.generate_i2c_code(config, "esp32")
    
    assert "#include <Wire.h>" in code
    assert "0x68" in code
    assert "21" in code  # SDA pin
    assert "22" in code  # SCL pin
    assert "400000" in code


def test_i2c_code_generation_stm32():
    """Test I2C code generation for STM32."""
    config = I2CConfig(address=0x3C, speed=100000)
    code = ProtocolGenerator.generate_i2c_code(config, "stm32")
    
    assert "stm32f4xx_hal.h" in code
    assert "I2C_HandleTypeDef" in code
    assert "0x3C" in code


def test_spi_code_generation_arduino():
    """Test SPI code generation for Arduino."""
    config = SPIConfig(mode=0, speed=1000000, cs_pin=10)
    code = ProtocolGenerator.generate_spi_code(config, "arduino")
    
    assert "#include <SPI.h>" in code
    assert "SPI_MODE0" in code
    assert "1000000" in code
    assert "spiTransfer" in code
    assert "spiWrite" in code


def test_spi_code_generation_esp32():
    """Test SPI code generation for ESP32."""
    config = SPIConfig(mode=1, speed=2000000, cs_pin=5)
    code = ProtocolGenerator.generate_spi_code(config, "esp32")
    
    assert "#include <SPI.h>" in code
    assert "SPI_MODE1" in code
    assert "2000000" in code
    assert "VSPI" in code


def test_can_code_generation_esp32():
    """Test CAN code generation for ESP32."""
    config = CANConfig(baudrate=500000, tx_pin=5, rx_pin=4)
    code = ProtocolGenerator.generate_can_code(config, "esp32")
    
    assert "driver/can.h" in code
    assert "500000" in code
    assert "GPIO_NUM_5" in code
    assert "GPIO_NUM_4" in code
    assert "canSend" in code
    assert "canReceive" in code


def test_can_code_generation_stm32():
    """Test CAN code generation for STM32."""
    config = CANConfig(baudrate=250000)
    code = ProtocolGenerator.generate_can_code(config, "stm32")
    
    assert "CAN_HandleTypeDef" in code
    assert "CAN1" in code
    assert "canSend" in code
    assert "canReceive" in code


def test_bme280_driver_generation():
    """Test BME280 sensor driver generation."""
    driver = DeviceDriverGenerator.generate_sensor_driver("bme280", "i2c", "arduino")
    
    assert "BME280" in driver
    assert "readTemperature" in driver
    assert "readHumidity" in driver
    assert "readPressure" in driver


def test_mpu6050_driver_generation():
    """Test MPU6050 sensor driver generation."""
    driver = DeviceDriverGenerator.generate_sensor_driver("mpu6050", "i2c", "esp32")
    
    assert "MPU6050" in driver
    assert "readAccel" in driver
    assert "readGyro" in driver


def test_ina219_driver_generation():
    """Test INA219 sensor driver generation."""
    driver = DeviceDriverGenerator.generate_sensor_driver("ina219", "i2c", "arduino")
    
    assert "INA219" in driver
    assert "readCurrent" in driver
    assert "readBusVoltage" in driver or "readShuntVoltage" in driver
    assert "readPower" in driver


def test_unsupported_sensor():
    """Test handling of unsupported sensor."""
    driver = DeviceDriverGenerator.generate_sensor_driver("unknown_sensor", "i2c", "arduino")
    
    assert "not yet implemented" in driver.lower()


def test_sensor_wrong_protocol():
    """Test sensor driver with wrong protocol."""
    driver = DeviceDriverGenerator.generate_sensor_driver("bme280", "spi", "arduino")
    
    assert "requires" in driver.lower() or "not yet implemented" in driver.lower()
