# M5Stack Integration Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

## Overview

This guide covers the integration of M5Stack platform support in Accelerapp. M5Stack is an ESP32-based modular development platform with built-in display, buttons, and expandable modules, making it ideal for rapid prototyping and IoT applications.

## What is M5Stack?

M5Stack is a modular, stackable development platform built around the ESP32 microcontroller. It features:

- **ESP32 Core**: Dual-core Xtensa LX6 processor at up to 240MHz
- **Built-in Display**: 320x240 pixel TFT LCD (ILI9341 driver)
- **Physical Buttons**: Three programmable buttons (A, B, C)
- **Built-in Speaker**: For audio feedback and alerts
- **I2C Grove Ports**: For easy sensor and module connections
- **SD Card Slot**: For data logging and storage
- **Battery Support**: Built-in battery management
- **Modular Design**: Stackable modules for expanded functionality

## Supported M5Stack Models

Accelerapp supports the following M5Stack variants:

| Model | Description | Display | Special Features |
|-------|-------------|---------|------------------|
| **Core** | Standard M5Stack | 320x240 TFT | 3 buttons, speaker, battery |
| **Core2** | Next generation | 320x240 Touch | Touch screen, improved audio |
| **StickC** | Compact version | 80x160 TFT | Ultra-portable, built-in IMU |
| **StickC Plus** | Enhanced StickC | 135x240 TFT | Larger screen, better battery |
| **Atom** | Minimal version | 5x5 RGB LED | Tiny form factor, Grove port |
| **Stamp** | Production module | None | Stamp-size, no display |

## Getting Started

### Prerequisites

1. **Hardware**:
   - M5Stack device (Core, Core2, StickC, etc.)
   - USB-C cable for programming
   - Computer with USB port

2. **Software**:
   - Accelerapp installed
   - PlatformIO or Arduino IDE
   - M5Stack library

### Installation

#### Using PlatformIO (Recommended)

```bash
# Install PlatformIO
pip install platformio

# M5Stack library will be auto-installed by generated code
```

#### Using Arduino IDE

1. Install Arduino IDE
2. Add ESP32 board support: `https://dl.espressif.com/dl/package_esp32_index.json`
3. Install M5Stack library from Library Manager

## Basic Usage

### 1. Create Configuration File

Create a YAML file describing your M5Stack project:

```yaml
# my_m5stack_project.yaml
device_name: "My M5Stack Device"
platform: "m5stack"
m5stack_model: "core"

peripherals:
  - type: "display"
    description: "Built-in TFT display"
  - type: "button"
    pin: 39
    name: "Button A"
```

### 2. Generate Firmware

Use Accelerapp to generate firmware:

```bash
accelerapp generate firmware my_m5stack_project.yaml --output ./output
```

This generates:
- `main.cpp` - Main firmware code
- `config.h` - Configuration header
- `platformio.ini` - PlatformIO configuration
- `wifi_config.h` - WiFi settings (if WiFi enabled)

### 3. Build and Upload

#### Using PlatformIO:

```bash
cd output
pio run --target upload
```

#### Using Arduino IDE:

1. Open `main.cpp` in Arduino IDE
2. Select board: "M5Stack-Core-ESP32"
3. Select port
4. Click Upload

## Hardware Specifications

### M5Stack Core

#### Pin Assignments

| Function | GPIO Pin | Notes |
|----------|----------|-------|
| Button A | 39 | Left button, INPUT_PULLUP |
| Button B | 38 | Middle button, INPUT_PULLUP |
| Button C | 37 | Right button, INPUT_PULLUP |
| Speaker | 25 | PWM output for audio |
| I2C SDA | 21 | Grove port I2C data |
| I2C SCL | 22 | Grove port I2C clock |
| TFT DC | 27 | Display data/command |
| TFT CS | 14 | Display chip select |
| TFT MOSI | 23 | SPI data out |
| TFT CLK | 18 | SPI clock |
| SD CS | 4 | SD card chip select |

#### Display Specifications

- **Resolution**: 320x240 pixels
- **Driver**: ILI9341
- **Interface**: SPI
- **Colors**: 16-bit color (65K colors)
- **Backlight**: GPIO 32 (PWM dimmable)

### M5Stack Core2

Key differences from Core:
- **Touch Screen**: FT6336U capacitive touch
- **Vibration Motor**: GPIO 4
- **Green LED**: GPIO 10
- **I2S Audio**: Enhanced audio capabilities
- **RTC**: BM8563 real-time clock

## Example Projects

### Example 1: Basic Display and Buttons

```yaml
# examples/m5stack_basic.yaml
device_name: "M5Stack Basic Demo"
platform: "m5stack"
m5stack_model: "core"

peripherals:
  - type: "display"
  - type: "button"
    pin: 39
  - type: "button"
    pin: 38
  - type: "button"
    pin: 37
  - type: "speaker"
    pin: 25
```

### Example 2: WiFi Sensor Hub

```yaml
# examples/m5stack_wifi_sensor.yaml
device_name: "M5Stack WiFi Sensor Hub"
platform: "m5stack"
m5stack_model: "core"

wifi:
  ssid: "YourNetworkName"
  password: "YourPassword"

peripherals:
  - type: "display"
  - type: "sensor"
    pin: 36
  - type: "wifi_module"
```

### Example 3: IoT Dashboard

See `examples/m5stack_iot_dashboard.yaml` for a complete IoT monitoring dashboard configuration.

### Example 4: Remote Control

See `examples/m5stack_remote_control.yaml` for a WiFi-based remote control implementation.

## WiFi Configuration

M5Stack supports WiFi connectivity for IoT applications:

```yaml
wifi:
  ssid: "YourNetworkSSID"
  password: "YourPassword"
```

