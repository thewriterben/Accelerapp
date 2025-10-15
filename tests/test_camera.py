"""
Tests for ESP32-CAM hardware module.
"""

import pytest
from accelerapp.hardware.camera import (
    ESP32Camera,
    CameraConfig,
    CameraResolution,
    StreamingServer,
    StreamProtocol,
    MotionDetector,
    MotionEvent,
    CameraDigitalTwin,
    CameraWebInterface,
    StorageManager,
    CameraSecurityManager,
)
from accelerapp.hardware.camera.esp32_cam.core import CameraModel, FrameFormat
from accelerapp.hardware.camera.esp32_cam.streaming import StreamConfig
from accelerapp.hardware.camera.esp32_cam.motion_detection import MotionSensitivity
from accelerapp.hardware.camera.esp32_cam.storage import StorageConfig, StorageType
from accelerapp.hardware.camera.esp32_cam.security import SecurityConfig, AuthMethod, AccessLevel


def test_camera_import():
    """Test camera module can be imported."""
    from accelerapp.hardware import camera
    assert camera is not None


def test_camera_config_creation():
    """Test creating camera configuration."""
    config = CameraConfig(
        device_id="test_cam_001",
        board_type="ai_thinker",
        resolution=CameraResolution.VGA,
    )
    
    assert config.device_id == "test_cam_001"
    assert config.board_type == "ai_thinker"
    assert config.resolution == CameraResolution.VGA
    assert len(config.pin_config) > 0  # Should have default pins


def test_camera_initialization():
    """Test camera initialization."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    assert not camera._initialized
    assert camera.initialize()
    assert camera._initialized


def test_camera_capture():
    """Test image capture."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    result = camera.capture_image()
    assert result is not None
    assert result["device_id"] == "test_cam"
    assert "timestamp" in result
    assert "resolution" in result


def test_camera_streaming():
    """Test video streaming."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    assert not camera.is_streaming()
    assert camera.start_streaming()
    assert camera.is_streaming()
    assert camera.stop_streaming()
    assert not camera.is_streaming()


def test_camera_settings():
    """Test camera settings adjustment."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    # Test resolution change
    assert camera.set_resolution(CameraResolution.HD)
    assert camera.config.resolution == CameraResolution.HD
    
    # Test quality change
    assert camera.set_quality(15)
    assert camera.config.jpeg_quality == 15
    
    # Test brightness
    assert camera.set_brightness(1)
    assert camera.config.brightness == 1
    
    # Test flip settings
    assert camera.set_flip(vertical=True, horizontal=True)
    assert camera.config.vertical_flip
    assert camera.config.horizontal_mirror


def test_camera_status():
    """Test getting camera status."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    camera.initialize()
    
    status = camera.get_status()
    assert status["device_id"] == "test_cam"
    assert status["initialized"]
    assert "resolution" in status
    assert "stats" in status


def test_streaming_server():
    """Test streaming server."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    stream_config = StreamConfig(protocol=StreamProtocol.MJPEG, port=81)
    server = StreamingServer(camera, stream_config)
    
    assert server.start()
    assert server.add_client("client1", {"ip": "192.168.1.100"})
    assert server.get_client_count() == 1
    assert server.remove_client("client1")
    assert server.get_client_count() == 0
    assert server.stop()


def test_streaming_url():
    """Test getting stream URL."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    stream_config = StreamConfig(protocol=StreamProtocol.MJPEG, port=81)
    server = StreamingServer(camera, stream_config)
    
    url = server.get_stream_url()
    assert "http" in url
    assert "81" in url


def test_motion_detection():
    """Test motion detection."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    detector = MotionDetector(camera, sensitivity=MotionSensitivity.MEDIUM)
    
    assert not detector.is_enabled()
    assert detector.enable()
    assert detector.is_enabled()
    
    # Test sensitivity change
    assert detector.set_sensitivity(MotionSensitivity.HIGH)
    assert detector.sensitivity == MotionSensitivity.HIGH
    
    assert detector.disable()
    assert not detector.is_enabled()


def test_motion_callbacks():
    """Test motion detection callbacks."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    detector = MotionDetector(camera)
    
    callback_called = []
    
    def motion_callback(event):
        callback_called.append(event)
    
    detector.register_callback(motion_callback)
    assert detector.unregister_callback(motion_callback)


def test_digital_twin():
    """Test camera digital twin integration."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    camera.initialize()
    
    twin = CameraDigitalTwin(camera)
    
    # Test state synchronization
    state = twin.sync_state()
    assert state["twin_id"] == "test_cam"
    assert "camera_status" in state
    
    # Test telemetry
    telemetry = twin.get_telemetry()
    assert "metrics" in telemetry
    assert "health" in telemetry
    
    # Test analytics
    analytics = twin.get_analytics()
    assert "performance" in analytics


def test_predictive_maintenance():
    """Test predictive maintenance."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    twin = CameraDigitalTwin(camera)
    
    prediction = twin.predict_maintenance()
    assert "usage_percentage" in prediction
    assert "maintenance_recommended" in prediction
    assert "health_status" in prediction


def test_web_interface():
    """Test web interface."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    web = CameraWebInterface(camera, port=80)
    
    assert not web.is_running()
    assert web.start()
    assert web.is_running()
    
    # Test API handlers
    status = web.get_status_handler()
    assert status["status"] == "success"
    
    config_resp = web.get_config_handler()
    assert config_resp["status"] == "success"
    
    assert web.stop()


