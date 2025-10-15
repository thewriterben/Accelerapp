"""
ESP32-CAM Integration Demo
Demonstrates comprehensive camera functionality for Accelerapp platform.
"""

from accelerapp.hardware.camera import (
    ESP32Camera,
    CameraConfig,
    CameraResolution,
    StreamingServer,
    StreamProtocol,
    MotionDetector,
    CameraDigitalTwin,
    CameraWebInterface,
    StorageManager,
    CameraSecurityManager,
)
from accelerapp.hardware.camera.esp32_cam.streaming import StreamConfig
from accelerapp.hardware.camera.esp32_cam.motion_detection import MotionSensitivity
from accelerapp.hardware.camera.esp32_cam.security import SecurityConfig, AuthMethod, AccessLevel


def demo_basic_camera():
    """Demonstrate basic camera operations."""
    print("\n" + "=" * 60)
    print("1. Basic Camera Operations")
    print("=" * 60)
    
    # Create camera configuration
    config = CameraConfig(
        device_id="esp32cam_demo_001",
        board_type="ai_thinker",
        resolution=CameraResolution.HD,
        frame_rate=15,
    )
    
    # Initialize camera
    camera = ESP32Camera(config)
    print(f"✓ Camera created: {config.device_id}")
    
    if camera.initialize():
        print("✓ Camera initialized successfully")
    
    # Capture image
    image = camera.capture_image()
    if image:
        print(f"✓ Image captured: {image['resolution']}")
        print(f"  Capture #{image['capture_number']}")
    
    # Get status
    status = camera.get_status()
    print(f"✓ Camera status:")
    print(f"  Board: {status['board_type']}")
    print(f"  Resolution: {status['resolution']}")
    print(f"  Total captures: {status['stats']['captures']}")


def demo_streaming():
    """Demonstrate video streaming capabilities."""
    print("\n" + "=" * 60)
    print("2. Video Streaming")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_stream_001")
    camera = ESP32Camera(config)
    camera.initialize()
    
    # Setup MJPEG streaming
    stream_config = StreamConfig(
        protocol=StreamProtocol.MJPEG,
        port=81,
        max_clients=5,
    )
    
    server = StreamingServer(camera, stream_config)
    print(f"✓ Streaming server created")
    
    if server.start():
        print(f"✓ Streaming started")
        print(f"  Stream URL: {server.get_stream_url()}")
        print(f"  Protocol: {stream_config.protocol.value}")
        print(f"  Max clients: {stream_config.max_clients}")
    
    # Simulate client connections
    server.add_client("client_001", {"ip": "192.168.1.100"})
    server.add_client("client_002", {"ip": "192.168.1.101"})
    print(f"✓ Active clients: {server.get_client_count()}")
    
    # Get status
    status = server.get_status()
    print(f"✓ Server status:")
    print(f"  Active: {status['active']}")
    print(f"  Clients: {status['clients']}/{status['max_clients']}")
    
    server.stop()
    print("✓ Streaming stopped")


def demo_motion_detection():
    """Demonstrate motion detection features."""
    print("\n" + "=" * 60)
    print("3. Motion Detection")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_motion_001")
    camera = ESP32Camera(config)
    camera.initialize()
    
    # Setup motion detector
    detector = MotionDetector(camera, sensitivity=MotionSensitivity.MEDIUM)
    print(f"✓ Motion detector created")
    
    # Register callback
    def on_motion(event):
        print(f"  ⚠️  Motion detected! Event ID: {event.event_id}")
    
    detector.register_callback(on_motion)
    print("✓ Motion callback registered")
    
    # Enable detection
    if detector.enable():
        print("✓ Motion detection enabled")
    
    # Configure settings
    detector.set_sensitivity(MotionSensitivity.HIGH)
    print(f"✓ Sensitivity set to: {detector.sensitivity.value}")
    
    # Get status
    status = detector.get_status()
    print(f"✓ Detector status:")
    print(f"  Enabled: {status['enabled']}")
    print(f"  Sensitivity: {status['sensitivity']}")
    print(f"  Events: {status['event_count']}")


def demo_digital_twin():
    """Demonstrate digital twin integration."""
    print("\n" + "=" * 60)
    print("4. Digital Twin Integration")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_twin_001")
    camera = ESP32Camera(config)
    camera.initialize()
    
    # Create digital twin
    twin = CameraDigitalTwin(camera, twin_id="twin_cam_001")
    print(f"✓ Digital twin created: {twin.twin_id}")
    
    # Sync state
    state = twin.sync_state()
    print(f"✓ State synchronized")
    print(f"  Timestamp: {state['timestamp']}")
    
    # Get telemetry
    telemetry = twin.get_telemetry()
    print(f"✓ Telemetry collected:")
    print(f"  Health: {telemetry['health']}")
    print(f"  Initialized: {telemetry['metrics']['initialized']}")
    
    # Predictive maintenance
    maintenance = twin.predict_maintenance()
    print(f"✓ Predictive maintenance:")
    print(f"  Usage: {maintenance['usage_percentage']:.1f}%")
    print(f"  Maintenance recommended: {maintenance['maintenance_recommended']}")
    print(f"  Health: {maintenance['health_status']}")
    
    # Analytics
    analytics = twin.get_analytics()
    print(f"✓ Performance analytics:")
    print(f"  Total captures: {analytics['performance']['total_captures']}")
    print(f"  Errors: {analytics['performance']['error_count']}")


