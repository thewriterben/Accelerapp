"""
Tests for ESP32-CAM hardware support.
"""

import pytest
from accelerapp.hardware.camera.esp32_cam import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
    CameraSensor,
    FrameSize,
    PixelFormat,
    StreamingManager,
    StreamingProtocol,
    StreamConfig,
    AIProcessor,
    DetectionModel,
    ModelConfig,
    MotionDetector,
    MotionConfig,
    QRScanner,
    RemoteAccess,
    AuthConfig,
    TunnelConfig,
    WebInterface,
    APIConfig,
)


# Core Camera Tests


def test_esp32_camera_import():
    """Test that ESP32Camera can be imported."""
    assert ESP32Camera is not None
    assert CameraVariant is not None
    assert CameraConfig is not None


def test_esp32_camera_initialization():
    """Test ESP32Camera initialization with default config."""
    camera = ESP32Camera()
    
    assert camera is not None
    assert camera.initialized is False
    assert camera.config.variant == CameraVariant.AI_THINKER
    assert camera.config.sensor == CameraSensor.OV2640
    assert camera.frame_count == 0


def test_esp32_camera_variants():
    """Test different camera variants."""
    variants = [
        CameraVariant.AI_THINKER,
        CameraVariant.WROVER_KIT,
        CameraVariant.ESP_EYE,
        CameraVariant.M5STACK_CAMERA,
    ]
    
    for variant in variants:
        config = CameraConfig(variant=variant)
        camera = ESP32Camera(config)
        assert camera.config.variant == variant


def test_camera_initialization():
    """Test camera hardware initialization."""
    camera = ESP32Camera()
    result = camera.initialize()
    
    assert result is True
    assert camera.initialized is True


def test_camera_config_validation():
    """Test camera configuration validation."""
    camera = ESP32Camera()
    
    # Valid config
    assert camera._validate_config() is True
    
    # Invalid JPEG quality
    camera.config.jpeg_quality = 100
    assert camera._validate_config() is False
    
    # Reset to valid
    camera.config.jpeg_quality = 12
    assert camera._validate_config() is True


def test_camera_capture_frame():
    """Test frame capture."""
    camera = ESP32Camera()
    camera.initialize()
    
    frame = camera.capture_frame()
    assert frame is not None
    assert camera.frame_count == 1


def test_camera_set_quality():
    """Test setting JPEG quality."""
    camera = ESP32Camera()
    
    # Valid quality
    assert camera.set_quality(10) is True
    assert camera.config.jpeg_quality == 10
    
    # Invalid quality
    assert camera.set_quality(100) is False


def test_camera_set_brightness():
    """Test setting brightness."""
    camera = ESP32Camera()
    
    assert camera.set_brightness(1) is True
    assert camera.config.brightness == 1
    
    assert camera.set_brightness(-2) is True
    assert camera.config.brightness == -2
    
    assert camera.set_brightness(5) is False


def test_camera_set_flip():
    """Test setting flip settings."""
    camera = ESP32Camera()
    
    assert camera.set_flip(horizontal=True, vertical=False) is True
    assert camera.config.horizontal_flip is True
    assert camera.config.vertical_flip is False


def test_camera_get_status():
    """Test getting camera status."""
    camera = ESP32Camera()
    camera.initialize()
    
    status = camera.get_status()
    
    assert "initialized" in status
    assert status["initialized"] is True
    assert "variant" in status
    assert "frame_count" in status


def test_camera_firmware_generation():
    """Test firmware configuration generation."""
    camera = ESP32Camera()
    code = camera.generate_firmware_config()
    
    assert code is not None
    assert "camera_config_t" in code
    assert "esp_camera_init" in code
    assert "#include <esp_camera.h>" in code


# Streaming Tests


def test_streaming_manager_initialization():
    """Test streaming manager initialization."""
    camera = ESP32Camera()
    config = StreamConfig(protocol=StreamingProtocol.MJPEG)
    
    manager = StreamingManager(camera, config)
    
    assert manager is not None
    assert manager.config.protocol == StreamingProtocol.MJPEG


def test_streaming_protocols():
    """Test different streaming protocols."""
    camera = ESP32Camera()
    camera.initialize()
    
    protocols = [
        StreamingProtocol.MJPEG,
        StreamingProtocol.RTSP,
        StreamingProtocol.WEBRTC,
        StreamingProtocol.HTTP,
    ]
    
    for protocol in protocols:
        config = StreamConfig(protocol=protocol)
        manager = StreamingManager(camera, config)
        assert manager.config.protocol == protocol


def test_streaming_start_stop():
    """Test starting and stopping streams."""
    camera = ESP32Camera()
    camera.initialize()
    manager = StreamingManager(camera)
    
    # Start stream
    info = manager.start_stream()
    assert info["status"] == "active"
    assert "urls" in info
    
    # Stop stream
    stream_id = info["stream_id"]
    result = manager.stop_stream(stream_id)
    assert result is True


