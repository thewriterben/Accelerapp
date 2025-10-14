"""
Hardware communication protocols support.
Provides I2C, SPI, and CAN protocol specifications and code generation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProtocolType(Enum):
    """Hardware communication protocol types."""

    I2C = "i2c"
    SPI = "spi"
    CAN = "can"
    UART = "uart"
    USB = "usb"


@dataclass
class I2CConfig:
    """I2C (Inter-Integrated Circuit) protocol configuration."""

    address: int  # 7-bit or 10-bit address
    speed: int = 100000  # Speed in Hz (100kHz standard, 400kHz fast, 1MHz fast-plus)
    sda_pin: Optional[int] = None
    scl_pin: Optional[int] = None
    pullup_enabled: bool = True

    def validate(self) -> List[str]:
        """Validate I2C configuration."""
        errors = []
        if self.address < 0 or self.address > 0x7F:
            errors.append(f"I2C address {self.address} out of range (0x00-0x7F)")
        if self.speed not in [100000, 400000, 1000000, 3400000]:
            errors.append(f"I2C speed {self.speed} not standard (use 100k, 400k, 1M, or 3.4M)")
        return errors


@dataclass
class SPIConfig:
    """SPI (Serial Peripheral Interface) protocol configuration."""

    mode: int = 0  # SPI mode (0-3)
    speed: int = 1000000  # Speed in Hz
    mosi_pin: Optional[int] = None
    miso_pin: Optional[int] = None
    sclk_pin: Optional[int] = None
    cs_pin: Optional[int] = None
    bit_order: str = "MSB"  # MSB or LSB first

    def validate(self) -> List[str]:
        """Validate SPI configuration."""
        errors = []
        if self.mode not in [0, 1, 2, 3]:
            errors.append(f"SPI mode {self.mode} invalid (must be 0-3)")
        if self.bit_order not in ["MSB", "LSB"]:
            errors.append(f"Bit order {self.bit_order} invalid (must be MSB or LSB)")
        return errors


@dataclass
class CANConfig:
    """CAN (Controller Area Network) bus configuration."""

    baudrate: int = 500000  # Common: 125k, 250k, 500k, 1M
    tx_pin: Optional[int] = None
    rx_pin: Optional[int] = None
    mode: str = "normal"  # normal, loopback, silent, silent-loopback

    def validate(self) -> List[str]:
        """Validate CAN configuration."""
        errors = []
        if self.baudrate not in [125000, 250000, 500000, 1000000]:
            errors.append(f"CAN baudrate {self.baudrate} not standard")
        if self.mode not in ["normal", "loopback", "silent", "silent-loopback"]:
            errors.append(f"CAN mode {self.mode} invalid")
        return errors


class ProtocolGenerator:
    """Generate code for hardware communication protocols."""

    @staticmethod
    def generate_i2c_code(config: I2CConfig, platform: str) -> str:
        """
        Generate I2C initialization and communication code.

        Args:
            config: I2C configuration
            platform: Target platform (arduino, esp32, stm32, etc.)

        Returns:
            Generated code string
        """
        if platform == "arduino":
            return ProtocolGenerator._generate_arduino_i2c(config)
        elif platform == "esp32":
            return ProtocolGenerator._generate_esp32_i2c(config)
        elif platform == "stm32":
            return ProtocolGenerator._generate_stm32_i2c(config)
        else:
            return f"// I2C not yet supported for {platform}"

    @staticmethod
    def _generate_arduino_i2c(config: I2CConfig) -> str:
        """Generate Arduino I2C code."""
        code = f"""
// I2C Configuration
#include <Wire.h>

#define I2C_ADDRESS 0x{config.address:02X}
#define I2C_SPEED {config.speed}

void setupI2C() {{
    Wire.begin();
    Wire.setClock(I2C_SPEED);
}}

// Write data to I2C device
bool i2cWrite(uint8_t reg, uint8_t* data, size_t len) {{
    Wire.beginTransmission(I2C_ADDRESS);
    Wire.write(reg);
    for(size_t i = 0; i < len; i++) {{
        Wire.write(data[i]);
    }}
    return Wire.endTransmission() == 0;
}}

