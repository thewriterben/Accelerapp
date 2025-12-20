"""
Core ESP32-CAM module providing camera interface and configuration.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field


class CameraModel(Enum):
    """Camera sensor model types."""

    OV2640 = "OV2640"
    OV3660 = "OV3660"
    OV5640 = "OV5640"


class FrameFormat(Enum):
    """Camera frame formats."""

    JPEG = "jpeg"
    RGB565 = "rgb565"
    GRAYSCALE = "grayscale"
    RAW = "raw"


class FrameSize(Enum):
    """Camera frame sizes."""

    QQVGA = "160x120"  # 160x120
    QVGA = "320x240"  # 320x240
    VGA = "640x480"  # 640x480
    SVGA = "800x600"  # 800x600
    XGA = "1024x768"  # 1024x768
    HD = "1280x720"  # 1280x720
    SXGA = "1280x1024"  # 1280x1024
    UXGA = "1600x1200"  # 1600x1200


class CameraVariant(Enum):
    """ESP32-CAM board variants."""

    AI_THINKER = "ai_thinker"
    WROVER_KIT = "wrover_kit"
    ESP_EYE = "esp_eye"
    M5STACK_CAMERA = "m5stack_camera"
    ESP32_S3_CAM = "esp32_s3_cam"


class CameraSensor(Enum):
    """Camera sensor types."""

    OV2640 = "OV2640"
    OV3660 = "OV3660"
    OV5640 = "OV5640"


class PixelFormat(Enum):
    """Pixel format options."""

    JPEG = "JPEG"
    RGB565 = "RGB565"
    GRAYSCALE = "GRAYSCALE"


@dataclass
class CameraConfig:
    """Camera configuration."""

    variant: CameraVariant = CameraVariant.AI_THINKER
    sensor: CameraSensor = CameraSensor.OV2640
    frame_size: FrameSize = FrameSize.VGA
    pixel_format: PixelFormat = PixelFormat.JPEG
    jpeg_quality: int = 12  # 0-63, lower is better
    brightness: int = 0  # -2 to 2
    contrast: int = 0  # -2 to 2
    saturation: int = 0  # -2 to 2
    horizontal_flip: bool = False
    vertical_flip: bool = False

    # Digital twin integration
    twin_id: Optional[str] = None
    twin_sync_interval: int = 60

    # Observability
    enable_metrics: bool = False
    enable_health_checks: bool = False

    # Pin configuration (variant-specific)
    pin_config: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Set default pin configuration based on variant."""
        if not self.pin_config:
            if self.variant == CameraVariant.AI_THINKER:
                self.pin_config = {
                    "PWDN": 32,
                    "RESET": -1,
                    "XCLK": 0,
                    "SIOD": 26,
                    "SIOC": 27,
                    "Y9": 35,
                    "Y8": 34,
                    "Y7": 39,
                    "Y6": 36,
                    "Y5": 21,
                    "Y4": 19,
                    "Y3": 18,
                    "Y2": 5,
                    "VSYNC": 25,
                    "HREF": 23,
                    "PCLK": 22,
                }
            elif self.variant == CameraVariant.ESP32_S3_CAM:
                self.pin_config = {
                    "PWDN": -1,
                    "RESET": -1,
                    "XCLK": 15,
                    "SIOD": 4,
                    "SIOC": 5,
                    "Y9": 16,
                    "Y8": 17,
                    "Y7": 18,
                    "Y6": 12,
                    "Y5": 10,
                    "Y4": 8,
                    "Y3": 9,
                    "Y2": 11,
                    "VSYNC": 6,
                    "HREF": 7,
                    "PCLK": 13,
                }