def demo_web_interface():
    """Demonstrate web interface and API."""
    print("\n" + "=" * 60)
    print("5. Web Interface & API")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_web_001")
    camera = ESP32Camera(config)
    camera.initialize()
    
    # Setup web interface
    web = CameraWebInterface(camera, port=80)
    print(f"✓ Web interface created")
    
    if web.start():
        print(f"✓ Web server started")
        print(f"  URL: {web.get_interface_url()}")
    
    # Test API endpoints
    api_info = web.get_api_info()
    print(f"✓ API endpoints available:")
    for endpoint in api_info['endpoints']:
        print(f"  - {endpoint}")
    
    # Simulate API calls
    status = web.get_status_handler()
    print(f"✓ API call: GET /api/status")
    print(f"  Response: {status['status']}")
    
    config_resp = web.get_config_handler()
    print(f"✓ API call: GET /api/config")
    print(f"  Device: {config_resp['data']['device_id']}")
    
    web.stop()
    print("✓ Web server stopped")


def demo_storage():
    """Demonstrate storage management."""
    print("\n" + "=" * 60)
    print("6. Storage Management")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_storage_001")
    camera = ESP32Camera(config)
    camera.initialize()
    
    # Setup storage
    storage = StorageManager(camera)
    print(f"✓ Storage manager created")
    
    if storage.initialize():
        print("✓ Storage initialized")
    
    # Save images
    for i in range(3):
        image_data = {"size_bytes": 1024 * (i + 1)}
        filepath = storage.save_image(image_data)
        print(f"✓ Image saved: {filepath}")
    
    # Get storage info
    info = storage.get_storage_info()
    print(f"✓ Storage information:")
    print(f"  Type: {info['storage_type']}")
    print(f"  Files: {info['file_count']}")
    print(f"  Used: {info['used_space_mb']:.2f} MB")
    print(f"  Free: {info['free_space_mb']:.2f} MB")
    print(f"  Usage: {info['used_percent']:.1f}%")
    
    # List files
    files = storage.list_files()
    print(f"✓ Files stored: {len(files)}")


def demo_security():
    """Demonstrate security features."""
    print("\n" + "=" * 60)
    print("7. Security Management")
    print("=" * 60)
    
    config = CameraConfig(device_id="esp32cam_secure_001")
    camera = ESP32Camera(config)
    
    # Setup security
    security_config = SecurityConfig(
        auth_method=AuthMethod.TOKEN,
        enable_encryption=True,
    )
    security = CameraSecurityManager(camera, security_config)
    print(f"✓ Security manager created")
    
    # Add users
    security.add_user("admin", "admin123", AccessLevel.ADMIN)
    security.add_user("operator", "op123", AccessLevel.USER)
    security.add_user("viewer", "view123", AccessLevel.GUEST)
    print("✓ Users added: admin, operator, viewer")
    
    # Authenticate
    admin_token = security.authenticate("admin", "admin123")
    if admin_token:
        print(f"✓ Admin authenticated")
        print(f"  Token: {admin_token[:16]}...")
    
    # Check permissions
    has_admin = security.check_permission(admin_token, AccessLevel.ADMIN)
    print(f"✓ Permission check (ADMIN): {has_admin}")
    
    # Security status
    status = security.get_security_status()
    print(f"✓ Security status:")
    print(f"  Auth method: {status['auth_method']}")
    print(f"  Encryption: {status['encryption_enabled']}")
    print(f"  Total users: {status['total_users']}")
    print(f"  Active tokens: {status['active_tokens']}")


def demo_advanced_features():
    """Demonstrate advanced camera features."""
    print("\n" + "=" * 60)
    print("8. Advanced Features")
    print("=" * 60)
    
    config = CameraConfig(
        device_id="esp32cam_advanced_001",
        board_type="esp32_s3_cam",  # Using S3 variant
        resolution=CameraResolution.UXGA,
        frame_rate=20,
    )
    
    camera = ESP32Camera(config)
    camera.initialize()
    print(f"✓ Advanced camera initialized")
    print(f"  Board: {config.board_type}")
    print(f"  Resolution: {config.resolution.value}")
    
    # Test different resolutions
    resolutions = [
        CameraResolution.VGA,
        CameraResolution.HD,
        CameraResolution.UXGA,
    ]
    
    print("✓ Testing resolution changes:")
    for res in resolutions:
        camera.set_resolution(res)
        print(f"  - {res.value}")
    
    # Test image adjustments
    camera.set_brightness(1)
    camera.set_quality(8)
    camera.set_flip(vertical=False, horizontal=True)
    print("✓ Image adjustments applied")
    
    # Multiple captures
    print("✓ Performing multiple captures:")
    for i in range(5):
        image = camera.capture_image()
        print(f"  Capture #{image['capture_number']}")
    
    final_config = camera.get_config()
    print(f"✓ Final configuration:")
    print(f"  Resolution: {final_config['resolution']}")
    print(f"  Quality: {final_config['jpeg_quality']}")
    print(f"  Brightness: {final_config['brightness']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("ESP32-CAM Integration Demonstration")
    print("Accelerapp Hardware Camera Module")
    print("=" * 60)
    
    try:
        demo_basic_camera()
        demo_streaming()
        demo_motion_detection()
        demo_digital_twin()
        demo_web_interface()
        demo_storage()
        demo_security()
        demo_advanced_features()
        
        print("\n" + "=" * 60)
        print("✓ All demonstrations completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
