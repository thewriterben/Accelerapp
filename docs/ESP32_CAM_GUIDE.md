# ESP32-CAM Comprehensive Guide

## Overview

The ESP32-CAM module provides comprehensive camera support for the Accelerapp hardware control platform. It integrates advanced features including TinyML AI processing, multi-protocol streaming, motion detection, remote access, and web-based management.

## Features

### 1. Core Camera Support
- **Multi-variant support**: AI-Thinker, TTGO, WROVER Kit, ESP-EYE, M5Stack
- **Multiple sensors**: OV2640, OV5640, OV3660, OV7670
- **Flexible configuration**: Frame size, pixel format, quality settings
- **Advanced controls**: Brightness, contrast, saturation, sharpness, flip settings

### 2. Multi-Protocol Streaming
- **MJPEG**: Simple HTTP-based streaming
- **RTSP**: Real-Time Streaming Protocol
- **WebRTC**: Low-latency peer-to-peer streaming
- **HTTP**: Standard HTTP streaming
- **Adaptive quality**: Automatic quality adjustment based on bandwidth
- **Multiple concurrent streams**: Support for multiple clients

### 3. AI Processing
- **TinyML integration**: Edge AI inference using TensorFlow Lite Micro
- **Person detection**: Detect humans in frame
- **Face detection**: Detect and recognize faces
- **Object detection**: General object detection
- **Gesture recognition**: Detect hand gestures
- **Custom models**: Support for custom TFLite models

### 4. Motion Detection
- **Multiple algorithms**: Frame difference, background subtraction, optical flow
- **Detection zones**: Define specific areas for motion detection
- **Event-driven**: Trigger callbacks on motion events
- **QR code scanning**: Detect and decode QR codes
- **Configurable sensitivity**: Adjust detection threshold

### 5. Remote Access
- **Secure tunneling**: ngrok, Cloudflare, or custom tunnels
- **Multiple auth methods**: None, Basic, Token, OAuth, Certificate
- **Access control**: IP whitelisting, rate limiting
- **Session management**: Track and manage active sessions
- **Audit logging**: Record all access attempts

### 6. Web Interface
- **RESTful API**: Complete camera control API
- **Web UI**: Built-in web interface for management
- **Live view**: Real-time camera preview
- **Settings management**: Configure camera from web browser
- **CORS support**: Cross-origin resource sharing

## Installation

```bash
pip install accelerapp
```

## Quick Start

### Basic Camera Setup

```python
from accelerapp.hardware.camera.esp32_cam import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
)

# Create camera with AI-Thinker variant
config = CameraConfig(
    variant=CameraVariant.AI_THINKER,
    frame_size=FrameSize.VGA,
    jpeg_quality=12,
)

camera = ESP32Camera(config)
camera.initialize()

# Capture a frame
frame = camera.capture_frame()
```

### Streaming Setup

```python
from accelerapp.hardware.camera.esp32_cam import (
    StreamingManager,
    StreamingProtocol,
    StreamConfig,
)

# Configure MJPEG streaming
stream_config = StreamConfig(
    protocol=StreamingProtocol.MJPEG,
    port=8080,
    fps_target=15,
)

streaming = StreamingManager(camera, stream_config)
stream_info = streaming.start_stream()

print(f"Stream available at: {stream_info['urls']['mjpeg']}")
```

### AI Processing

```python
from accelerapp.hardware.camera.esp32_cam import (
    AIProcessor,
    DetectionModel,
    ModelConfig,
)

# Setup person detection
model_config = ModelConfig(
    model_type=DetectionModel.PERSON_DETECTION,
    confidence_threshold=0.7,
)

ai = AIProcessor(camera, model_config)
ai.load_model()

# Detect people in frame
detections = ai.detect()
for detection in detections:
    print(f"Detected: {detection.label} ({detection.confidence:.2f})")
```

### Motion Detection

```python
from accelerapp.hardware.camera.esp32_cam import (
    MotionDetector,
    MotionConfig,
)

# Setup motion detection
motion_config = MotionConfig(
    threshold=20,
    min_area=500,
)

motion = MotionDetector(camera, motion_config)

# Add event callback
def on_motion(event):
    print(f"Motion detected! Confidence: {event.confidence}")

motion.add_event_callback(on_motion)

# Detect motion
if motion.detect_motion():
    print("Motion detected!")
```

### Remote Access

