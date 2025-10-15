"""
ESP32-CAM Comprehensive Demo

Demonstrates all major features of the ESP32-CAM module:
- Camera initialization and configuration
- Multi-protocol streaming
- AI processing with TinyML
- Motion detection
- Remote access
- Web interface

Usage:
    python examples/esp32_cam_demo.py
"""

from accelerapp.hardware.camera.esp32_cam import (
    ESP32Camera,
    CameraVariant,
    CameraConfig,
    FrameSize,
    PixelFormat,
    StreamingManager,
    StreamingProtocol,
    StreamConfig,
    StreamQuality,
    AIProcessor,
    DetectionModel,
    ModelConfig,
    MotionDetector,
    MotionConfig,
    MotionAlgorithm,
    QRScanner,
    RemoteAccess,
    AuthConfig,
    TunnelConfig,
    AuthMethod,
    TunnelType,
    WebInterface,
    APIConfig,
)


def demo_basic_camera():
    """Demonstrate basic camera operations."""
    print("\n" + "=" * 60)
    print("BASIC CAMERA DEMO")
    print("=" * 60)
    
    # Create camera configuration
    config = CameraConfig(
        variant=CameraVariant.AI_THINKER,
        frame_size=FrameSize.VGA,
        pixel_format=PixelFormat.JPEG,
        jpeg_quality=12,
        brightness=0,
        contrast=0,
    )
    
    # Initialize camera
    print("\nInitializing ESP32-CAM...")
    camera = ESP32Camera(config)
    
    if camera.initialize():
        print("✓ Camera initialized successfully")
        
        # Get status
        status = camera.get_status()
        print(f"\nCamera Status:")
        print(f"  Variant: {status['variant']}")
        print(f"  Sensor: {status['sensor']}")
        print(f"  Frame Size: {status['frame_size']}")
        print(f"  Frame Count: {status['frame_count']}")
        
        # Capture frames
        print("\nCapturing frames...")
        for i in range(3):
            frame = camera.capture_frame()
            if frame:
                print(f"  Frame {i+1} captured: {len(frame)} bytes")
        
        # Adjust settings
        print("\nAdjusting camera settings...")
        camera.set_quality(10)
        camera.set_brightness(1)
        camera.set_flip(horizontal=False, vertical=False)
        print("✓ Settings updated")
        
        return camera
    else:
        print("✗ Camera initialization failed")
        return None


def demo_streaming(camera):
    """Demonstrate streaming capabilities."""
    print("\n" + "=" * 60)
    print("STREAMING DEMO")
    print("=" * 60)
    
    if not camera or not camera.initialized:
        print("✗ Camera not initialized")
        return None
    
    # MJPEG Streaming
    print("\n1. MJPEG Streaming")
    mjpeg_config = StreamConfig(
        protocol=StreamingProtocol.MJPEG,
        quality=StreamQuality.MEDIUM,
        port=8080,
        fps_target=15,
    )
    
    mjpeg_stream = StreamingManager(camera, mjpeg_config)
    stream_info = mjpeg_stream.start_stream("mjpeg_stream")
    
    print(f"  Status: {stream_info['status']}")
    print(f"  Protocol: {stream_info['protocol']}")
    print(f"  URLs:")
    for url_type, url in stream_info['urls'].items():
        print(f"    {url_type}: {url}")
    
    # RTSP Streaming
    print("\n2. RTSP Streaming")
    rtsp_config = StreamConfig(
        protocol=StreamingProtocol.RTSP,
        port=554,
        rtsp_path="/stream",
    )
    
    rtsp_stream = StreamingManager(camera, rtsp_config)
    rtsp_info = rtsp_stream.start_stream("rtsp_stream")
    print(f"  RTSP URL: {rtsp_info['urls'].get('rtsp', 'N/A')}")
    
    # WebRTC Streaming
    print("\n3. WebRTC Streaming")
    webrtc_config = StreamConfig(
        protocol=StreamingProtocol.WEBRTC,
        port=8443,
    )
    
    webrtc_stream = StreamingManager(camera, webrtc_config)
    webrtc_info = webrtc_stream.start_stream("webrtc_stream")
    print(f"  WebRTC URL: {webrtc_info['urls'].get('webrtc', 'N/A')}")
    
    # Stream statistics
    stats = mjpeg_stream.get_stream_stats()
    print(f"\nStreaming Statistics:")
    print(f"  Active Streams: {stats['active_streams']}")
    print(f"  Total Frames: {stats['total_frames']}")
    
    return mjpeg_stream