// Read data from I2C device
bool i2cRead(uint8_t reg, uint8_t* data, size_t len) {{
    Wire.beginTransmission(I2C_ADDRESS);
    Wire.write(reg);
    if(Wire.endTransmission(false) != 0) return false;
    
    Wire.requestFrom(I2C_ADDRESS, len);
    for(size_t i = 0; i < len && Wire.available(); i++) {{
        data[i] = Wire.read();
    }}
    return true;
}}
"""
        return code.strip()

    @staticmethod
    def _generate_esp32_i2c(config: I2CConfig) -> str:
        """Generate ESP32 I2C code."""
        sda = config.sda_pin if config.sda_pin else 21
        scl = config.scl_pin if config.scl_pin else 22

        code = f"""
// I2C Configuration for ESP32
#include <Wire.h>

#define I2C_ADDRESS 0x{config.address:02X}
#define I2C_SDA {sda}
#define I2C_SCL {scl}
#define I2C_SPEED {config.speed}

void setupI2C() {{
    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(I2C_SPEED);
}}

// Write data to I2C device
bool i2cWrite(uint8_t reg, uint8_t* data, size_t len) {{
    Wire.beginTransmission(I2C_ADDRESS);
    Wire.write(reg);
    Wire.write(data, len);
    return Wire.endTransmission() == 0;
}}

// Read data from I2C device
bool i2cRead(uint8_t reg, uint8_t* data, size_t len) {{
    Wire.beginTransmission(I2C_ADDRESS);
    Wire.write(reg);
    if(Wire.endTransmission(false) != 0) return false;
    
    size_t received = Wire.requestFrom((uint8_t)I2C_ADDRESS, len);
    for(size_t i = 0; i < received; i++) {{
        data[i] = Wire.read();
    }}
    return received == len;
}}
"""
        return code.strip()

    @staticmethod
    def _generate_stm32_i2c(config: I2CConfig) -> str:
        """Generate STM32 I2C code."""
        code = f"""
// I2C Configuration for STM32
#include "stm32f4xx_hal.h"

#define I2C_ADDRESS (0x{config.address:02X} << 1)

I2C_HandleTypeDef hi2c1;

void setupI2C() {{
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = {config.speed};
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}}

// Write data to I2C device
HAL_StatusTypeDef i2cWrite(uint8_t reg, uint8_t* data, uint16_t len) {{
    uint8_t buffer[len + 1];
    buffer[0] = reg;
    memcpy(&buffer[1], data, len);
    return HAL_I2C_Master_Transmit(&hi2c1, I2C_ADDRESS, buffer, len + 1, HAL_MAX_DELAY);
}}

// Read data from I2C device
HAL_StatusTypeDef i2cRead(uint8_t reg, uint8_t* data, uint16_t len) {{
    HAL_StatusTypeDef status = HAL_I2C_Master_Transmit(&hi2c1, I2C_ADDRESS, &reg, 1, HAL_MAX_DELAY);
    if(status != HAL_OK) return status;
    return HAL_I2C_Master_Receive(&hi2c1, I2C_ADDRESS, data, len, HAL_MAX_DELAY);
}}
"""
        return code.strip()

    @staticmethod
    def generate_spi_code(config: SPIConfig, platform: str) -> str:
        """
        Generate SPI initialization and communication code.

        Args:
            config: SPI configuration
            platform: Target platform

        Returns:
            Generated code string
        """
        if platform == "arduino":
            return ProtocolGenerator._generate_arduino_spi(config)
        elif platform == "esp32":
            return ProtocolGenerator._generate_esp32_spi(config)
        elif platform == "stm32":
            return ProtocolGenerator._generate_stm32_spi(config)
        else:
            return f"// SPI not yet supported for {platform}"

    @staticmethod
    def _generate_arduino_spi(config: SPIConfig) -> str:
        """Generate Arduino SPI code."""
        cs_pin = config.cs_pin if config.cs_pin else 10

        code = f"""
// SPI Configuration
#include <SPI.h>

#define SPI_CS_PIN {cs_pin}
#define SPI_SPEED {config.speed}

SPISettings spiSettings(SPI_SPEED, {"MSBFIRST" if config.bit_order == "MSB" else "LSBFIRST"}, SPI_MODE{config.mode});