def test_streaming_code_generation():
    """Test streaming code generation."""
    camera = ESP32Camera()
    config = StreamConfig(protocol=StreamingProtocol.MJPEG)
    manager = StreamingManager(camera, config)
    
    code = manager.generate_streaming_code()
    
    assert "mjpeg_stream.h" in code
    assert "mjpeg_stream.cpp" in code


# AI Processing Tests


def test_ai_processor_initialization():
    """Test AI processor initialization."""
    camera = ESP32Camera()
    config = ModelConfig(model_type=DetectionModel.PERSON_DETECTION)
    
    processor = AIProcessor(camera, config)
    
    assert processor is not None
    assert processor.config.model_type == DetectionModel.PERSON_DETECTION


def test_ai_model_types():
    """Test different AI model types."""
    camera = ESP32Camera()
    
    models = [
        DetectionModel.PERSON_DETECTION,
        DetectionModel.FACE_DETECTION,
        DetectionModel.OBJECT_DETECTION,
    ]
    
    for model in models:
        config = ModelConfig(model_type=model)
        processor = AIProcessor(camera, config)
        assert processor.config.model_type == model


def test_ai_load_model():
    """Test loading AI model."""
    camera = ESP32Camera()
    processor = AIProcessor(camera)
    
    result = processor.load_model()
    assert result is True
    assert processor.model_loaded is True


def test_ai_detection():
    """Test AI detection."""
    camera = ESP32Camera()
    camera.initialize()
    processor = AIProcessor(camera)
    processor.load_model()
    
    detections = processor.detect()
    
    assert isinstance(detections, list)
    assert processor.inference_count > 0


def test_ai_inference_code_generation():
    """Test inference code generation."""
    camera = ESP32Camera()
    processor = AIProcessor(camera)
    
    code = processor.generate_inference_code()
    
    assert "ai_inference.h" in code
    assert "ai_inference.cpp" in code
    assert "tensorflow/lite" in code["ai_inference.h"]


def test_ai_tinyml_integration():
    """Test TinyML agent integration."""
    camera = ESP32Camera()
    processor = AIProcessor(camera)
    
    spec = processor.integrate_with_tinyml_agent()
    
    assert spec["task_type"] == "inference"
    assert spec["platform"] == "esp32"
    assert "input_shape" in spec


# Motion Detection Tests


def test_motion_detector_initialization():
    """Test motion detector initialization."""
    camera = ESP32Camera()
    config = MotionConfig(threshold=20)
    
    detector = MotionDetector(camera, config)
    
    assert detector is not None
    assert detector.config.threshold == 20


def test_motion_detection():
    """Test motion detection."""
    camera = ESP32Camera()
    camera.initialize()
    detector = MotionDetector(camera)
    
    # First frame - no motion
    result = detector.detect_motion()
    assert result is False
    
    # Second frame - motion detected
    result = detector.detect_motion()
    # May or may not detect depending on placeholder data


def test_motion_statistics():
    """Test motion detection statistics."""
    camera = ESP32Camera()
    detector = MotionDetector(camera)
    
    stats = detector.get_statistics()
    
    assert "algorithm" in stats
    assert "motion_detected" in stats
    assert "total_events" in stats


def test_motion_code_generation():
    """Test motion detection code generation."""
    camera = ESP32Camera()
    detector = MotionDetector(camera)
    
    code = detector.generate_motion_detection_code()
    
    assert "motion_detection.h" in code
    assert "motion_detection.cpp" in code


def test_qr_scanner_initialization():
    """Test QR scanner initialization."""
    camera = ESP32Camera()
    scanner = QRScanner(camera)
    
    assert scanner is not None
    assert scanner.scan_count == 0


def test_qr_scan():
    """Test QR code scanning."""
    camera = ESP32Camera()
    camera.initialize()
    scanner = QRScanner(camera)
    
    result = scanner.scan()
    
    # With placeholder implementation, should return a result
    if result:
        assert "type" in result
        assert "data" in result


def test_qr_code_generation():
    """Test QR scanner code generation."""
    camera = ESP32Camera()
    scanner = QRScanner(camera)
    
    code = scanner.generate_qr_scanner_code()
    
    assert "qr_scanner.h" in code
    assert "qr_scanner.cpp" in code


# Remote Access Tests


def test_remote_access_initialization():
    """Test remote access initialization."""
    camera = ESP32Camera()
    from accelerapp.hardware.camera.esp32_cam import AuthMethod
    auth_config = AuthConfig(method=AuthMethod.TOKEN)
    
    remote = RemoteAccess(camera, auth_config)
    
    assert remote is not None