def demo_ai_processing(camera):
    """Demonstrate AI processing capabilities."""
    print("\n" + "=" * 60)
    print("AI PROCESSING DEMO")
    print("=" * 60)
    
    if not camera or not camera.initialized:
        print("✗ Camera not initialized")
        return None
    
    # Person Detection
    print("\n1. Person Detection")
    person_config = ModelConfig(
        model_type=DetectionModel.PERSON_DETECTION,
        confidence_threshold=0.7,
        input_width=96,
        input_height=96,
    )
    
    person_ai = AIProcessor(camera, person_config)
    if person_ai.load_model():
        print("  ✓ Model loaded successfully")
        
        detections = person_ai.detect()
        print(f"  Detections: {len(detections)}")
        for det in detections:
            print(f"    - {det.label}: {det.confidence:.2f}")
    
    # Face Detection
    print("\n2. Face Detection")
    face_config = ModelConfig(
        model_type=DetectionModel.FACE_DETECTION,
        confidence_threshold=0.8,
    )
    
    face_ai = AIProcessor(camera, face_config)
    if face_ai.load_model():
        print("  ✓ Face detection model loaded")
        
        detections = face_ai.detect()
        print(f"  Faces detected: {len(detections)}")
    
    # AI Statistics
    stats = person_ai.get_statistics()
    print(f"\nAI Statistics:")
    print(f"  Model Type: {stats['model_type']}")
    print(f"  Backend: {stats['backend']}")
    print(f"  Inference Count: {stats['inference_count']}")
    print(f"  Total Detections: {stats['total_detections']}")
    
    # TinyML Integration
    print("\n3. TinyML Agent Integration")
    tinyml_spec = person_ai.integrate_with_tinyml_agent()
    print(f"  Platform: {tinyml_spec['platform']}")
    print(f"  Model Type: {tinyml_spec['model_type']}")
    print(f"  Optimization: {tinyml_spec['optimization_level']}")
    
    return person_ai


def demo_motion_detection(camera):
    """Demonstrate motion detection."""
    print("\n" + "=" * 60)
    print("MOTION DETECTION DEMO")
    print("=" * 60)
    
    if not camera or not camera.initialized:
        print("✗ Camera not initialized")
        return None
    
    # Setup motion detection
    motion_config = MotionConfig(
        algorithm=MotionAlgorithm.FRAME_DIFF,
        threshold=20,
        min_area=500,
        cooldown_seconds=5,
    )
    
    motion = MotionDetector(camera, motion_config)
    print(f"Algorithm: {motion_config.algorithm.value}")
    print(f"Threshold: {motion_config.threshold}")
    print(f"Min Area: {motion_config.min_area}")
    
    # Add event callback
    def motion_callback(event):
        print(f"\n  🔔 Motion Event!")
        print(f"     Timestamp: {event.timestamp}")
        print(f"     Confidence: {event.confidence:.2f}")
        print(f"     Area: {event.area}")
    
    motion.add_event_callback(motion_callback)
    
    # Detect motion
    print("\nDetecting motion (capturing frames)...")
    for i in range(5):
        detected = motion.detect_motion()
        if detected:
            print(f"  Frame {i+1}: Motion detected!")
        else:
            print(f"  Frame {i+1}: No motion")
    
    # Motion statistics
    stats = motion.get_statistics()
    print(f"\nMotion Statistics:")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Motion Detected: {stats['motion_detected']}")
    
    # QR Scanner
    print("\n" + "-" * 60)
    print("QR CODE SCANNING")
    print("-" * 60)
    
    scanner = QRScanner(camera)
    print("\nScanning for QR codes...")
    result = scanner.scan()
    
    if result:
        print(f"  ✓ QR Code detected!")
        print(f"    Type: {result['type']}")
        print(f"    Data: {result['data']}")
    else:
        print("  No QR codes found")
    
    return motion