void setupSPI() {{
    pinMode(SPI_CS_PIN, OUTPUT);
    digitalWrite(SPI_CS_PIN, HIGH);
    SPI.begin();
}}

// Transfer data via SPI
void spiTransfer(uint8_t* txData, uint8_t* rxData, size_t len) {{
    digitalWrite(SPI_CS_PIN, LOW);
    SPI.beginTransaction(spiSettings);
    
    for(size_t i = 0; i < len; i++) {{
        rxData[i] = SPI.transfer(txData[i]);
    }}
    
    SPI.endTransaction();
    digitalWrite(SPI_CS_PIN, HIGH);
}}

// Write data via SPI
void spiWrite(uint8_t* data, size_t len) {{
    digitalWrite(SPI_CS_PIN, LOW);
    SPI.beginTransaction(spiSettings);
    
    for(size_t i = 0; i < len; i++) {{
        SPI.transfer(data[i]);
    }}
    
    SPI.endTransaction();
    digitalWrite(SPI_CS_PIN, HIGH);
}}
"""
        return code.strip()

    @staticmethod
    def _generate_esp32_spi(config: SPIConfig) -> str:
        """Generate ESP32 SPI code."""
        code = f"""
// SPI Configuration for ESP32
#include <SPI.h>

#define SPI_CS_PIN {config.cs_pin if config.cs_pin else 5}
#define SPI_SPEED {config.speed}

SPIClass spi(VSPI);
SPISettings spiSettings(SPI_SPEED, {"MSBFIRST" if config.bit_order == "MSB" else "LSBFIRST"}, SPI_MODE{config.mode});

void setupSPI() {{
    pinMode(SPI_CS_PIN, OUTPUT);
    digitalWrite(SPI_CS_PIN, HIGH);
    spi.begin();
}}

// Transfer data via SPI
void spiTransfer(uint8_t* txData, uint8_t* rxData, size_t len) {{
    digitalWrite(SPI_CS_PIN, LOW);
    spi.beginTransaction(spiSettings);
    spi.transferBytes(txData, rxData, len);
    spi.endTransaction();
    digitalWrite(SPI_CS_PIN, HIGH);
}}

// Write data via SPI
void spiWrite(uint8_t* data, size_t len) {{
    digitalWrite(SPI_CS_PIN, LOW);
    spi.beginTransaction(spiSettings);
    spi.writeBytes(data, len);
    spi.endTransaction();
    digitalWrite(SPI_CS_PIN, HIGH);
}}
"""
        return code.strip()

    @staticmethod
    def _generate_stm32_spi(config: SPIConfig) -> str:
        """Generate STM32 SPI code."""
        code = f"""
// SPI Configuration for STM32
#include "stm32f4xx_hal.h"

SPI_HandleTypeDef hspi1;

void setupSPI() {{
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = {"SPI_POLARITY_LOW" if config.mode in [0, 1] else "SPI_POLARITY_HIGH"};
    hspi1.Init.CLKPhase = {"SPI_PHASE_1EDGE" if config.mode in [0, 2] else "SPI_PHASE_2EDGE"};
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
    hspi1.Init.FirstBit = {"SPI_FIRSTBIT_MSB" if config.bit_order == "MSB" else "SPI_FIRSTBIT_LSB"};
    HAL_SPI_Init(&hspi1);
}}

// Transfer data via SPI
HAL_StatusTypeDef spiTransfer(uint8_t* txData, uint8_t* rxData, uint16_t len) {{
    return HAL_SPI_TransmitReceive(&hspi1, txData, rxData, len, HAL_MAX_DELAY);
}}

// Write data via SPI
HAL_StatusTypeDef spiWrite(uint8_t* data, uint16_t len) {{
    return HAL_SPI_Transmit(&hspi1, data, len, HAL_MAX_DELAY);
}}
"""
        return code.strip()

    @staticmethod
    def generate_can_code(config: CANConfig, platform: str) -> str:
        """
        Generate CAN bus initialization and communication code.

        Args:
            config: CAN configuration
            platform: Target platform

        Returns:
            Generated code string
        """
        if platform == "esp32":
            return ProtocolGenerator._generate_esp32_can(config)
        elif platform == "stm32":
            return ProtocolGenerator._generate_stm32_can(config)
        else:
            return f"// CAN not yet supported for {platform}"

    @staticmethod
    def _generate_esp32_can(config: CANConfig) -> str:
        """Generate ESP32 CAN code."""
        tx_pin = config.tx_pin if config.tx_pin else 5
        rx_pin = config.rx_pin if config.rx_pin else 4

        code = f"""