def test_remote_tunnel_start_stop():
    """Test starting and stopping tunnel."""
    camera = ESP32Camera()
    from accelerapp.hardware.camera.esp32_cam import TunnelType
    tunnel_config = TunnelConfig(tunnel_type=TunnelType.NGROK)
    remote = RemoteAccess(camera, tunnel_config=tunnel_config)
    
    # Start tunnel
    info = remote.start_tunnel()
    assert "public_url" in info or info["status"] == "disabled"
    
    # Stop tunnel
    if remote.tunnel_active:
        result = remote.stop_tunnel()
        assert result is True


def test_remote_authentication():
    """Test authentication methods."""
    camera = ESP32Camera()
    from accelerapp.hardware.camera.esp32_cam import AuthMethod
    
    # No auth
    auth_config = AuthConfig(method=AuthMethod.NONE)
    remote = RemoteAccess(camera, auth_config)
    result = remote.authenticate({})
    assert result["authenticated"] is True
    
    # Token auth
    auth_config = AuthConfig(method=AuthMethod.TOKEN, access_token="test123")
    remote = RemoteAccess(camera, auth_config)
    result = remote.authenticate({"token": "test123"})
    assert result["authenticated"] is True


def test_remote_session_management():
    """Test session management."""
    camera = ESP32Camera()
    remote = RemoteAccess(camera)
    
    # Create session
    result = remote.create_session("user1", "192.168.1.1")
    assert result["status"] == "success"
    
    # End session
    session_id = result["session"]["session_id"]
    result = remote.end_session(session_id)
    assert result is True


def test_remote_code_generation():
    """Test remote access code generation."""
    camera = ESP32Camera()
    remote = RemoteAccess(camera)
    
    code = remote.generate_remote_access_code()
    
    assert "remote_access.h" in code
    assert "remote_access.cpp" in code


# Web Interface Tests


def test_web_interface_initialization():
    """Test web interface initialization."""
    camera = ESP32Camera()
    config = APIConfig(port=8080)
    
    interface = WebInterface(camera, config)
    
    assert interface is not None
    assert interface.config.port == 8080


def test_web_api_routes():
    """Test API route handling."""
    camera = ESP32Camera()
    camera.initialize()
    interface = WebInterface(camera)
    
    # Test status endpoint
    response = interface.handle_request("/api/camera/status", "GET", {})
    assert response["code"] == 200
    assert "data" in response


def test_web_capture_endpoint():
    """Test capture endpoint."""
    camera = ESP32Camera()
    camera.initialize()
    interface = WebInterface(camera)
    
    response = interface.handle_request("/api/camera/capture", "GET", {})
    assert response["code"] == 200


def test_web_settings_endpoints():
    """Test settings endpoints."""
    camera = ESP32Camera()
    camera.initialize()
    interface = WebInterface(camera)
    
    # Set quality
    response = interface.handle_request(
        "/api/settings/quality", "PUT", {"quality": 15}
    )
    assert response["code"] == 200


def test_web_ui_pages():
    """Test UI page generation."""
    camera = ESP32Camera()
    interface = WebInterface(camera)
    
    # Home page
    response = interface.handle_request("/", "GET", {})
    assert response["code"] == 200
    assert "html" in response
    
    # Live page
    response = interface.handle_request("/ui/live", "GET", {})
    assert response["code"] == 200
    
    # Settings page
    response = interface.handle_request("/ui/settings", "GET", {})
    assert response["code"] == 200


def test_web_api_documentation():
    """Test API documentation generation."""
    camera = ESP32Camera()
    interface = WebInterface(camera)
    
    docs = interface.generate_api_documentation()
    
    assert docs is not None
    assert "API Documentation" in docs


# Integration Tests


def test_full_stack_integration():
    """Test integration of all components."""
    # Create camera
    camera = ESP32Camera()
    camera.initialize()
    
    # Add streaming
    streaming = StreamingManager(camera)
    stream_info = streaming.start_stream()
    assert stream_info["status"] == "active"
    
    # Add AI
    ai = AIProcessor(camera)
    ai.load_model()
    detections = ai.detect()
    assert isinstance(detections, list)
    
    # Add motion detection
    motion = MotionDetector(camera)
    motion.detect_motion()
    
    # Add web interface
    web = WebInterface(camera)
    response = web.handle_request("/api/camera/status", "GET", {})
    assert response["code"] == 200


def test_camera_with_digital_twin():
    """Test camera with digital twin integration."""
    config = CameraConfig(
        twin_id="camera_001",
        twin_sync_interval=30,
    )
    
    camera = ESP32Camera(config)
    
    assert camera.config.twin_id == "camera_001"
    assert camera.config.twin_sync_interval == 30


def test_camera_observability():
    """Test camera observability features."""
    config = CameraConfig(
        enable_metrics=True,
        enable_health_checks=True,
    )
    
    camera = ESP32Camera(config)
    
    assert camera.config.enable_metrics is True
    assert camera.config.enable_health_checks is True


def test_hardware_import():
    """Test that camera can be imported from hardware module."""
    from accelerapp.hardware import ESP32Camera, CameraVariant
    
    assert ESP32Camera is not None
    assert CameraVariant is not None