def demo_remote_access(camera):
    """Demonstrate remote access capabilities."""
    print("\n" + "=" * 60)
    print("REMOTE ACCESS DEMO")
    print("=" * 60)
    
    if not camera or not camera.initialized:
        print("✗ Camera not initialized")
        return None
    
    # Setup authentication
    print("\n1. Authentication Configuration")
    auth_config = AuthConfig(
        method=AuthMethod.TOKEN,
        access_token="demo_secure_token_12345",
        allowed_ips=["192.168.1.0/24"],
        rate_limit_per_minute=60,
    )
    
    print(f"  Auth Method: {auth_config.method.value}")
    print(f"  Rate Limit: {auth_config.rate_limit_per_minute} req/min")
    print(f"  IP Whitelist: {auth_config.allowed_ips}")
    
    # Setup tunnel
    print("\n2. Cloud Tunnel Configuration")
    tunnel_config = TunnelConfig(
        tunnel_type=TunnelType.NGROK,
        enable_tls=True,
    )
    
    print(f"  Tunnel Type: {tunnel_config.tunnel_type.value}")
    print(f"  TLS Enabled: {tunnel_config.enable_tls}")
    
    # Create remote access
    remote = RemoteAccess(camera, auth_config, tunnel_config)
    
    # Start tunnel
    print("\n3. Starting Tunnel...")
    tunnel_info = remote.start_tunnel()
    
    if tunnel_info['status'] == 'active':
        print(f"  ✓ Tunnel active")
        print(f"  Public URL: {tunnel_info['public_url']}")
        print(f"  Secure: {tunnel_info['secure']}")
    else:
        print(f"  Status: {tunnel_info['status']}")
    
    # Test authentication
    print("\n4. Testing Authentication")
    
    # Valid token
    result = remote.authenticate({"token": "demo_secure_token_12345"})
    print(f"  Valid Token: {result['authenticated']}")
    
    # Invalid token
    result = remote.authenticate({"token": "wrong_token"})
    print(f"  Invalid Token: {result['authenticated']}")
    
    # Create session
    print("\n5. Session Management")
    session = remote.create_session("demo_user", "192.168.1.100")
    
    if session['status'] == 'success':
        print(f"  ✓ Session created")
        print(f"    Session ID: {session['session']['session_id']}")
        print(f"    User: {session['session']['user_id']}")
        print(f"    IP: {session['session']['ip_address']}")
    
    # Remote status
    status = remote.get_status()
    print(f"\nRemote Access Status:")
    print(f"  Tunnel Active: {status['tunnel_active']}")
    print(f"  Active Sessions: {status['active_sessions']}")
    
    return remote


def demo_web_interface(camera):
    """Demonstrate web interface."""
    print("\n" + "=" * 60)
    print("WEB INTERFACE DEMO")
    print("=" * 60)
    
    if not camera or not camera.initialized:
        print("✗ Camera not initialized")
        return None
    
    # Setup web interface
    api_config = APIConfig(
        port=80,
        enable_api=True,
        enable_web_ui=True,
        enable_cors=True,
    )
    
    web = WebInterface(camera, api_config)
    print(f"Port: {api_config.port}")
    print(f"API Enabled: {api_config.enable_api}")
    print(f"Web UI Enabled: {api_config.enable_web_ui}")
    
    # Test API endpoints
    print("\nTesting API Endpoints:")
    
    # Status endpoint
    print("\n1. GET /api/camera/status")
    response = web.handle_request("/api/camera/status", "GET", {})
    print(f"   Status Code: {response['code']}")
    print(f"   Response: {response['status']}")
    
    # Capture endpoint
    print("\n2. GET /api/camera/capture")
    response = web.handle_request("/api/camera/capture", "GET", {})
    print(f"   Status Code: {response['code']}")
    print(f"   Message: {response.get('message', 'N/A')}")
    
    # Set quality
    print("\n3. PUT /api/settings/quality")
    response = web.handle_request(
        "/api/settings/quality",
        "PUT",
        {"quality": 15}
    )
    print(f"   Status Code: {response['code']}")
    print(f"   New Quality: {response.get('quality', 'N/A')}")
    
    # UI Pages
    print("\nWeb UI Pages:")
    print("  / - Home page")
    print("  /ui/live - Live view")
    print("  /ui/settings - Settings page")
    
    # Statistics
    stats = web.get_statistics()
    print(f"\nWeb Interface Statistics:")
    print(f"  Request Count: {stats['request_count']}")
    print(f"  Registered Routes: {stats['registered_routes']}")
    
    return web


