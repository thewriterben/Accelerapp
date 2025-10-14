# Configuration Reference

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

This document describes all configuration options available in Accelerapp hardware specification files.

## Basic Structure

```yaml
device_name: "Device Name"
platform: "arduino"
software_language: "python"
ui_framework: "react"

hardware:
  # Hardware specs

pins:
  # Pin definitions

timing:
  # Timing parameters

peripherals:
  # Peripheral list

communication:
  # Communication settings
```

## Top-Level Options

### device_name
**Type**: String  
**Required**: Yes  
**Description**: Human-readable name for your device

### platform
**Type**: String  
**Required**: Yes  
**Options**: `arduino`, `stm32`, `esp32`  
**Description**: Target hardware platform for firmware

### software_language
**Type**: String  
**Required**: No  
**Default**: `python`  
**Options**: `python`, `cpp`, `javascript`  
**Description**: Language for generated SDK

### ui_framework
**Type**: String  
**Required**: No  
**Default**: `react`  
**Options**: `react`, `vue`, `html`  
**Description**: Framework for generated UI

## Hardware Section

Defines the core hardware specifications:

```yaml
hardware:
  mcu: "ATmega328P"
  clock_speed: "16MHz"
  memory: "32KB"
  wifi: false
```

### mcu
**Type**: String  
**Description**: Microcontroller model

### clock_speed
**Type**: String  
**Description**: System clock speed

### memory
**Type**: String  
**Description**: Available memory

### wifi
**Type**: Boolean  
**Description**: WiFi capability (for ESP32)

## Pins Section

Defines pin assignments:

```yaml
pins:
  LED_PIN: 13
  SENSOR_PIN: "A0"
  BUTTON_PIN: 2
```

Each entry maps a symbolic name to a pin number or identifier.

## Timing Section

Defines timing parameters:

```yaml
timing:
  BAUD_RATE: 9600
  SAMPLE_RATE: 100
  UPDATE_INTERVAL: 1000
  PWM_FREQUENCY: 1000
```

All values are in appropriate units (Hz, ms, etc.)

## Peripherals Section

Defines connected peripherals:

```yaml
peripherals:
  - type: "led"
    pin: 13
    description: "Status LED"
  
  - type: "sensor"
    pin: "A0"
    description: "Temperature sensor"
    sensor_type: "analog"
  
  - type: "motor"
    pin: 3
    description: "DC motor"
```

### Common Peripheral Properties

- **type**: Peripheral type (led, sensor, motor, button, encoder, etc.)
- **pin**: Pin assignment
- **description**: Human-readable description

### Type-Specific Properties

Additional properties vary by peripheral type:

**Sensor**:
- `sensor_type`: analog, digital, i2c, spi

**Motor**:
- `pwm_pin`: PWM control pin
- `dir_pin`: Direction control pin

## Communication Section

Defines communication parameters:

```yaml
communication:
  protocol: "serial"
  baudrate: 9600
  data_format: "json"
  wifi_enabled: false
```

### protocol
**Type**: String  
**Options**: `serial`, `i2c`, `spi`, `wifi`

### baudrate
**Type**: Integer  
**Description**: Communication speed

### data_format
**Type**: String  
**Options**: `text`, `json`, `binary`

## Complete Example

See the `examples/` directory for complete configuration examples.
