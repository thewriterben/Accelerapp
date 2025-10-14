# Complete Workflow Example

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

This document demonstrates a complete end-to-end workflow using Accelerapp.

## Scenario: Building a Smart Temperature Monitor

Let's build a complete temperature monitoring system from scratch.

### Step 1: Define Hardware Requirements

We want to build a system that:
- Reads temperature from an analog sensor
- Displays status on an LED
- Communicates via serial
- Has a web-based monitoring interface
- Uses ESP32 for WiFi capability

### Step 2: Create Configuration

```bash
accelerapp init temp_monitor.yaml
```

Edit `temp_monitor.yaml`:

```yaml
device_name: "Smart Temperature Monitor"
platform: "esp32"
software_language: "python"
ui_framework: "react"

hardware:
  mcu: "ESP32"
  clock_speed: "240MHz"
  memory: "520KB"
  wifi: true

pins:
  TEMP_SENSOR: 34
  STATUS_LED: 2
  ALERT_LED: 4

timing:
  BAUD_RATE: 115200
  SAMPLE_RATE: 1000
  UPDATE_INTERVAL: 5000
  ALERT_THRESHOLD: 30

peripherals:
  - type: "sensor"
    pin: 34
    description: "Analog temperature sensor"
    sensor_type: "analog"
  
  - type: "led"
    pin: 2
    description: "Status indicator LED"
  
  - type: "led"
    pin: 4
    description: "High temperature alert LED"

communication:
  protocol: "serial"
  baudrate: 115200
  data_format: "json"
  wifi_enabled: true
```

### Step 3: Generate Complete System

```bash
accelerapp generate temp_monitor.yaml --output ./smart_temp_monitor
```

Output:
```
Loading configuration from: temp_monitor.yaml
Generating complete stack: firmware, software, and UI...

✓ Generation complete!
  firmware: ./smart_temp_monitor/firmware
  software: ./smart_temp_monitor/software
  ui: ./smart_temp_monitor/ui
```

### Step 4: Review Generated Files

```bash
tree smart_temp_monitor/
```

```
smart_temp_monitor/
├── firmware/
│   ├── main.c                 # ESP32 main program
│   ├── config.h              # Pin and timing definitions
│   ├── sensor.c/.h           # Temperature sensor driver
│   ├── led.c/.h              # LED control driver (×2)
│   └── README.txt            # Build instructions
│
├── software/
│   ├── smart_temperature_monitor_sdk.py  # Python SDK
│   ├── example.py            # Usage example
│   └── requirements.txt      # pyserial dependency
│
└── ui/
    ├── App.jsx               # React main component
    ├── App.css               # Styling
    ├── index.html            # HTML entry
    ├── index.js              # React entry point
    ├── package.json          # Dependencies
    └── README.md             # UI documentation
```

### Step 5: Deploy Firmware

```bash
cd smart_temp_monitor/firmware

# Option A: Use ESP-IDF
idf.py build
idf.py flash

# Option B: Use Arduino IDE
# Open main.c in Arduino IDE, select ESP32 board, and upload
```

### Step 6: Test with Python SDK

```python
# In smart_temp_monitor/software/
from smart_temperature_monitor_sdk import SmartTemperatureMonitor

# Connect to device
monitor = SmartTemperatureMonitor('/dev/ttyUSB0', 115200)
monitor.connect()

# Read temperature
temp_response = monitor.control_sensor('read')
print(f"Temperature: {temp_response}")

# Control status LED
monitor.control_led('on')

# Disconnect
monitor.disconnect()
```

### Step 7: Launch Web Interface

```bash
cd smart_temp_monitor/ui
npm install
npm start
```

Opens browser to http://localhost:3000 with:
- Connection status indicator
- Real-time temperature display
- LED control buttons
- Temperature history graph
- Alert threshold controls

### Step 8: Customize and Extend

**Add logging to Python SDK:**
```python
import logging

class SmartTemperatureMonitor:
    def __init__(self, port, baudrate=115200):
        self.logger = logging.getLogger(__name__)
        # ... rest of code
```

**Add temperature thresholds to firmware:**
```c
// In sensor.c
void handle_sensor(void) {
    int temp = read_temperature();
    if (temp > ALERT_THRESHOLD) {
        digitalWrite(ALERT_LED, HIGH);
    } else {
        digitalWrite(ALERT_LED, LOW);
    }
}
```