// CAN Configuration for ESP32
#include <driver/can.h>

#define CAN_TX_PIN GPIO_NUM_{tx_pin}
#define CAN_RX_PIN GPIO_NUM_{rx_pin}
#define CAN_BAUDRATE {config.baudrate}

void setupCAN() {{
    can_general_config_t g_config = CAN_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, CAN_MODE_NORMAL);
    can_timing_config_t t_config;
    
    // Set timing based on baudrate
    switch(CAN_BAUDRATE) {{
        case 125000:  t_config = CAN_TIMING_CONFIG_125KBITS(); break;
        case 250000:  t_config = CAN_TIMING_CONFIG_250KBITS(); break;
        case 500000:  t_config = CAN_TIMING_CONFIG_500KBITS(); break;
        case 1000000: t_config = CAN_TIMING_CONFIG_1MBITS(); break;
        default:      t_config = CAN_TIMING_CONFIG_500KBITS();
    }}
    
    can_filter_config_t f_config = CAN_FILTER_CONFIG_ACCEPT_ALL();
    
    // Install CAN driver
    can_driver_install(&g_config, &t_config, &f_config);
    can_start();
}}

// Send CAN message
esp_err_t canSend(uint32_t id, uint8_t* data, uint8_t len, bool extended) {{
    can_message_t message;
    message.identifier = id;
    message.data_length_code = len;
    message.flags = extended ? CAN_MSG_FLAG_EXTD : CAN_MSG_FLAG_NONE;
    memcpy(message.data, data, len);
    
    return can_transmit(&message, pdMS_TO_TICKS(1000));
}}

// Receive CAN message
esp_err_t canReceive(can_message_t* message, uint32_t timeout_ms) {{
    return can_receive(message, pdMS_TO_TICKS(timeout_ms));
}}
"""
        return code.strip()

    @staticmethod
    def _generate_stm32_can(config: CANConfig) -> str:
        """Generate STM32 CAN code."""
        code = f"""
// CAN Configuration for STM32
#include "stm32f4xx_hal.h"

CAN_HandleTypeDef hcan1;

void setupCAN() {{
    hcan1.Instance = CAN1;
    hcan1.Init.Prescaler = 16;  // Adjust based on clock and desired baudrate
    hcan1.Init.Mode = CAN_MODE_NORMAL;
    hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;
    hcan1.Init.TimeSeg1 = CAN_BS1_13TQ;
    hcan1.Init.TimeSeg2 = CAN_BS2_2TQ;
    hcan1.Init.TimeTriggeredMode = DISABLE;
    hcan1.Init.AutoBusOff = DISABLE;
    hcan1.Init.AutoWakeUp = DISABLE;
    hcan1.Init.AutoRetransmission = ENABLE;
    hcan1.Init.ReceiveFifoLocked = DISABLE;
    hcan1.Init.TransmitFifoPriority = DISABLE;
    
    HAL_CAN_Init(&hcan1);
    
    // Configure filter to accept all messages
    CAN_FilterTypeDef filter;
    filter.FilterBank = 0;
    filter.FilterMode = CAN_FILTERMODE_IDMASK;
    filter.FilterScale = CAN_FILTERSCALE_32BIT;
    filter.FilterIdHigh = 0x0000;
    filter.FilterIdLow = 0x0000;
    filter.FilterMaskIdHigh = 0x0000;
    filter.FilterMaskIdLow = 0x0000;
    filter.FilterFIFOAssignment = CAN_RX_FIFO0;
    filter.FilterActivation = ENABLE;
    
    HAL_CAN_ConfigFilter(&hcan1, &filter);
    HAL_CAN_Start(&hcan1);
    HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);
}}

