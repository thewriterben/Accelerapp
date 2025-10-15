# ESP32-CAM Firmware

This directory contains firmware templates and utilities for ESP32-CAM devices.

## Firmware Generation

The ESP32-CAM module can generate firmware code for various features:

### Camera Configuration

```python
from accelerapp.hardware.camera.esp32_cam import ESP32Camera

camera = ESP32Camera()
firmware_code = camera.generate_firmware_config()

# Save to file
with open("camera_config.cpp", "w") as f:
    f.write(firmware_code)
```

### Streaming Code

```python
from accelerapp.hardware.camera.esp32_cam import StreamingManager

streaming = StreamingManager(camera)
stream_code = streaming.generate_streaming_code()

# Save files
for filename, code in stream_code.items():
    with open(f"firmware/{filename}", "w") as f:
        f.write(code)
```

### AI Inference Code

```python
from accelerapp.hardware.camera.esp32_cam import AIProcessor

ai = AIProcessor(camera)
ai_code = ai.generate_inference_code()

for filename, code in ai_code.items():
    with open(f"firmware/{filename}", "w") as f:
        f.write(code)
```

## PlatformIO Configuration

Example `platformio.ini` for ESP32-CAM:

```ini
[env:esp32cam]
platform = espressif32
board = esp32cam
framework = arduino

; Upload settings
upload_speed = 921600
monitor_speed = 115200

; Build flags
build_flags = 
    -DBOARD_HAS_PSRAM
    -DCAMERA_MODEL_AI_THINKER
    
; Libraries
lib_deps = 
    esp32-camera
    ArduinoJson
    AsyncTCP
    ESPAsyncWebServer
```

## Required Libraries

For Arduino ESP32:
- esp32-camera
- ArduinoJson
- AsyncTCP
- ESPAsyncWebServer

For TinyML:
- TensorFlowLite_ESP32 (for TFLite inference)
- ESP-NN (for optimized neural network operations)

For Streaming:
- Micro-RTSP (for RTSP streaming)
- AsyncTCP (for WebSocket/WebRTC)

## OTA Updates

The firmware supports OTA (Over-The-Air) updates. Configure in your code:

```cpp
#include <ArduinoOTA.h>

void setup() {
    // ... camera setup ...
    
    ArduinoOTA.setHostname("esp32cam");
    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();
    // ... your code ...
}
```

## Memory Considerations

ESP32-CAM typically has:
- 4MB Flash
- 520KB SRAM
- 4MB PSRAM (if available)

Optimize memory usage:
- Use PSRAM for frame buffers
- Reduce frame buffer count
- Use lower frame sizes for AI processing
- Enable quantization for TinyML models

## Pin Mappings

### AI-Thinker ESP32-CAM

```
Camera Pins:
  PWDN  GPIO32
  RESET -1 (software reset)
  XCLK  GPIO0
  SIOD  GPIO26 (SDA)
  SIOC  GPIO27 (SCL)
  
  D7    GPIO35
  D6    GPIO34
  D5    GPIO39
  D4    GPIO36
  D3    GPIO21
  D2    GPIO19
  D1    GPIO18
  D0    GPIO5
  VSYNC GPIO25
  HREF  GPIO23
  PCLK  GPIO22

Flash:
  GPIO4 (built-in LED/Flash)

SD Card:
  Not available on AI-Thinker
```

### WROVER-KIT

```
Camera Pins:
  PWDN  -1
  RESET -1
  XCLK  GPIO21
  SIOD  GPIO26 (SDA)
  SIOC  GPIO27 (SCL)
  
  D7    GPIO35
  D6    GPIO34
  D5    GPIO39
  D4    GPIO36
  D3    GPIO19
  D2    GPIO18
  D1    GPIO5
  D0    GPIO4
  VSYNC GPIO25
  HREF  GPIO23
  PCLK  GPIO22
```

## Troubleshooting

### Camera initialization fails
- Check power supply (5V, 500mA minimum)
- Verify pin connections
- Test with basic example first

### Out of memory errors
- Reduce frame size
- Use single frame buffer
- Enable PSRAM

### Streaming issues
- Check WiFi signal strength
- Reduce frame rate
- Lower JPEG quality

### AI inference slow
- Use INT8 quantization
- Reduce input size
- Enable ESP-NN optimizations

## Example Firmware

See generated code examples:
- `examples/esp32_cam_demo.py` - Generates complete firmware
- `docs/ESP32_CAM_GUIDE.md` - Firmware generation guide

## Building

Using Arduino IDE:
1. Install ESP32 board support
2. Select "AI Thinker ESP32-CAM" board
3. Add required libraries
4. Upload generated code

Using PlatformIO:
```bash
pio run -t upload
pio device monitor
```

## License

MIT License - See main LICENSE file