**Enhance UI with charts:**
```jsx
// In App.jsx
import { LineChart, Line, XAxis, YAxis } from 'recharts';

function TemperatureChart({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="time" />
      <YAxis />
      <Line type="monotone" dataKey="temp" stroke="#8884d8" />
    </LineChart>
  );
}
```

## What You Get

### Generated Firmware Features
- ✅ Analog sensor reading with proper ADC configuration
- ✅ LED control with PWM support
- ✅ Serial communication with JSON formatting
- ✅ WiFi initialization (ESP32)
- ✅ Clean, modular code structure
- ✅ Configuration through headers
- ✅ Platform-optimized code

### Generated Python SDK Features
- ✅ Serial port management
- ✅ Automatic connection handling
- ✅ Command formatting
- ✅ Response parsing
- ✅ Context manager support
- ✅ Error handling
- ✅ Type hints and documentation

### Generated React UI Features
- ✅ Modern, responsive design
- ✅ Connection management
- ✅ Real-time sensor display
- ✅ Interactive controls
- ✅ Status indicators
- ✅ Mobile-friendly
- ✅ Ready for deployment

## Time Savings

**Manual Development Time:**
- Firmware: 4-6 hours
- Python SDK: 2-3 hours
- React UI: 4-6 hours
- Testing & Integration: 2-4 hours
- **Total: 12-19 hours**

**With Accelerapp:**
- Configuration: 10 minutes
- Generation: 3 seconds
- Customization: 1-2 hours
- **Total: ~1.5 hours**

**Time Saved: 10-17 hours** (85-90% reduction)

## Best Practices

### 1. Start with Examples
```bash
# Use provided examples as templates
cp examples/sensor_array.yaml my_project.yaml
# Edit my_project.yaml for your needs
```

### 2. Iterate Quickly
```bash
# Make changes to config
nano my_project.yaml

# Regenerate
accelerapp generate my_project.yaml

# Test immediately
```

### 3. Version Control Your Configs
```bash
git add my_project.yaml
git commit -m "Add temperature monitor configuration"
```

### 4. Customize Generated Code
- Keep generated code separate from custom code
- Use inheritance to extend generated classes
- Add features in separate files

### 5. Test Incrementally
- Test firmware first (serial monitor)
- Test SDK second (Python scripts)
- Test UI last (web browser)

## Advanced Workflows

### Multi-Device Setup
```bash
# Generate controller
accelerapp generate controller.yaml --output ./controller

# Generate sensor node 1
accelerapp generate sensor1.yaml --output ./sensor1

# Generate sensor node 2
accelerapp generate sensor2.yaml --output ./sensor2
```

### Cross-Platform Development
```yaml
# Arduino version
platform: "arduino"

# Then regenerate for ESP32
platform: "esp32"

# Or STM32
platform: "stm32"
```

### Multiple Language SDKs
```bash
# Python SDK
accelerapp generate config.yaml --software-only

# Edit config: software_language: "cpp"
# C++ SDK
accelerapp generate config.yaml --software-only

# Edit config: software_language: "javascript"
# JavaScript SDK
accelerapp generate config.yaml --software-only
```

## Troubleshooting

### Firmware Won't Compile
```bash
# Check platform setting
cat config.yaml | grep platform

# Verify pin assignments
cat smart_temp_monitor/firmware/config.h
```

### SDK Connection Fails
```python
# Check available ports
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)
```

### UI Won't Start
```bash
# Clear node_modules and reinstall
cd smart_temp_monitor/ui
rm -rf node_modules
npm install
npm start
```

## Next Steps

1. **Production Deployment**: Add error handling, logging, security
2. **Data Storage**: Integrate database for historical data
3. **Cloud Integration**: Connect to AWS IoT, Azure IoT, or Google Cloud
4. **Mobile App**: Generate React Native version
5. **Analytics**: Add data analysis and visualization

## Resources

- [Configuration Reference](docs/CONFIGURATION.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Example Projects](examples/)
- [Contributing Guide](CONTRIBUTING.md)

---

**Built with Accelerapp** - From concept to working prototype in minutes! 🚀