// Send CAN message
HAL_StatusTypeDef canSend(uint32_t id, uint8_t* data, uint8_t len, bool extended) {{
    CAN_TxHeaderTypeDef header;
    header.StdId = extended ? 0 : id;
    header.ExtId = extended ? id : 0;
    header.IDE = extended ? CAN_ID_EXT : CAN_ID_STD;
    header.RTR = CAN_RTR_DATA;
    header.DLC = len;
    header.TransmitGlobalTime = DISABLE;
    
    uint32_t mailbox;
    return HAL_CAN_AddTxMessage(&hcan1, &header, data, &mailbox);
}}

// Receive CAN message
HAL_StatusTypeDef canReceive(uint32_t* id, uint8_t* data, uint8_t* len, bool* extended) {{
    CAN_RxHeaderTypeDef header;
    HAL_StatusTypeDef status = HAL_CAN_GetRxMessage(&hcan1, CAN_RX_FIFO0, &header, data);
    
    if(status == HAL_OK) {{
        *id = (header.IDE == CAN_ID_EXT) ? header.ExtId : header.StdId;
        *len = header.DLC;
        *extended = (header.IDE == CAN_ID_EXT);
    }}
    
    return status;
}}
"""
        return code.strip()


class DeviceDriverGenerator:
    """Generate device drivers for common hardware components."""

    @staticmethod
    def generate_sensor_driver(sensor_type: str, protocol: str, platform: str) -> str:
        """
        Generate device driver for common sensors.

        Args:
            sensor_type: Type of sensor (e.g., 'bme280', 'mpu6050', 'ina219')
            protocol: Communication protocol (i2c, spi)
            platform: Target platform

        Returns:
            Generated driver code
        """
        if sensor_type.lower() == "bme280":
            return DeviceDriverGenerator._generate_bme280_driver(protocol, platform)
        elif sensor_type.lower() == "mpu6050":
            return DeviceDriverGenerator._generate_mpu6050_driver(protocol, platform)
        elif sensor_type.lower() == "ina219":
            return DeviceDriverGenerator._generate_ina219_driver(protocol, platform)
        else:
            return f"// Driver for {sensor_type} not yet implemented"

    @staticmethod
    def _generate_bme280_driver(protocol: str, platform: str) -> str:
        """Generate BME280 temperature/humidity/pressure sensor driver."""
        if protocol.lower() != "i2c":
            return "// BME280 driver requires I2C protocol"

        code = """
// BME280 Temperature/Humidity/Pressure Sensor Driver
#define BME280_I2C_ADDR 0x76

// BME280 registers
#define BME280_REG_TEMP_MSB   0xFA
#define BME280_REG_PRESS_MSB  0xF7
#define BME280_REG_HUM_MSB    0xFD
#define BME280_REG_CTRL_MEAS  0xF4
#define BME280_REG_CONFIG     0xF5
#define BME280_REG_CTRL_HUM   0xF2

class BME280 {
private:
    int32_t t_fine;
    
public:
    bool begin() {
        // Configure sensor
        uint8_t ctrl_hum = 0x01;  // Humidity oversampling x1
        i2cWrite(BME280_REG_CTRL_HUM, &ctrl_hum, 1);
        
        uint8_t ctrl_meas = 0x27; // Temp/Press oversampling x1, normal mode
        i2cWrite(BME280_REG_CTRL_MEAS, &ctrl_meas, 1);
        
        uint8_t config = 0xA0;    // Standby 1000ms, filter off
        i2cWrite(BME280_REG_CONFIG, &config, 1);
        
        return true;
    }
    
    float readTemperature() {
        uint8_t data[3];
        i2cRead(BME280_REG_TEMP_MSB, data, 3);
        int32_t adc_T = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
        
        // Simplified temperature calculation (requires calibration data)
        return adc_T / 100.0;
    }
    
    float readHumidity() {
        uint8_t data[2];
        i2cRead(BME280_REG_HUM_MSB, data, 2);
        int32_t adc_H = (data[0] << 8) | data[1];
        
        // Simplified humidity calculation (requires calibration data)
        return adc_H / 1024.0;
    }
    
