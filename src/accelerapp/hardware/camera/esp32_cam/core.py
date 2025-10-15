"""
Core ESP32-CAM module with multi-variant support and advanced camera interface.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class CameraVariant(Enum):
    """Supported ESP32-CAM board variants."""
    AI_THINKER = "ai_thinker"
    TTGO_T_CAMERA = "ttgo_t_camera"
    TTGO_T_JOURNAL = "ttgo_t_journal"
    M5STACK_CAMERA = "m5stack_camera"
    WROVER_KIT = "wrover_kit"
    ESP_EYE = "esp_eye"
    GENERIC = "generic"


class CameraSensor(Enum):
    """Supported camera sensors."""
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    OV3660 = "ov3660"
    OV7670 = "ov7670"


class FrameSize(Enum):
    """Camera frame sizes."""
    QQVGA = "160x120"     # 160x120
    QCIF = "176x144"      # 176x144
    HQVGA = "240x176"     # 240x176
    QVGA = "320x240"      # 320x240
    CIF = "400x296"       # 400x296
    VGA = "640x480"       # 640x480
    SVGA = "800x600"      # 800x600
    XGA = "1024x768"      # 1024x768
    SXGA = "1280x1024"    # 1280x1024
    UXGA = "1600x1200"    # 1600x1200


class PixelFormat(Enum):
    """Camera pixel formats."""
    RGB565 = "rgb565"
    YUV422 = "yuv422"
    GRAYSCALE = "grayscale"
    JPEG = "jpeg"
    RGB888 = "rgb888"


@dataclass
class CameraConfig:
    """ESP32-CAM configuration."""
    variant: CameraVariant = CameraVariant.AI_THINKER
    sensor: CameraSensor = CameraSensor.OV2640
    frame_size: FrameSize = FrameSize.VGA
    pixel_format: PixelFormat = PixelFormat.JPEG
    jpeg_quality: int = 12  # 0-63, lower is higher quality
    fb_count: int = 2  # Frame buffer count
    
    # Camera settings
    brightness: int = 0  # -2 to 2
    contrast: int = 0    # -2 to 2
    saturation: int = 0  # -2 to 2
    sharpness: int = 0   # -2 to 2
    
    # Advanced settings
    auto_exposure: bool = True
    auto_white_balance: bool = True
    auto_white_balance_gain: bool = True
    exposure_ctrl_sensor: bool = True
    gain_ctrl: bool = True
    
    # Flip and mirror
    horizontal_flip: bool = False
    vertical_flip: bool = False
    
    # Pin configuration (AI-Thinker defaults)
    pin_pwdn: int = 32
    pin_reset: int = -1
    pin_xclk: int = 0
    pin_sscb_sda: int = 26
    pin_sscb_scl: int = 27
    
    pin_d7: int = 35
    pin_d6: int = 34
    pin_d5: int = 39
    pin_d4: int = 36
    pin_d3: int = 21
    pin_d2: int = 19
    pin_d1: int = 18
    pin_d0: int = 5
    pin_vsync: int = 25
    pin_href: int = 23
    pin_pclk: int = 22
    
    xclk_freq_hz: int = 20000000
    ledc_timer: int = 0
    ledc_channel: int = 0
    
    # Digital twin integration
    twin_id: Optional[str] = None
    twin_sync_interval: int = 60  # seconds
    
    # Observability
    enable_metrics: bool = True
    enable_health_checks: bool = True
    
    # Custom metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ESP32Camera:
    """
    ESP32-CAM interface with comprehensive feature support.
    Supports multiple variants, sensors, and advanced camera operations.
    """
    
    def __init__(self, config: Optional[CameraConfig] = None):
        """
        Initialize ESP32-CAM interface.
        
        Args:
            config: Camera configuration, defaults to AI-Thinker variant
        """
        self.config = config or CameraConfig()
        self.initialized = False
        self.frame_count = 0
        self.error_count = 0
        
        # Apply variant-specific pin configurations
        self._apply_variant_config()
        
        logger.info(f"ESP32Camera initialized with variant: {self.config.variant.value}")
    
    def _apply_variant_config(self):
        """Apply pin configuration based on camera variant."""
        variant_configs = {
            CameraVariant.AI_THINKER: {
                "pin_pwdn": 32, "pin_reset": -1, "pin_xclk": 0,
                "pin_sscb_sda": 26, "pin_sscb_scl": 27,
                "pin_d7": 35, "pin_d6": 34, "pin_d5": 39, "pin_d4": 36,
                "pin_d3": 21, "pin_d2": 19, "pin_d1": 18, "pin_d0": 5,
                "pin_vsync": 25, "pin_href": 23, "pin_pclk": 22,
            },
            CameraVariant.WROVER_KIT: {
                "pin_pwdn": -1, "pin_reset": -1, "pin_xclk": 21,
                "pin_sscb_sda": 26, "pin_sscb_scl": 27,
                "pin_d7": 35, "pin_d6": 34, "pin_d5": 39, "pin_d4": 36,
                "pin_d3": 19, "pin_d2": 18, "pin_d1": 5, "pin_d0": 4,
                "pin_vsync": 25, "pin_href": 23, "pin_pclk": 22,
            },
            CameraVariant.ESP_EYE: {
                "pin_pwdn": -1, "pin_reset": -1, "pin_xclk": 4,
                "pin_sscb_sda": 18, "pin_sscb_scl": 23,
                "pin_d7": 36, "pin_d6": 37, "pin_d5": 38, "pin_d4": 39,
                "pin_d3": 35, "pin_d2": 14, "pin_d1": 13, "pin_d0": 34,
                "pin_vsync": 5, "pin_href": 27, "pin_pclk": 25,
            },
            CameraVariant.M5STACK_CAMERA: {
                "pin_pwdn": -1, "pin_reset": 15, "pin_xclk": 27,
                "pin_sscb_sda": 25, "pin_sscb_scl": 23,
                "pin_d7": 19, "pin_d6": 36, "pin_d5": 18, "pin_d4": 39,
                "pin_d3": 5, "pin_d2": 34, "pin_d1": 35, "pin_d0": 32,
                "pin_vsync": 22, "pin_href": 26, "pin_pclk": 21,
            },
        }
        
        if self.config.variant in variant_configs:
            for key, value in variant_configs[self.config.variant].items():
                setattr(self.config, key, value)
    
    def initialize(self) -> bool:
        """
        Initialize camera hardware.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing ESP32-CAM hardware...")
            
            # Validate configuration
            if not self._validate_config():
                logger.error("Camera configuration validation failed")
                return False
            
            # In production, this would initialize the actual hardware
            # For now, we simulate successful initialization
            self.initialized = True
            logger.info("ESP32-CAM initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.error_count += 1
            return False
    
    def _validate_config(self) -> bool:
        """Validate camera configuration."""
        # Check JPEG quality range
        if not 0 <= self.config.jpeg_quality <= 63:
            logger.error(f"Invalid JPEG quality: {self.config.jpeg_quality}")
            return False
        
        # Check frame buffer count
        if not 1 <= self.config.fb_count <= 2:
            logger.error(f"Invalid frame buffer count: {self.config.fb_count}")
            return False
        
        # Check camera settings ranges
        for setting in ['brightness', 'contrast', 'saturation', 'sharpness']:
            value = getattr(self.config, setting)
            if not -2 <= value <= 2:
                logger.error(f"Invalid {setting}: {value}")
                return False
        
        return True
    
    def capture_frame(self) -> Optional[bytes]:
        """
        Capture a single frame from the camera.
        
        Returns:
            Frame data as bytes, or None if capture failed
        """
        if not self.initialized:
            logger.error("Camera not initialized")
            return None
        
        try:
            # In production, this would capture from actual hardware
            self.frame_count += 1
            logger.debug(f"Frame captured: {self.frame_count}")
            
            # Return placeholder data
            return b"JPEG_FRAME_DATA"
            
        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            self.error_count += 1
            return None
    
    def set_quality(self, quality: int) -> bool:
        """
        Set JPEG quality.
        
        Args:
            quality: JPEG quality (0-63, lower is better)
        
        Returns:
            True if successful
        """
        if not 0 <= quality <= 63:
            logger.error(f"Invalid quality value: {quality}")
            return False
        
        self.config.jpeg_quality = quality
        logger.info(f"JPEG quality set to: {quality}")
        return True
    
    def set_frame_size(self, frame_size: FrameSize) -> bool:
        """
        Set frame size.
        
        Args:
            frame_size: Target frame size
        
        Returns:
            True if successful
        """
        self.config.frame_size = frame_size
        logger.info(f"Frame size set to: {frame_size.value}")
        return True
    
    def set_brightness(self, brightness: int) -> bool:
        """Set brightness (-2 to 2)."""
        if not -2 <= brightness <= 2:
            return False
        self.config.brightness = brightness
        return True
    
    def set_contrast(self, contrast: int) -> bool:
        """Set contrast (-2 to 2)."""
        if not -2 <= contrast <= 2:
            return False
        self.config.contrast = contrast
        return True
    
    def set_flip(self, horizontal: bool = False, vertical: bool = False) -> bool:
        """Set image flip settings."""
        self.config.horizontal_flip = horizontal
        self.config.vertical_flip = vertical
        logger.info(f"Flip settings: H={horizontal}, V={vertical}")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera status and statistics.
        
        Returns:
            Status dictionary
        """
        return {
            "initialized": self.initialized,
            "variant": self.config.variant.value,
            "sensor": self.config.sensor.value,
            "frame_size": self.config.frame_size.value,
            "pixel_format": self.config.pixel_format.value,
            "frame_count": self.frame_count,
            "error_count": self.error_count,
            "jpeg_quality": self.config.jpeg_quality,
            "twin_id": self.config.twin_id,
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "variant": self.config.variant.value,
            "sensor": self.config.sensor.value,
            "frame_size": self.config.frame_size.value,
            "pixel_format": self.config.pixel_format.value,
            "jpeg_quality": self.config.jpeg_quality,
            "fb_count": self.config.fb_count,
            "brightness": self.config.brightness,
            "contrast": self.config.contrast,
            "saturation": self.config.saturation,
            "sharpness": self.config.sharpness,
            "auto_exposure": self.config.auto_exposure,
            "horizontal_flip": self.config.horizontal_flip,
            "vertical_flip": self.config.vertical_flip,
        }
    
    def generate_firmware_config(self) -> str:
        """
        Generate ESP32 firmware configuration code.
        
        Returns:
            C/C++ configuration code
        """
        lines = [
            "// ESP32-CAM Configuration",
            "// Auto-generated by Accelerapp",
            "",
            "#include <esp_camera.h>",
            "",
            "// Camera configuration",
            "static camera_config_t camera_config = {",
            f"    .pin_pwdn = {self.config.pin_pwdn},",
            f"    .pin_reset = {self.config.pin_reset},",
            f"    .pin_xclk = {self.config.pin_xclk},",
            f"    .pin_sscb_sda = {self.config.pin_sscb_sda},",
            f"    .pin_sscb_scl = {self.config.pin_sscb_scl},",
            "",
            f"    .pin_d7 = {self.config.pin_d7},",
            f"    .pin_d6 = {self.config.pin_d6},",
            f"    .pin_d5 = {self.config.pin_d5},",
            f"    .pin_d4 = {self.config.pin_d4},",
            f"    .pin_d3 = {self.config.pin_d3},",
            f"    .pin_d2 = {self.config.pin_d2},",
            f"    .pin_d1 = {self.config.pin_d1},",
            f"    .pin_d0 = {self.config.pin_d0},",
            f"    .pin_vsync = {self.config.pin_vsync},",
            f"    .pin_href = {self.config.pin_href},",
            f"    .pin_pclk = {self.config.pin_pclk},",
            "",
            f"    .xclk_freq_hz = {self.config.xclk_freq_hz},",
            f"    .ledc_timer = LEDC_TIMER_{self.config.ledc_timer},",
            f"    .ledc_channel = LEDC_CHANNEL_{self.config.ledc_channel},",
            "",
            f"    .pixel_format = PIXFORMAT_{self.config.pixel_format.name},",
            f"    .frame_size = FRAMESIZE_{self.config.frame_size.name},",
            f"    .jpeg_quality = {self.config.jpeg_quality},",
            f"    .fb_count = {self.config.fb_count},",
            "};",
            "",
            "// Initialize camera",
            "esp_err_t camera_init() {",
            "    esp_err_t err = esp_camera_init(&camera_config);",
            "    if (err != ESP_OK) {",
            "        return err;",
            "    }",
            "",
            "    // Apply sensor settings",
            "    sensor_t *s = esp_camera_sensor_get();",
            f"    s->set_brightness(s, {self.config.brightness});",
            f"    s->set_contrast(s, {self.config.contrast});",
            f"    s->set_saturation(s, {self.config.saturation});",
            f"    s->set_sharpness(s, {self.config.sharpness});",
            f"    s->set_hmirror(s, {1 if self.config.horizontal_flip else 0});",
            f"    s->set_vflip(s, {1 if self.config.vertical_flip else 0});",
            "",
            "    return ESP_OK;",
            "}",
            "",
        ]
        
        return "\n".join(lines)
    
    def shutdown(self):
        """Shutdown camera and release resources."""
        if self.initialized:
            logger.info("Shutting down ESP32-CAM")
            self.initialized = False