Generated code includes:
- WiFi connection management
- Connection status display
- Automatic reconnection
- IP address display

## Display Programming

The generated code uses the M5Stack library for display control:

```cpp
// Initialize display
M5.begin();
M5.Lcd.fillScreen(BLACK);
M5.Lcd.setTextColor(WHITE);
M5.Lcd.setTextSize(2);

// Draw text
M5.Lcd.setCursor(10, 10);
M5.Lcd.println("Hello M5Stack!");

// Draw graphics
M5.Lcd.drawLine(0, 0, 320, 240, BLUE);
M5.Lcd.fillCircle(160, 120, 50, RED);
```

## Button Handling

Buttons are handled through the M5Stack library:

```cpp
void loop() {
    M5.update();  // Update button states
    
    if (M5.BtnA.wasPressed()) {
        // Button A pressed
    }
    if (M5.BtnB.wasPressed()) {
        // Button B pressed
    }
    if (M5.BtnC.wasPressed()) {
        // Button C pressed
    }
}
```

## Sensor Integration

### I2C Sensors (Grove Port)

M5Stack's Grove port makes sensor integration simple:

```yaml
peripherals:
  - type: "temperature"
    address: 0x76  # I2C address
    description: "BME280 temperature sensor"
```

Common I2C sensors:
- **BME280**: Temperature, humidity, pressure
- **MPU6886**: Accelerometer, gyroscope (built-in on some models)
- **BMP280**: Barometric pressure

### Analog Sensors

Connect analog sensors to available GPIO pins:

```yaml
peripherals:
  - type: "sensor"
    pin: 36
    description: "Analog light sensor"
```

## Power Management

M5Stack includes battery management:

```cpp
// Check battery level
int batteryLevel = M5.Power.getBatteryLevel();

// Check charging status
bool isCharging = M5.Power.isCharging();

// Power off
M5.Power.powerOFF();
```

## SD Card Support

Access SD card for data logging:

```cpp
#include <SD.h>

void setup() {
    SD.begin(4);  // CS pin 4
    
    File file = SD.open("/data.txt", FILE_WRITE);
    file.println("Sensor data");
    file.close();
}
```

## Troubleshooting

### Common Issues

#### Display Not Working
- **Check**: M5Stack library installed
- **Solution**: Install via PlatformIO or Arduino Library Manager

#### Buttons Not Responding
- **Check**: `M5.update()` called in loop
- **Solution**: Add `M5.update()` at start of loop function

#### WiFi Connection Fails
- **Check**: SSID and password in `wifi_config.h`
- **Solution**: Update credentials and rebuild

#### Upload Fails
- **Check**: Correct board selected
- **Solution**: Select "M5Stack-Core-ESP32" or appropriate board

### Serial Debugging

Enable serial debugging:

```cpp
Serial.begin(115200);
Serial.println("Debug message");
```

Monitor with PlatformIO:
```bash
pio device monitor -b 115200
```

## Advanced Features

### Modular Extensions

M5Stack supports stackable modules:
- **GPS Module**: Location tracking
- **LoRa Module**: Long-range communication
- **ENV Sensor**: Environmental monitoring
- **Camera Module**: Image capture
- **Faces Module**: Keyboard, joystick input

### MQTT Integration

For IoT projects with MQTT:

```yaml
communication:
  protocol: "wifi"
  mqtt_broker: "mqtt.example.com"
  mqtt_port: 1883
```

### Web Server

Host a web server on M5Stack:

```cpp
#include <WebServer.h>

WebServer server(80);

void handleRoot() {
    server.send(200, "text/html", "<h1>M5Stack Web Server</h1>");
}

void setup() {
    server.on("/", handleRoot);
    server.begin();
}
```

## Best Practices

1. **Power Management**
   - Use deep sleep for battery operation
   - Dim display when possible
   - Monitor battery level

2. **Display Updates**
   - Minimize full screen refreshes
   - Update only changed areas
   - Use double buffering for smooth animations

3. **Button Handling**
   - Always call `M5.update()` in loop
   - Use `wasPressed()` for single events
   - Use `isPressed()` for continuous actions

4. **WiFi Usage**
   - Check connection before transmitting
   - Implement reconnection logic
   - Use WiFi sleep modes when idle

5. **Code Organization**
   - Separate display logic from business logic
   - Use state machines for complex UIs
   - Keep loop() function responsive

## Resources

### Official Documentation
- [M5Stack Official Site](https://m5stack.com/)
- [M5Stack Docs](https://docs.m5stack.com/)
- [M5Stack GitHub](https://github.com/m5stack/M5Stack)

### Community
- [M5Stack Community Forum](https://community.m5stack.com/)
- [M5Stack Discord](https://discord.gg/m5stack)

### Libraries
- [M5Stack Arduino Library](https://github.com/m5stack/M5Stack)
- [M5Core2 Library](https://github.com/m5stack/M5Core2)
- [M5StickC Library](https://github.com/m5stack/M5StickC)

## Support

For issues with M5Stack platform support in Accelerapp:

1. Check this documentation
2. Review example configurations
3. Check generated code for errors
4. Submit issues on GitHub: [Accelerapp Issues](https://github.com/thewriterben/Accelerapp/issues)

## Version History

- **1.0.0** (2025-10-14): Initial M5Stack platform support
  - Basic M5Stack Core support
  - Display and button integration
  - WiFi connectivity
  - Example configurations
  - PlatformIO integration

## Next Steps

- Explore example configurations in `examples/m5stack_*.yaml`
- Read the [Platform Abstraction Guide](../src/accelerapp/platforms/README.md)
- Check out [ESP32 platform documentation](../ENHANCED_HARDWARE_SUPPORT.md) for underlying ESP32 features
- Join the Accelerapp community for support