    float readPressure() {
        uint8_t data[3];
        i2cRead(BME280_REG_PRESS_MSB, data, 3);
        int32_t adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
        
        // Simplified pressure calculation (requires calibration data)
        return adc_P / 256.0;
    }
};
"""
        return code.strip()

    @staticmethod
    def _generate_mpu6050_driver(protocol: str, platform: str) -> str:
        """Generate MPU6050 accelerometer/gyroscope driver."""
        if protocol.lower() != "i2c":
            return "// MPU6050 driver requires I2C protocol"

        code = """
// MPU6050 Accelerometer/Gyroscope Driver
#define MPU6050_I2C_ADDR 0x68

// MPU6050 registers
#define MPU6050_REG_PWR_MGMT_1  0x6B
#define MPU6050_REG_ACCEL_XOUT  0x3B
#define MPU6050_REG_GYRO_XOUT   0x43

class MPU6050 {
public:
    bool begin() {
        // Wake up the MPU6050
        uint8_t pwr_mgmt = 0x00;
        return i2cWrite(MPU6050_REG_PWR_MGMT_1, &pwr_mgmt, 1);
    }
    
    void readAccel(float* x, float* y, float* z) {
        uint8_t data[6];
        i2cRead(MPU6050_REG_ACCEL_XOUT, data, 6);
        
        int16_t ax = (data[0] << 8) | data[1];
        int16_t ay = (data[2] << 8) | data[3];
        int16_t az = (data[4] << 8) | data[5];
        
        // Convert to g (assuming ±2g range)
        *x = ax / 16384.0;
        *y = ay / 16384.0;
        *z = az / 16384.0;
    }
    
    void readGyro(float* x, float* y, float* z) {
        uint8_t data[6];
        i2cRead(MPU6050_REG_GYRO_XOUT, data, 6);
        
        int16_t gx = (data[0] << 8) | data[1];
        int16_t gy = (data[2] << 8) | data[3];
        int16_t gz = (data[4] << 8) | data[5];
        
        // Convert to deg/s (assuming ±250°/s range)
        *x = gx / 131.0;
        *y = gy / 131.0;
        *z = gz / 131.0;
    }
};
"""
        return code.strip()

    @staticmethod
    def _generate_ina219_driver(protocol: str, platform: str) -> str:
        """Generate INA219 current/voltage sensor driver."""
        if protocol.lower() != "i2c":
            return "// INA219 driver requires I2C protocol"

        code = """
// INA219 Current/Voltage Sensor Driver
#define INA219_I2C_ADDR 0x40

// INA219 registers
#define INA219_REG_CONFIG      0x00
#define INA219_REG_SHUNT_V     0x01
#define INA219_REG_BUS_V       0x02
#define INA219_REG_POWER       0x03
#define INA219_REG_CURRENT     0x04
#define INA219_REG_CALIBRATION 0x05

class INA219 {
private:
    float currentLSB;
    
public:
    bool begin() {
        // Configure for 16V, 400mA range
        uint8_t config[2] = {0x19, 0x9F};
        i2cWrite(INA219_REG_CONFIG, config, 2);
        
        // Set calibration
        uint8_t cal[2] = {0x10, 0x00};
        i2cWrite(INA219_REG_CALIBRATION, cal, 2);
        
        currentLSB = 0.1;  // 0.1mA per bit
        return true;
    }
    
    float readBusVoltage() {
        uint8_t data[2];
        i2cRead(INA219_REG_BUS_V, data, 2);
        int16_t value = (data[0] << 8) | data[1];
        return (value >> 3) * 0.004;  // LSB = 4mV
    }
    
    float readShuntVoltage() {
        uint8_t data[2];
        i2cRead(INA219_REG_SHUNT_V, data, 2);
        int16_t value = (data[0] << 8) | data[1];
        return value * 0.01;  // LSB = 10uV
    }
    
    float readCurrent() {
        uint8_t data[2];
        i2cRead(INA219_REG_CURRENT, data, 2);
        int16_t value = (data[0] << 8) | data[1];
        return value * currentLSB;
    }
    
    float readPower() {
        uint8_t data[2];
        i2cRead(INA219_REG_POWER, data, 2);
        int16_t value = (data[0] << 8) | data[1];
        return value * currentLSB * 20;
    }
};
"""
        return code.strip()