```python
from accelerapp.hardware.camera.esp32_cam import (
    RemoteAccess,
    AuthConfig,
    TunnelConfig,
    AuthMethod,
    TunnelType,
)

# Setup secure remote access
auth_config = AuthConfig(
    method=AuthMethod.TOKEN,
    access_token="your_secure_token",
)

tunnel_config = TunnelConfig(
    tunnel_type=TunnelType.NGROK,
    ngrok_auth_token="your_ngrok_token",
)

remote = RemoteAccess(camera, auth_config, tunnel_config)

# Start tunnel
info = remote.start_tunnel()
print(f"Camera accessible at: {info['public_url']}")
```

### Web Interface

```python
from accelerapp.hardware.camera.esp32_cam import (
    WebInterface,
    APIConfig,
)

# Setup web interface
api_config = APIConfig(
    port=80,
    enable_api=True,
    enable_web_ui=True,
)

web = WebInterface(camera, api_config)

# API endpoints available:
# GET  /api/camera/status
# GET  /api/camera/capture
# GET  /api/camera/config
# PUT  /api/camera/config
# POST /api/stream/start
# POST /api/stream/stop
# PUT  /api/settings/quality
# PUT  /api/settings/brightness
# PUT  /api/settings/flip
```

## Hardware Variants

### AI-Thinker (Default)
Most common ESP32-CAM variant.

```python
config = CameraConfig(variant=CameraVariant.AI_THINKER)
camera = ESP32Camera(config)
```

### WROVER Kit
ESP32-WROVER-KIT development board.

```python
config = CameraConfig(variant=CameraVariant.WROVER_KIT)
camera = ESP32Camera(config)
```

### ESP-EYE
ESP32-EYE AI development board.

```python
config = CameraConfig(variant=CameraVariant.ESP_EYE)
camera = ESP32Camera(config)
```

### M5Stack Camera
M5Stack camera modules.

```python
config = CameraConfig(variant=CameraVariant.M5STACK_CAMERA)
camera = ESP32Camera(config)
```

## Firmware Generation

Generate firmware code for ESP32:

```python
# Camera configuration
firmware_code = camera.generate_firmware_config()

# Streaming code
stream_code = streaming.generate_streaming_code()

# AI inference code
ai_code = ai.generate_inference_code()

# Motion detection code
motion_code = motion.generate_motion_detection_code()

# Remote access code
remote_code = remote.generate_remote_access_code()
```

## Digital Twin Integration

Integrate with Accelerapp's Digital Twin platform:

```python
config = CameraConfig(
    twin_id="camera_001",
    twin_sync_interval=60,  # seconds
    enable_metrics=True,
    enable_health_checks=True,
)

camera = ESP32Camera(config)
```

## TinyML Integration

Integrate with TinyMLAgent:

```python
from accelerapp.agents import TinyMLAgent

# Setup AI processor
ai = AIProcessor(camera)

# Get TinyML integration spec
spec = ai.integrate_with_tinyml_agent()

# Use with TinyMLAgent
tinyml_agent = TinyMLAgent()
result = tinyml_agent.generate(spec)
```

## Advanced Configuration

### Custom Pin Configuration

```python
config = CameraConfig(
    variant=CameraVariant.GENERIC,
    pin_pwdn=32,
    pin_reset=-1,
    pin_xclk=0,
    pin_sscb_sda=26,
    pin_sscb_scl=27,
    # ... other pins
)
```

### Camera Settings

```python
# Adjust quality
camera.set_quality(10)  # 0-63, lower is better

# Adjust brightness
camera.set_brightness(1)  # -2 to 2

# Adjust contrast
camera.set_contrast(1)  # -2 to 2

# Flip image
camera.set_flip(horizontal=True, vertical=False)

# Set frame size
camera.set_frame_size(FrameSize.SVGA)
```

### Streaming Quality Presets

```python
from accelerapp.hardware.camera.esp32_cam import StreamQuality

# Low quality (320x240)
config = StreamConfig(quality=StreamQuality.LOW)

# Medium quality (640x480)
config = StreamConfig(quality=StreamQuality.MEDIUM)

# High quality (800x600)
config = StreamConfig(quality=StreamQuality.HIGH)

# Ultra quality (1024x768+)
config = StreamConfig(quality=StreamQuality.ULTRA)
```

## API Reference

### ESP32Camera

Main camera interface class.