def demo_firmware_generation(camera):
    """Demonstrate firmware code generation."""
    print("\n" + "=" * 60)
    print("FIRMWARE GENERATION DEMO")
    print("=" * 60)
    
    if not camera:
        print("✗ Camera not initialized")
        return
    
    print("\nGenerating firmware code...")
    
    # Camera configuration
    print("\n1. Camera Configuration Code")
    camera_code = camera.generate_firmware_config()
    print(f"   Length: {len(camera_code)} characters")
    print("   Includes:")
    print("   - Pin configuration")
    print("   - Sensor settings")
    print("   - Camera initialization")
    
    # Streaming code
    print("\n2. Streaming Code")
    streaming = StreamingManager(camera)
    stream_code = streaming.generate_streaming_code()
    print(f"   Files generated: {len(stream_code)}")
    for filename in stream_code.keys():
        print(f"   - {filename}")
    
    # AI inference code
    print("\n3. AI Inference Code")
    ai = AIProcessor(camera)
    ai_code = ai.generate_inference_code()
    print(f"   Files generated: {len(ai_code)}")
    for filename in ai_code.keys():
        print(f"   - {filename}")
    
    # Motion detection code
    print("\n4. Motion Detection Code")
    motion = MotionDetector(camera)
    motion_code = motion.generate_motion_detection_code()
    print(f"   Files generated: {len(motion_code)}")
    for filename in motion_code.keys():
        print(f"   - {filename}")
    
    print("\n✓ All firmware code generated successfully")


def main():
    """Run complete ESP32-CAM demo."""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  ESP32-CAM COMPREHENSIVE DEMO".center(58) + "*")
    print("*" + "  Accelerapp Hardware Control Platform".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    
    try:
        # 1. Basic camera operations
        camera = demo_basic_camera()
        
        if camera:
            # 2. Streaming
            streaming = demo_streaming(camera)
            
            # 3. AI processing
            ai = demo_ai_processing(camera)
            
            # 4. Motion detection
            motion = demo_motion_detection(camera)
            
            # 5. Remote access
            remote = demo_remote_access(camera)
            
            # 6. Web interface
            web = demo_web_interface(camera)
            
            # 7. Firmware generation
            demo_firmware_generation(camera)
            
            # Summary
            print("\n" + "=" * 60)
            print("DEMO SUMMARY")
            print("=" * 60)
            print("\n✓ All ESP32-CAM features demonstrated successfully!")
            print("\nFeatures tested:")
            print("  ✓ Camera initialization and configuration")
            print("  ✓ Multi-protocol streaming (MJPEG, RTSP, WebRTC)")
            print("  ✓ AI processing with TinyML")
            print("  ✓ Motion detection and QR scanning")
            print("  ✓ Remote access with authentication")
            print("  ✓ Web interface and REST API")
            print("  ✓ Firmware code generation")
            
            print("\nNext steps:")
            print("  - See docs/ESP32_CAM_GUIDE.md for detailed documentation")
            print("  - Check examples/ for more specific examples")
            print("  - Run tests with: pytest tests/test_esp32_cam.py")
            
        else:
            print("\n✗ Demo failed - camera initialization error")
    
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "*" * 60 + "\n")


if __name__ == "__main__":
    main()
