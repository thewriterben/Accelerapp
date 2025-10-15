"""
CYD hardware simulator for digital twin.

Provides virtual CYD hardware simulation for testing and development.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SimulationMode(Enum):
    """Simulation modes."""
    REALTIME = "realtime"
    ACCELERATED = "accelerated"
    STEP_BY_STEP = "step_by_step"


@dataclass
class SimulatedState:
    """Simulated hardware state."""
    timestamp: datetime
    display_buffer: List[List[int]]  # 2D array of pixel colors
    touch_points: List[Tuple[int, int]]
    gpio_states: Dict[int, bool]
    power_consumption: float
    temperature: float
    cpu_frequency: int


class CYDSimulator:
    """
    Virtual hardware simulator for CYD.
    
    Provides:
    - Display frame buffer simulation
    - Touch input simulation
    - GPIO state simulation
    - Power consumption modeling
    - Performance simulation
    - Temperature simulation
    """

    def __init__(self, mode: SimulationMode = SimulationMode.REALTIME):
        """
        Initialize CYD simulator.
        
        Args:
            mode: Simulation mode
        """
        self.mode = mode
        self._width = 320
        self._height = 240
        self._display_buffer = [[0x0000 for _ in range(self._width)] for _ in range(self._height)]
        self._touch_points: List[Tuple[int, int]] = []
        self._gpio_states: Dict[int, bool] = {}
        self._running = False
        self._cpu_frequency = 240  # MHz
        self._power_consumption = 0.0  # Watts
        self._temperature = 25.0  # Celsius
        self._simulation_time = 0.0  # seconds

    def start(self) -> None:
        """Start simulation."""
        self._running = True
        print(f"CYD Simulator started in {self.mode.value} mode")

    def stop(self) -> None:
        """Stop simulation."""
        self._running = False
        print("CYD Simulator stopped")

    def reset(self) -> None:
        """Reset simulator to initial state."""
        self._display_buffer = [[0x0000 for _ in range(self._width)] for _ in range(self._height)]
        self._touch_points.clear()
        self._gpio_states.clear()
        self._simulation_time = 0.0
        self._temperature = 25.0
        self._power_consumption = 0.0

    def step(self, delta_time: float = 0.01) -> None:
        """
        Advance simulation by time step.
        
        Args:
            delta_time: Time step in seconds
        """
        if not self._running:
            return
        
        self._simulation_time += delta_time
        
        # Update temperature based on power consumption
        if self._power_consumption > 0:
            self._temperature += 0.01 * self._power_consumption * delta_time
        
        # Passive cooling
        if self._temperature > 25.0:
            self._temperature -= 0.02 * delta_time

    def set_pixel(self, x: int, y: int, color: int) -> None:
        """
        Set pixel in simulated display.
        
        Args:
            x, y: Pixel coordinates
            color: RGB565 color value
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            self._display_buffer[y][x] = color

    def get_pixel(self, x: int, y: int) -> Optional[int]:
        """
        Get pixel from simulated display.
        
        Args:
            x, y: Pixel coordinates
            
        Returns:
            RGB565 color value or None if out of bounds
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._display_buffer[y][x]
        return None

    def fill_rectangle(self, x: int, y: int, w: int, h: int, color: int) -> None:
        """
        Fill rectangle in simulated display.
        
        Args:
            x, y: Top-left corner
            w, h: Width and height
            color: RGB565 color value
        """
        for py in range(y, min(y + h, self._height)):
            for px in range(x, min(x + w, self._width)):
                self._display_buffer[py][px] = color

    def simulate_touch(self, x: int, y: int) -> None:
        """
        Simulate touch input.
        
        Args:
            x, y: Touch coordinates
        """
        if 0 <= x < self._width and 0 <= y < self._height:
            self._touch_points.append((x, y))

    def get_touch_points(self) -> List[Tuple[int, int]]:
        """
        Get simulated touch points.
        
        Returns:
            List of (x, y) touch coordinates
        """
        return self._touch_points.copy()

    def clear_touch_points(self) -> None:
        """Clear all simulated touch points."""
        self._touch_points.clear()

    def set_gpio(self, pin: int, state: bool) -> None:
        """
        Set GPIO pin state.
        
        Args:
            pin: Pin number
            state: Pin state (True=HIGH, False=LOW)
        """
        self._gpio_states[pin] = state

    def get_gpio(self, pin: int) -> Optional[bool]:
        """
        Get GPIO pin state.
        
        Args:
            pin: Pin number
            
        Returns:
            Pin state or None if not configured
        """
        return self._gpio_states.get(pin)

    def set_cpu_frequency(self, frequency: int) -> None:
        """
        Set simulated CPU frequency.
        
        Args:
            frequency: Frequency in MHz (80, 160, or 240)
        """
        if frequency in [80, 160, 240]:
            self._cpu_frequency = frequency
            self._update_power_consumption()

    def _update_power_consumption(self) -> None:
        """Update power consumption based on current state."""
        # Base consumption from CPU
        cpu_power = {
            80: 0.05,
            160: 0.08,
            240: 0.16,
        }.get(self._cpu_frequency, 0.16)
        
        # Display consumption (if any pixels are non-black)
        display_on = any(
            self._display_buffer[y][x] != 0x0000
            for y in range(self._height)
            for x in range(self._width)
        )
        display_power = 0.075 if display_on else 0.0
        
        # GPIO power (estimate)
        gpio_power = len(self._gpio_states) * 0.001
        
        self._power_consumption = cpu_power + display_power + gpio_power

    def get_state(self) -> SimulatedState:
        """
        Get current simulated state.
        
        Returns:
            Current simulation state
        """
        self._update_power_consumption()
        
        return SimulatedState(
            timestamp=datetime.now(),
            display_buffer=self._display_buffer,
            touch_points=self._touch_points.copy(),
            gpio_states=self._gpio_states.copy(),
            power_consumption=self._power_consumption,
            temperature=self._temperature,
            cpu_frequency=self._cpu_frequency,
        )

    def export_display_buffer(self, format: str = "rgb565") -> bytes:
        """
        Export display buffer.
        
        Args:
            format: Output format (rgb565, rgb888, png)
            
        Returns:
            Display buffer data
        """
        if format == "rgb565":
            data = bytearray()
            for row in self._display_buffer:
                for pixel in row:
                    data.extend(pixel.to_bytes(2, byteorder='big'))
            return bytes(data)
        
        return b""

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get simulation statistics.
        
        Returns:
            Statistics dictionary
        """
        pixel_count = sum(
            1 for y in range(self._height)
            for x in range(self._width)
            if self._display_buffer[y][x] != 0x0000
        )
        
        return {
            "simulation_time": self._simulation_time,
            "running": self._running,
            "cpu_frequency_mhz": self._cpu_frequency,
            "power_consumption_w": self._power_consumption,
            "temperature_c": self._temperature,
            "display_pixels_lit": pixel_count,
            "total_pixels": self._width * self._height,
            "gpio_pins_used": len(self._gpio_states),
            "touch_points": len(self._touch_points),
        }

    def inject_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Inject external event into simulation.
        
        Args:
            event_type: Type of event (touch, gpio, temperature, etc.)
            data: Event data
        """
        if event_type == "touch":
            x = data.get("x", 0)
            y = data.get("y", 0)
            self.simulate_touch(x, y)
        
        elif event_type == "gpio":
            pin = data.get("pin")
            state = data.get("state", False)
            if pin is not None:
                self.set_gpio(pin, state)
        
        elif event_type == "temperature":
            temp = data.get("temperature", 25.0)
            self._temperature = temp

    def create_snapshot(self) -> Dict[str, Any]:
        """
        Create simulation snapshot.
        
        Returns:
            Snapshot data
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode.value,
            "state": {
                "display_width": self._width,
                "display_height": self._height,
                "gpio_states": self._gpio_states.copy(),
                "cpu_frequency": self._cpu_frequency,
                "power_consumption": self._power_consumption,
                "temperature": self._temperature,
                "simulation_time": self._simulation_time,
            },
            "statistics": self.get_statistics(),
        }
