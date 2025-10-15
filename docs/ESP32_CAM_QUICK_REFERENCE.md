# ESP32-CAM Quick Reference

## Installation

```bash
pip install accelerapp
```

## Basic Usage

```python
from accelerapp.hardware import ESP32Camera, CameraVariant

# Initialize camera
camera = ESP32Camera()
camera.initialize()

# Capture frame
frame = camera.capture_frame()
```

## Camera Variants

```python
from accelerapp.hardware.camera.esp32_cam import CameraVariant

CameraVariant.AI_THINKER      # Default, most common
CameraVariant.WROVER_KIT      # ESP32-WROVER-KIT
CameraVariant.ESP_EYE         # ESP32-EYE
CameraVariant.M5STACK_CAMERA  # M5Stack
CameraVariant.TTGO_T_CAMERA   # TTGO T-Camera
```

## Frame Sizes

```python
from accelerapp.hardware.camera.esp32_cam import FrameSize

FrameSize.QQVGA  # 160x120
FrameSize.QVGA   # 320x240
FrameSize.VGA    # 640x480
FrameSize.SVGA   # 800x600
FrameSize.XGA    # 1024x768
FrameSize.SXGA   # 1280x1024
FrameSize.UXGA   # 1600x1200
```

## Streaming

### MJPEG Streaming

```python
from accelerapp.hardware.camera.esp32_cam import (
    StreamingManager,
    StreamingProtocol,
)

streaming = StreamingManager(camera)
stream_info = streaming.start_stream()
# Access at: http://device:8080/stream
```

### RTSP Streaming

```python
from accelerapp.hardware.camera.esp32_cam import StreamConfig

config = StreamConfig(protocol=StreamingProtocol.RTSP)
streaming = StreamingManager(camera, config)
stream_info = streaming.start_stream()
# Access at: rtsp://device:8080/stream
```

### WebRTC Streaming

```python
config = StreamConfig(protocol=StreamingProtocol.WEBRTC)
streaming = StreamingManager(camera, config)
stream_info = streaming.start_stream()
```

## AI Processing

### Person Detection

```python
from accelerapp.hardware.camera.esp32_cam import (
    AIProcessor,
    DetectionModel,
)

ai = AIProcessor(camera)
ai.config.model_type = DetectionModel.PERSON_DETECTION
ai.load_model()

detections = ai.detect()
```

### Face Detection

```python
ai = AIProcessor(camera)
ai.config.model_type = DetectionModel.FACE_DETECTION
ai.load_model()

detections = ai.detect()
```

### Custom Model

```python
from accelerapp.hardware.camera.esp32_cam import ModelConfig

config = ModelConfig(
    model_type=DetectionModel.CUSTOM,
    model_path="/path/to/model.tflite",
    confidence_threshold=0.7,
)

ai = AIProcessor(camera, config)
ai.load_model()
```

## Motion Detection

```python
from accelerapp.hardware.camera.esp32_cam import (
    MotionDetector,
    MotionConfig,
)

# Setup
motion = MotionDetector(camera)

# Detect
if motion.detect_motion():
    print("Motion detected!")

# Event callback
def on_motion(event):
    print(f"Motion: {event.confidence}")

motion.add_event_callback(on_motion)
```

## QR Code Scanning

```python
from accelerapp.hardware.camera.esp32_cam import QRScanner

scanner = QRScanner(camera)
result = scanner.scan()

if result:
    print(f"QR Data: {result['data']}")
```

## Remote Access

### Basic Token Auth

```python
from accelerapp.hardware.camera.esp32_cam import (
    RemoteAccess,
    AuthConfig,
    AuthMethod,
)

auth_config = AuthConfig(
    method=AuthMethod.TOKEN,
    access_token="your_token_here",
)

remote = RemoteAccess(camera, auth_config)
```

### With ngrok Tunnel