class ESP32Camera:
    """
    ESP32-CAM interface for camera control and configuration.
    Supports multiple camera variants and sensors.
    """

    def __init__(self, config: Optional[CameraConfig] = None):
        """
        Initialize ESP32-CAM interface.

        Args:
            config: Camera configuration
        """
        self.config = config or CameraConfig()
        self.initialized = False
        self.frame_count = 0
        self._last_frame = None

    def initialize(self) -> bool:
        """
        Initialize camera hardware.

        Returns:
            True if initialization successful
        """
        # In real implementation, would call esp_camera_init()
        self.initialized = True
        return True

    def _validate_config(self) -> bool:
        """
        Validate camera configuration.

        Returns:
            True if configuration is valid
        """
        if self.config.jpeg_quality < 0 or self.config.jpeg_quality > 63:
            return False
        if self.config.brightness < -2 or self.config.brightness > 2:
            return False
        return True

    def capture_frame(self) -> Optional[bytes]:
        """
        Capture a single frame.

        Returns:
            Frame data as bytes, or None if failed
        """
        if not self.initialized:
            return None

        # Simulated frame capture
        self.frame_count += 1
        self._last_frame = b"FRAME_DATA_PLACEHOLDER"
        return self._last_frame

    def set_quality(self, quality: int) -> bool:
        """
        Set JPEG quality.

        Args:
            quality: Quality value (0-63, lower is better)

        Returns:
            True if set successfully
        """
        if quality < 0 or quality > 63:
            return False
        self.config.jpeg_quality = quality
        return True

    def set_brightness(self, brightness: int) -> bool:
        """
        Set image brightness.

        Args:
            brightness: Brightness value (-2 to 2)

        Returns:
            True if set successfully
        """
        if brightness < -2 or brightness > 2:
            return False
        self.config.brightness = brightness
        return True

    def set_flip(self, horizontal: bool = False, vertical: bool = False) -> bool:
        """
        Set image flip settings.

        Args:
            horizontal: Enable horizontal flip
            vertical: Enable vertical flip

        Returns:
            True if set successfully
        """
        self.config.horizontal_flip = horizontal
        self.config.vertical_flip = vertical
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
            "frame_count": self.frame_count,
            "jpeg_quality": self.config.jpeg_quality,
            "brightness": self.config.brightness,
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get current camera configuration.

        Returns:
            Configuration dictionary
        """
        return {
            "variant": self.config.variant.value,
            "sensor": self.config.sensor.value,
            "frame_size": self.config.frame_size.value,
            "pixel_format": self.config.pixel_format.value,
            "jpeg_quality": self.config.jpeg_quality,
            "brightness": self.config.brightness,
            "contrast": self.config.contrast,
            "saturation": self.config.saturation,
            "horizontal_flip": self.config.horizontal_flip,
            "vertical_flip": self.config.vertical_flip,
            "twin_id": self.config.twin_id,
            "enable_metrics": self.config.enable_metrics,
            "enable_health_checks": self.config.enable_health_checks,
        }

    def generate_firmware_config(self) -> str:
        """
        Generate ESP32 firmware configuration code.

        Returns:
            C code string for camera configuration
        """
        pins = self.config.pin_config
        code = f"""
// Camera configuration for {self.config.variant.value}
#include <esp_camera.h>

camera_config_t camera_config = {{
    .pin_pwdn = {pins.get('PWDN', -1)},
    .pin_reset = {pins.get('RESET', -1)},
    .pin_xclk = {pins.get('XCLK', 0)},
    .pin_sscb_sda = {pins.get('SIOD', 26)},
    .pin_sscb_scl = {pins.get('SIOC', 27)},
    .pin_d7 = {pins.get('Y9', 35)},
    .pin_d6 = {pins.get('Y8', 34)},
    .pin_d5 = {pins.get('Y7', 39)},
    .pin_d4 = {pins.get('Y6', 36)},
    .pin_d3 = {pins.get('Y5', 21)},
    .pin_d2 = {pins.get('Y4', 19)},
    .pin_d1 = {pins.get('Y3', 18)},
    .pin_d0 = {pins.get('Y2', 5)},
    .pin_vsync = {pins.get('VSYNC', 25)},
    .pin_href = {pins.get('HREF', 23)},
    .pin_pclk = {pins.get('PCLK', 22)},
    .xclk_freq_hz = 20000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,
    .pixel_format = PIXFORMAT_JPEG,
    .frame_size = FRAMESIZE_VGA,
    .jpeg_quality = {self.config.jpeg_quality},
    .fb_count = 2,
}};

void init_camera() {{
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {{
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }}
    Serial.println("Camera initialized successfully");
}}
"""
        return code