def test_storage_manager():
    """Test storage management."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    storage_config = StorageConfig(storage_type=StorageType.SD_CARD)
    storage = StorageManager(camera, storage_config)
    
    assert storage.initialize()
    
    # Test image saving
    image_data = {"size_bytes": 1024}
    filepath = storage.save_image(image_data)
    assert filepath is not None
    
    # Test storage info
    info = storage.get_storage_info()
    assert "total_capacity_mb" in info
    assert "used_space_mb" in info
    assert info["file_count"] == 1


def test_storage_file_operations():
    """Test storage file operations."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    storage = StorageManager(camera)
    
    # Save files
    image_data = {"size_bytes": 1024}
    storage.save_image(image_data, "test1.jpg")
    storage.save_image(image_data, "test2.jpg")
    
    # List files
    files = storage.list_files()
    assert len(files) == 2
    
    # Delete file
    assert storage.delete_file("test1.jpg")
    files = storage.list_files()
    assert len(files) == 1


def test_security_manager():
    """Test security management."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    security_config = SecurityConfig(auth_method=AuthMethod.TOKEN)
    security = CameraSecurityManager(camera, security_config)
    
    # Test user management
    assert security.add_user("admin", "password123", AccessLevel.ADMIN)
    assert not security.add_user("admin", "password456", AccessLevel.USER)  # Duplicate
    
    # Test authentication
    token = security.authenticate("admin", "password123")
    assert token is not None
    
    # Test token validation
    token_info = security.validate_token(token)
    assert token_info is not None
    assert token_info["username"] == "admin"
    
    # Test permission check
    assert security.check_permission(token, AccessLevel.USER)
    assert security.check_permission(token, AccessLevel.ADMIN)


def test_security_failed_login():
    """Test security failed login handling."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    security = CameraSecurityManager(camera)
    
    security.add_user("user1", "correct", AccessLevel.USER)
    
    # Test wrong password
    token = security.authenticate("user1", "wrong")
    assert token is None


def test_pin_configurations():
    """Test pin configurations for different boards."""
    # AI-Thinker
    config = CameraConfig(device_id="test", board_type="ai_thinker")
    assert config.pin_config["PWDN"] == 32
    assert config.pin_config["XCLK"] == 0
    
    # ESP32-S3-CAM
    config = CameraConfig(device_id="test", board_type="esp32_s3_cam")
    assert config.pin_config["XCLK"] == 15
    assert config.pin_config["SIOD"] == 4


def test_camera_models():
    """Test different camera sensor models."""
    from accelerapp.hardware.camera.drivers import OV2640Driver, OV3660Driver
    
    # Test OV2640
    ov2640 = OV2640Driver()
    assert ov2640.initialize()
    caps = ov2640.get_capabilities()
    assert caps["sensor_name"] == "OV2640"
    assert "UXGA" in caps["supported_resolutions"]
    
    # Test OV3660
    ov3660 = OV3660Driver()
    assert ov3660.initialize()
    caps = ov3660.get_capabilities()
    assert caps["sensor_name"] == "OV3660"
    assert "QXGA" in caps["supported_resolutions"]


def test_streaming_protocols():
    """Test streaming protocol implementations."""
    from accelerapp.hardware.camera.protocols import MJPEGProtocol, RTSPProtocol
    
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    # Test MJPEG
    mjpeg = MJPEGProtocol(camera)
    assert mjpeg.start_stream()
    assert mjpeg.is_streaming()
    headers = mjpeg.get_stream_header()
    assert "Content-Type" in headers
    assert mjpeg.stop_stream()
    
    # Test RTSP
    rtsp = RTSPProtocol(camera)
    assert rtsp.start_server()
    assert rtsp.is_streaming()
    url = rtsp.get_stream_url()
    assert "rtsp://" in url
    assert rtsp.stop_server()


def test_config_validation():
    """Test configuration validation."""
    from accelerapp.hardware.camera.utils import ConfigValidator
    
    # Valid config
    valid_config = {
        "device_id": "test",
        "resolution": "640x480",
        "jpeg_quality": 10,
        "brightness": 0,
        "frame_rate": 15,
    }
    errors = ConfigValidator.validate_camera_config(valid_config)
    assert len(errors) == 0
    
    # Invalid config
    invalid_config = {
        "resolution": "999x999",
        "jpeg_quality": 100,
        "brightness": 10,
    }
    errors = ConfigValidator.validate_camera_config(invalid_config)
    assert len(errors) > 0


def test_network_utilities():
    """Test network utilities."""
    from accelerapp.hardware.camera.utils import NetworkHelper
    
    assert NetworkHelper.validate_ip("192.168.1.1")
    assert not NetworkHelper.validate_ip("999.999.999.999")
    assert not NetworkHelper.validate_ip("invalid")
    
    assert NetworkHelper.validate_port(80)
    assert NetworkHelper.validate_port(8080)
    assert not NetworkHelper.validate_port(0)
    assert not NetworkHelper.validate_port(70000)
    
    url = NetworkHelper.format_url("http", "localhost", 80, "/stream")
    assert url == "http://localhost:80/stream"


def test_camera_reset():
    """Test camera reset functionality."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    # Change settings
    camera.set_brightness(2)
    camera.set_flip(vertical=True, horizontal=True)
    
    # Reset
    assert camera.reset()
    assert camera.config.brightness == 0
    assert not camera.config.vertical_flip
    assert not camera.config.horizontal_mirror


def test_camera_shutdown():
    """Test camera shutdown."""
    config = CameraConfig(device_id="test_cam")
    camera = ESP32Camera(config)
    
    camera.initialize()
    camera.start_streaming()
    
    assert camera.shutdown()
    assert not camera._streaming
    assert not camera._initialized