**Methods:**
- `initialize()`: Initialize camera hardware
- `capture_frame()`: Capture a single frame
- `set_quality(quality)`: Set JPEG quality (0-63)
- `set_frame_size(size)`: Set frame size
- `set_brightness(value)`: Set brightness (-2 to 2)
- `set_contrast(value)`: Set contrast (-2 to 2)
- `set_flip(h, v)`: Set flip settings
- `get_status()`: Get camera status
- `get_config()`: Get configuration
- `generate_firmware_config()`: Generate firmware code
- `shutdown()`: Shutdown camera

### StreamingManager

Manages video streaming.

**Methods:**
- `start_stream(stream_id)`: Start streaming
- `stop_stream(stream_id)`: Stop specific stream
- `stop_all_streams()`: Stop all streams
- `get_stream_stats()`: Get statistics
- `generate_streaming_code()`: Generate firmware code

### AIProcessor

AI processing engine.

**Methods:**
- `load_model(path)`: Load TinyML model
- `detect(frame)`: Run detection
- `get_statistics()`: Get AI statistics
- `generate_inference_code()`: Generate firmware code
- `integrate_with_tinyml_agent()`: Get TinyML spec

### MotionDetector

Motion detection engine.

**Methods:**
- `detect_motion(frame)`: Detect motion
- `add_event_callback(callback)`: Add event handler
- `get_statistics()`: Get statistics
- `generate_motion_detection_code()`: Generate firmware

### QRScanner

QR code scanner.

**Methods:**
- `scan(frame)`: Scan for QR codes
- `get_statistics()`: Get scan statistics
- `generate_qr_scanner_code()`: Generate firmware

### RemoteAccess

Remote access manager.

**Methods:**
- `start_tunnel()`: Start cloud tunnel
- `stop_tunnel()`: Stop tunnel
- `authenticate(credentials)`: Authenticate user
- `create_session(user, ip)`: Create session
- `end_session(session_id)`: End session
- `get_status()`: Get remote access status
- `get_access_log()`: Get access log

### WebInterface

Web interface and API.

**Methods:**
- `handle_request(path, method, params)`: Handle HTTP request
- `get_statistics()`: Get interface statistics
- `generate_api_documentation()`: Generate docs

## Troubleshooting

### Camera initialization fails

**Issue:** Camera fails to initialize
**Solution:** 
- Check pin configuration for your board variant
- Verify power supply is adequate (5V, 500mA+)
- Check camera cable connection

### Streaming performance issues

**Issue:** Low FPS or choppy video
**Solution:**
- Reduce frame size (e.g., VGA instead of SVGA)
- Increase JPEG quality number (lower quality, higher FPS)
- Enable adaptive quality
- Check WiFi signal strength

### AI detection not working

**Issue:** No detections or low accuracy
**Solution:**
- Ensure model is loaded correctly
- Adjust confidence threshold
- Check lighting conditions
- Verify input image preprocessing

### Remote access connection fails

**Issue:** Cannot connect remotely
**Solution:**
- Check tunnel configuration
- Verify auth credentials
- Check firewall settings
- Ensure device has internet connectivity

## Performance Tips

1. **Frame Size**: Use smallest frame size needed for your application
2. **JPEG Quality**: Higher quality numbers = lower file size but lower quality
3. **Frame Buffer**: Use 2 frame buffers for smoother streaming
4. **AI Processing**: Use INT8 quantization for faster inference
5. **Motion Detection**: Use frame skip to reduce processing load
6. **Streaming**: Enable adaptive quality for variable bandwidth

## Security Best Practices

1. **Always use authentication** for remote access
2. **Use HTTPS/TLS** for encrypted communication
3. **Implement IP whitelisting** for production deployments
4. **Regular security audits** using Accelerapp's security tools
5. **Keep firmware updated** via OTA updates
6. **Use strong tokens** for token-based authentication
7. **Monitor access logs** for suspicious activity

## Examples

See the `examples/` directory for complete examples:
- `esp32_cam_basic.py`: Basic camera usage
- `esp32_cam_streaming.py`: Streaming setup
- `esp32_cam_ai.py`: AI processing
- `esp32_cam_remote.py`: Remote access
- `esp32_cam_full.py`: Complete integration

## Integration with Accelerapp Ecosystem

The ESP32-CAM module integrates seamlessly with:
- **Digital Twin Platform**: Real-time device monitoring
- **Observability System**: Metrics and health checks
- **TinyML Agent**: Edge AI model deployment
- **Security Framework**: Compliance and access control
- **Hardware Abstraction Layer**: Unified hardware interface

## Support

For issues and questions:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: https://github.com/thewriterben/Accelerapp/docs
- Examples: https://github.com/thewriterben/Accelerapp/examples

## License

MIT License - See LICENSE file for details
