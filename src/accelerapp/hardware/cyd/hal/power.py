"""
Power Management for CYD.

Provides power control and energy monitoring capabilities
for ESP32 Cheap Yellow Display boards.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PowerMode(Enum):
    """Power management modes."""
    ACTIVE = "active"
    LIGHT_SLEEP = "light_sleep"
    DEEP_SLEEP = "deep_sleep"
    MODEM_SLEEP = "modem_sleep"


@dataclass
class PowerConfig:
    """Power management configuration."""
    default_mode: PowerMode = PowerMode.ACTIVE
    auto_sleep_timeout: int = 300  # seconds
    wake_on_touch: bool = True
    wake_on_gpio: bool = False
    wake_gpio_pin: Optional[int] = None
    display_timeout: int = 60  # seconds


class PowerManager:
    """
    Power management for CYD hardware.
    
    Provides capabilities for:
    - Power mode control (active, light sleep, deep sleep)
    - Energy monitoring and statistics
    - Display backlight management
    - Wake-up source configuration
    - Battery status (if applicable)
    - Automatic power saving
    """

    def __init__(self, config: Optional[PowerConfig] = None):
        """
        Initialize power manager.
        
        Args:
            config: Power configuration (uses defaults if None)
        """
        self.config = config or PowerConfig()
        self._current_mode = PowerMode.ACTIVE
        self._uptime_start = datetime.now()
        self._sleep_count = 0
        self._total_sleep_time = 0
        self._display_on = True

    def set_power_mode(self, mode: PowerMode) -> bool:
        """
        Set device power mode.
        
        Args:
            mode: Target power mode
            
        Returns:
            True if mode change successful
        """
        self._current_mode = mode
        return True

    def get_power_mode(self) -> PowerMode:
        """
        Get current power mode.
        
        Returns:
            Current power mode
        """
        return self._current_mode

    def enter_light_sleep(self, duration_ms: Optional[int] = None) -> bool:
        """
        Enter light sleep mode.
        
        Args:
            duration_ms: Sleep duration in milliseconds (None for indefinite)
            
        Returns:
            True if sleep entry successful
        """
        self._sleep_count += 1
        self._current_mode = PowerMode.LIGHT_SLEEP
        return True

    def enter_deep_sleep(self, duration_ms: Optional[int] = None) -> bool:
        """
        Enter deep sleep mode.
        
        Args:
            duration_ms: Sleep duration in milliseconds (None for indefinite)
            
        Returns:
            True if sleep entry successful
        """
        self._sleep_count += 1
        self._current_mode = PowerMode.DEEP_SLEEP
        return True

    def configure_wake_source(
        self,
        touch: bool = True,
        gpio: bool = False,
        gpio_pin: Optional[int] = None,
        timer: bool = False,
        timer_ms: Optional[int] = None
    ) -> bool:
        """
        Configure wake-up sources.
        
        Args:
            touch: Enable wake on touch
            gpio: Enable wake on GPIO
            gpio_pin: GPIO pin for wake-up
            timer: Enable timer wake-up
            timer_ms: Timer duration in milliseconds
            
        Returns:
            True if configuration successful
        """
        self.config.wake_on_touch = touch
        self.config.wake_on_gpio = gpio
        self.config.wake_gpio_pin = gpio_pin
        return True

    def set_display_power(self, enabled: bool) -> bool:
        """
        Control display backlight power.
        
        Args:
            enabled: True to turn on, False to turn off
            
        Returns:
            True if power control successful
        """
        self._display_on = enabled
        return True

    def get_display_power(self) -> bool:
        """
        Get display power state.
        
        Returns:
            True if display is on
        """
        return self._display_on

    def get_uptime(self) -> float:
        """
        Get device uptime in seconds.
        
        Returns:
            Uptime in seconds
        """
        delta = datetime.now() - self._uptime_start
        return delta.total_seconds()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get power management statistics.
        
        Returns:
            Dictionary of power statistics
        """
        uptime = self.get_uptime()
        return {
            "uptime_seconds": uptime,
            "current_mode": self._current_mode.value,
            "sleep_count": self._sleep_count,
            "total_sleep_time": self._total_sleep_time,
            "display_on": self._display_on,
            "wake_sources": {
                "touch": self.config.wake_on_touch,
                "gpio": self.config.wake_on_gpio,
                "gpio_pin": self.config.wake_gpio_pin,
            },
        }

    def estimate_power_consumption(self) -> Dict[str, float]:
        """
        Estimate current power consumption.
        
        Returns:
            Dictionary with power consumption estimates (mW)
        """
        # Typical ESP32 power consumption estimates
        base_consumption = {
            PowerMode.ACTIVE: 160.0,  # ~80mA @ 5V
            PowerMode.MODEM_SLEEP: 30.0,  # ~15mA @ 5V
            PowerMode.LIGHT_SLEEP: 3.0,  # ~0.8mA @ 5V
            PowerMode.DEEP_SLEEP: 0.5,  # ~0.15mA @ 5V
        }
        
        cpu = base_consumption.get(self._current_mode, 160.0)
        display = 75.0 if self._display_on else 0.0  # TFT backlight
        
        return {
            "cpu_mw": cpu,
            "display_mw": display,
            "total_mw": cpu + display,
        }

    def generate_code(self, platform: str = "arduino") -> str:
        """
        Generate platform-specific power management code.
        
        Args:
            platform: Target platform (arduino, esp-idf, micropython)
            
        Returns:
            Generated code string
        """
        if platform == "arduino":
            return self._generate_arduino_code()
        elif platform == "esp-idf":
            return self._generate_esp_idf_code()
        elif platform == "micropython":
            return self._generate_micropython_code()
        else:
            return ""

    def _generate_arduino_code(self) -> str:
        """Generate Arduino power management code."""
        code = f"""// Power Management Configuration
#include <esp_sleep.h>

#define DISPLAY_TIMEOUT {self.config.display_timeout}  // seconds
#define AUTO_SLEEP_TIMEOUT {self.config.auto_sleep_timeout}  // seconds

unsigned long lastActivityTime = 0;
bool displayOn = true;

void setupPowerManagement() {{
    // Configure wake-up sources
"""
        
        if self.config.wake_on_touch:
            code += """    esp_sleep_enable_touchpad_wakeup();
"""
        
        if self.config.wake_on_gpio and self.config.wake_gpio_pin is not None:
            code += f"""    esp_sleep_enable_ext0_wakeup(GPIO_NUM_{self.config.wake_gpio_pin}, 1);
"""
        
        code += """}

void enterLightSleep(uint64_t duration_ms) {
    if (duration_ms > 0) {
        esp_sleep_enable_timer_wakeup(duration_ms * 1000);
    }
    esp_light_sleep_start();
}

void enterDeepSleep(uint64_t duration_ms) {
    if (duration_ms > 0) {
        esp_sleep_enable_timer_wakeup(duration_ms * 1000);
    }
    esp_deep_sleep_start();
}

void checkPowerTimeout() {
    unsigned long currentTime = millis();
    unsigned long idleTime = (currentTime - lastActivityTime) / 1000;
    
    // Auto-dim display
    if (displayOn && idleTime > DISPLAY_TIMEOUT) {
        digitalWrite(21, LOW);  // Turn off backlight
        displayOn = false;
    }
    
    // Auto-sleep
    if (idleTime > AUTO_SLEEP_TIMEOUT) {
        enterLightSleep(0);  // Sleep indefinitely
    }
}

void resetActivityTimer() {
    lastActivityTime = millis();
    if (!displayOn) {
        digitalWrite(21, HIGH);  // Turn on backlight
        displayOn = true;
    }
}
"""
        return code.strip()

    def _generate_esp_idf_code(self) -> str:
        """Generate ESP-IDF power management code."""
        code = f"""// Power Management Configuration for ESP-IDF
#include "esp_sleep.h"
#include "driver/rtc_io.h"
#include "driver/touch_pad.h"

#define DISPLAY_TIMEOUT_MS {self.config.display_timeout * 1000}
#define AUTO_SLEEP_TIMEOUT_MS {self.config.auto_sleep_timeout * 1000}

void power_management_init() {{
"""
        
        if self.config.wake_on_touch:
            code += """    // Configure touch wake-up
    esp_sleep_enable_touchpad_wakeup();
"""
        
        if self.config.wake_on_gpio and self.config.wake_gpio_pin is not None:
            code += f"""    // Configure GPIO wake-up
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_{self.config.wake_gpio_pin}, 1);
    rtc_gpio_pullup_en(GPIO_NUM_{self.config.wake_gpio_pin});
"""
        
        code += """}

void enter_light_sleep(uint64_t duration_ms) {
    if (duration_ms > 0) {
        esp_sleep_enable_timer_wakeup(duration_ms * 1000);
    }
    esp_light_sleep_start();
}

void enter_deep_sleep(uint64_t duration_ms) {
    if (duration_ms > 0) {
        esp_sleep_enable_timer_wakeup(duration_ms * 1000);
    }
    esp_deep_sleep_start();
}

void set_display_power(bool enabled) {
    gpio_set_level(GPIO_NUM_21, enabled ? 1 : 0);
}
"""
        return code.strip()

    def _generate_micropython_code(self) -> str:
        """Generate MicroPython power management code."""
        code = f"""# Power Management Configuration for MicroPython
from machine import Pin, deepsleep, lightsleep
import esp32

DISPLAY_TIMEOUT = {self.config.display_timeout}  # seconds
AUTO_SLEEP_TIMEOUT = {self.config.auto_sleep_timeout}  # seconds

display_bl = Pin(21, Pin.OUT)
display_on = True

def setup_power_management():
"""
        
        if self.config.wake_on_touch:
            code += """    # Configure touch wake-up
    esp32.wake_on_touch(True)
"""
        
        if self.config.wake_on_gpio and self.config.wake_gpio_pin is not None:
            code += f"""    # Configure GPIO wake-up
    wake_pin = Pin({self.config.wake_gpio_pin}, Pin.IN, Pin.PULL_UP)
    esp32.wake_on_ext0(wake_pin, esp32.WAKEUP_ANY_HIGH)
"""
        else:
            code += """    pass
"""
        
        code += """
def enter_light_sleep(duration_ms=None):
    if duration_ms:
        lightsleep(duration_ms)
    else:
        lightsleep()

def enter_deep_sleep(duration_ms=None):
    if duration_ms:
        deepsleep(duration_ms)
    else:
        deepsleep()

def set_display_power(enabled):
    global display_on
    display_bl.value(1 if enabled else 0)
    display_on = enabled

def get_display_power():
    return display_on
"""
        return code.strip()
