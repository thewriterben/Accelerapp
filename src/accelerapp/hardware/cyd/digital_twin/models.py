"""
Digital twin models for CYD hardware.

Provides data models and state management for CYD digital twins.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TwinStatus(Enum):
    """Digital twin status."""
    CREATED = "created"
    SYNCING = "syncing"
    SYNCHRONIZED = "synchronized"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class DisplayState:
    """Display hardware state."""
    enabled: bool = True
    brightness: int = 255
    rotation: int = 1
    width: int = 320
    height: int = 240
    backlight_on: bool = True
    update_count: int = 0


@dataclass
class TouchState:
    """Touch controller state."""
    enabled: bool = True
    calibrated: bool = False
    last_touch_x: Optional[int] = None
    last_touch_y: Optional[int] = None
    last_touch_time: Optional[datetime] = None
    touch_count: int = 0


@dataclass
class PowerState:
    """Power management state."""
    mode: str = "active"
    battery_voltage: Optional[float] = None
    current_draw_ma: float = 0.0
    power_consumption_mw: float = 0.0
    uptime_seconds: float = 0.0
    sleep_count: int = 0


@dataclass
class SystemState:
    """System state."""
    cpu_frequency_mhz: int = 240
    free_heap_bytes: int = 0
    temperature_c: float = 25.0
    wifi_connected: bool = False
    wifi_rssi: Optional[int] = None
    firmware_version: str = "1.0.0"


@dataclass
class CYDTwinModel:
    """
    Digital twin model for CYD hardware.
    
    Represents the complete state of a CYD device including:
    - Display state
    - Touch controller state
    - GPIO states
    - Power state
    - System state
    - Telemetry data
    """
    
    device_id: str
    device_name: str
    status: TwinStatus = TwinStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    
    # Hardware state
    display: DisplayState = field(default_factory=DisplayState)
    touch: TouchState = field(default_factory=TouchState)
    power: PowerState = field(default_factory=PowerState)
    system: SystemState = field(default_factory=SystemState)
    gpio_states: Dict[int, bool] = field(default_factory=dict)
    
    # Metadata
    location: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Telemetry
    telemetry_history: List[Dict[str, Any]] = field(default_factory=list)
    max_telemetry_records: int = 1000

    def update_display_state(self, **kwargs) -> None:
        """
        Update display state.
        
        Args:
            **kwargs: Display state fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.display, key):
                setattr(self.display, key, value)
        self.display.update_count += 1
        self._mark_synced()

    def update_touch_state(self, **kwargs) -> None:
        """
        Update touch state.
        
        Args:
            **kwargs: Touch state fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.touch, key):
                setattr(self.touch, key, value)
        self._mark_synced()

    def update_power_state(self, **kwargs) -> None:
        """
        Update power state.
        
        Args:
            **kwargs: Power state fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.power, key):
                setattr(self.power, key, value)
        self._mark_synced()

    def update_system_state(self, **kwargs) -> None:
        """
        Update system state.
        
        Args:
            **kwargs: System state fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.system, key):
                setattr(self.system, key, value)
        self._mark_synced()

    def set_gpio(self, pin: int, state: bool) -> None:
        """
        Set GPIO pin state.
        
        Args:
            pin: Pin number
            state: Pin state
        """
        self.gpio_states[pin] = state
        self._mark_synced()

    def get_gpio(self, pin: int) -> Optional[bool]:
        """
        Get GPIO pin state.
        
        Args:
            pin: Pin number
            
        Returns:
            Pin state or None
        """
        return self.gpio_states.get(pin)

    def record_telemetry(self, data: Dict[str, Any]) -> None:
        """
        Record telemetry data point.
        
        Args:
            data: Telemetry data
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        self.telemetry_history.append(record)
        
        # Limit history size
        if len(self.telemetry_history) > self.max_telemetry_records:
            self.telemetry_history = self.telemetry_history[-self.max_telemetry_records:]

    def get_telemetry(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent telemetry records.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of telemetry records
        """
        return self.telemetry_history[-limit:]

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of current state.
        
        Returns:
            State summary dictionary
        """
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "status": self.status.value,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "display": {
                "enabled": self.display.enabled,
                "brightness": self.display.brightness,
                "backlight_on": self.display.backlight_on,
                "updates": self.display.update_count,
            },
            "touch": {
                "enabled": self.touch.enabled,
                "calibrated": self.touch.calibrated,
                "touches": self.touch.touch_count,
            },
            "power": {
                "mode": self.power.mode,
                "consumption_mw": self.power.power_consumption_mw,
                "uptime_hours": self.power.uptime_seconds / 3600,
            },
            "system": {
                "cpu_mhz": self.system.cpu_frequency_mhz,
                "temperature_c": self.system.temperature_c,
                "wifi_connected": self.system.wifi_connected,
                "firmware": self.system.firmware_version,
            },
            "gpio_pins_used": len(self.gpio_states),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "display": {
                "enabled": self.display.enabled,
                "brightness": self.display.brightness,
                "rotation": self.display.rotation,
                "width": self.display.width,
                "height": self.display.height,
                "backlight_on": self.display.backlight_on,
                "update_count": self.display.update_count,
            },
            "touch": {
                "enabled": self.touch.enabled,
                "calibrated": self.touch.calibrated,
                "last_touch_x": self.touch.last_touch_x,
                "last_touch_y": self.touch.last_touch_y,
                "last_touch_time": self.touch.last_touch_time.isoformat() if self.touch.last_touch_time else None,
                "touch_count": self.touch.touch_count,
            },
            "power": {
                "mode": self.power.mode,
                "battery_voltage": self.power.battery_voltage,
                "current_draw_ma": self.power.current_draw_ma,
                "power_consumption_mw": self.power.power_consumption_mw,
                "uptime_seconds": self.power.uptime_seconds,
                "sleep_count": self.power.sleep_count,
            },
            "system": {
                "cpu_frequency_mhz": self.system.cpu_frequency_mhz,
                "free_heap_bytes": self.system.free_heap_bytes,
                "temperature_c": self.system.temperature_c,
                "wifi_connected": self.system.wifi_connected,
                "wifi_rssi": self.system.wifi_rssi,
                "firmware_version": self.system.firmware_version,
            },
            "gpio_states": self.gpio_states,
            "location": self.location,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CYDTwinModel":
        """
        Create model from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            CYDTwinModel instance
        """
        model = cls(
            device_id=data["device_id"],
            device_name=data["device_name"],
            status=TwinStatus(data.get("status", "created")),
        )
        
        if "display" in data:
            d = data["display"]
            model.display = DisplayState(**d)
        
        if "touch" in data:
            t = data["touch"]
            model.touch = TouchState(**{k: v for k, v in t.items() if k != "last_touch_time"})
        
        if "power" in data:
            p = data["power"]
            model.power = PowerState(**p)
        
        if "system" in data:
            s = data["system"]
            model.system = SystemState(**s)
        
        model.gpio_states = data.get("gpio_states", {})
        model.location = data.get("location")
        model.tags = data.get("tags", [])
        model.metadata = data.get("metadata", {})
        
        return model

    def _mark_synced(self) -> None:
        """Mark model as synchronized."""
        self.last_sync = datetime.now()
        if self.status == TwinStatus.CREATED:
            self.status = TwinStatus.SYNCHRONIZED

    def mark_disconnected(self) -> None:
        """Mark device as disconnected."""
        self.status = TwinStatus.DISCONNECTED

    def mark_error(self) -> None:
        """Mark device in error state."""
        self.status = TwinStatus.ERROR

    def is_healthy(self) -> bool:
        """
        Check if device is healthy.
        
        Returns:
            True if device is healthy
        """
        if self.status in [TwinStatus.DISCONNECTED, TwinStatus.ERROR]:
            return False
        
        # Check temperature
        if self.system.temperature_c > 80:
            return False
        
        # Check power
        if self.power.power_consumption_mw > 500:
            return False
        
        return True

    def get_health_report(self) -> Dict[str, Any]:
        """
        Get device health report.
        
        Returns:
            Health report dictionary
        """
        health = self.is_healthy()
        issues = []
        
        if self.status in [TwinStatus.DISCONNECTED, TwinStatus.ERROR]:
            issues.append(f"Device status: {self.status.value}")
        
        if self.system.temperature_c > 80:
            issues.append(f"High temperature: {self.system.temperature_c}°C")
        elif self.system.temperature_c > 60:
            issues.append(f"Elevated temperature: {self.system.temperature_c}°C")
        
        if self.power.power_consumption_mw > 500:
            issues.append(f"High power consumption: {self.power.power_consumption_mw}mW")
        
        if self.system.free_heap_bytes < 10000:
            issues.append(f"Low memory: {self.system.free_heap_bytes} bytes free")
        
        return {
            "healthy": health,
            "status": self.status.value,
            "issues": issues,
            "temperature_c": self.system.temperature_c,
            "power_consumption_mw": self.power.power_consumption_mw,
            "uptime_hours": self.power.uptime_seconds / 3600,
        }