```python
from accelerapp.hardware.camera.esp32_cam import (
    TunnelConfig,
    TunnelType,
)

tunnel_config = TunnelConfig(
    tunnel_type=TunnelType.NGROK,
    ngrok_auth_token="your_ngrok_token",
)

remote = RemoteAccess(camera, tunnel_config=tunnel_config)
info = remote.start_tunnel()
print(f"Access at: {info['public_url']}")
```

## Web Interface

```python
from accelerapp.hardware.camera.esp32_cam import WebInterface

web = WebInterface(camera)

# Handle API request
response = web.handle_request(
    "/api/camera/status",
    "GET",
    {}
)
```

### API Endpoints

```
GET  /api/camera/status      # Get camera status
GET  /api/camera/capture     # Capture single frame
GET  /api/camera/config      # Get configuration
PUT  /api/camera/config      # Update configuration

POST /api/stream/start       # Start streaming
POST /api/stream/stop        # Stop streaming
GET  /api/stream/status      # Stream status

PUT  /api/settings/quality   # Set JPEG quality
PUT  /api/settings/brightness # Set brightness
PUT  /api/settings/flip      # Set flip settings

GET  /                       # Home page
GET  /ui/live               # Live view
GET  /ui/settings           # Settings page
```

## Camera Settings

```python
# Quality (0-63, lower is better)
camera.set_quality(12)

# Brightness (-2 to 2)
camera.set_brightness(1)

# Contrast (-2 to 2)
camera.set_contrast(0)

# Flip
camera.set_flip(horizontal=True, vertical=False)

# Frame size
camera.set_frame_size(FrameSize.VGA)
```

## Firmware Generation

```python
# Camera config
firmware = camera.generate_firmware_config()

# Streaming
stream_code = streaming.generate_streaming_code()

# AI inference
ai_code = ai.generate_inference_code()

# Motion detection
motion_code = motion.generate_motion_detection_code()
```

## Digital Twin Integration

```python
from accelerapp.hardware.camera.esp32_cam import CameraConfig

config = CameraConfig(
    twin_id="camera_001",
    twin_sync_interval=60,
    enable_metrics=True,
    enable_health_checks=True,
)

camera = ESP32Camera(config)
```

## Complete Example

```python
from accelerapp.hardware.camera.esp32_cam import (
    ESP32Camera,
    CameraConfig,
    StreamingManager,
    AIProcessor,
    MotionDetector,
    WebInterface,
)

# Initialize
camera = ESP32Camera()
camera.initialize()

# Setup streaming
streaming = StreamingManager(camera)
streaming.start_stream()

# Setup AI
ai = AIProcessor(camera)
ai.load_model()

# Setup motion detection
motion = MotionDetector(camera)

# Setup web interface
web = WebInterface(camera)

# Main loop
while True:
    # Detect motion
    if motion.detect_motion():
        # Run AI detection
        detections = ai.detect()
        
        for det in detections:
            print(f"{det.label}: {det.confidence:.2f}")
```

## Common Issues

### Camera won't initialize
- Check pin configuration
- Verify power supply (5V, 500mA+)
- Check cable connection

### Low FPS
- Reduce frame size
- Increase JPEG quality value
- Check WiFi signal

### No detections
- Check model loading
- Adjust confidence threshold
- Verify lighting

## Performance Tips

- Use VGA (640x480) for balance of quality/performance
- JPEG quality 10-15 for most applications
- Enable adaptive streaming for variable bandwidth
- Use INT8 quantization for AI models
- Frame skip for motion detection (process every 2nd frame)

## Security

```python
# Use token authentication
auth_config = AuthConfig(
    method=AuthMethod.TOKEN,
    access_token="secure_random_token",
)

# Enable IP whitelisting
auth_config.allowed_ips = ["192.168.1.0/24"]

# Enable rate limiting
auth_config.rate_limit_per_minute = 60
```

## Resources

- Full Guide: `docs/ESP32_CAM_GUIDE.md`
- Examples: `examples/esp32_cam_*.py`
- Tests: `tests/test_esp32_cam.py`
- GitHub: https://github.com/thewriterben/Accelerapp
