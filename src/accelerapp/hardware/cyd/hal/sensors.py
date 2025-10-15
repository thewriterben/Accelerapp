"""
Sensor Monitoring for CYD.

Provides temperature and performance monitoring capabilities
for ESP32 Cheap Yellow Display boards.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SensorType(Enum):
    """Sensor types available on CYD."""
    TEMPERATURE = "temperature"
    LIGHT = "light"
    PERFORMANCE = "performance"
    SYSTEM = "system"


@dataclass
class SensorReading:
    """Sensor reading data."""
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime


class SensorMonitor:
    """
    Sensor monitoring for CYD hardware.
    
    Provides monitoring capabilities for:
    - Internal temperature sensor (ESP32)
    - Light sensor (LDR on pin 34)
    - Performance metrics (CPU, memory, network)
    - System health monitoring
    - Historical data tracking
    """

    # LDR (Light Dependent Resistor) pin
    LDR_PIN = 34

    def __init__(self):
        """Initialize sensor monitor."""
        self._readings: List[SensorReading] = []
        self._max_readings = 1000

    def read_temperature(self) -> Optional[float]:
        """
        Read internal temperature sensor.
        
        Returns:
            Temperature in Celsius or None if unavailable
        """
        # ESP32 internal temperature sensor
        # Typical operating range: -40°C to 125°C
        return None

    def read_light_level(self) -> Optional[int]:
        """
        Read ambient light level from LDR.
        
        Returns:
            Light level (0-4095 from 12-bit ADC) or None if unavailable
        """
        # LDR on pin 34 provides ambient light reading
        return None

    def read_cpu_frequency(self) -> int:
        """
        Read current CPU frequency.
        
        Returns:
            CPU frequency in MHz
        """
        # ESP32 can run at 80, 160, or 240 MHz
        return 240

    def read_free_heap(self) -> int:
        """
        Read free heap memory.
        
        Returns:
            Free heap in bytes
        """
        return 0

    def read_heap_size(self) -> int:
        """
        Read total heap size.
        
        Returns:
            Total heap in bytes
        """
        return 0

    def read_cpu_usage(self) -> float:
        """
        Estimate CPU usage.
        
        Returns:
            CPU usage percentage (0-100)
        """
        return 0.0

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics.
        
        Returns:
            Dictionary of system statistics
        """
        return {
            "temperature_c": self.read_temperature(),
            "light_level": self.read_light_level(),
            "cpu_frequency_mhz": self.read_cpu_frequency(),
            "free_heap_bytes": self.read_free_heap(),
            "heap_size_bytes": self.read_heap_size(),
            "cpu_usage_percent": self.read_cpu_usage(),
        }

    def record_reading(self, reading: SensorReading) -> None:
        """
        Record a sensor reading.
        
        Args:
            reading: Sensor reading to record
        """
        self._readings.append(reading)
        
        # Limit stored readings
        if len(self._readings) > self._max_readings:
            self._readings = self._readings[-self._max_readings:]

    def get_readings(
        self,
        sensor_type: Optional[SensorType] = None,
        limit: int = 100
    ) -> List[SensorReading]:
        """
        Get historical sensor readings.
        
        Args:
            sensor_type: Filter by sensor type (None for all)
            limit: Maximum number of readings to return
            
        Returns:
            List of sensor readings
        """
        readings = self._readings
        
        if sensor_type:
            readings = [r for r in readings if r.sensor_type == sensor_type]
        
        return readings[-limit:]

    def get_average(
        self,
        sensor_type: SensorType,
        minutes: int = 5
    ) -> Optional[float]:
        """
        Get average sensor reading over time period.
        
        Args:
            sensor_type: Type of sensor
            minutes: Time period in minutes
            
        Returns:
            Average value or None if no data
        """
        now = datetime.now()
        readings = [
            r for r in self._readings
            if r.sensor_type == sensor_type
            and (now - r.timestamp).total_seconds() < minutes * 60
        ]
        
        if not readings:
            return None
        
        return sum(r.value for r in readings) / len(readings)

    def get_min_max(
        self,
        sensor_type: SensorType,
        minutes: int = 5
    ) -> Optional[Dict[str, float]]:
        """
        Get min/max sensor readings over time period.
        
        Args:
            sensor_type: Type of sensor
            minutes: Time period in minutes
            
        Returns:
            Dictionary with min and max values or None
        """
        now = datetime.now()
        readings = [
            r for r in self._readings
            if r.sensor_type == sensor_type
            and (now - r.timestamp).total_seconds() < minutes * 60
        ]
        
        if not readings:
            return None
        
        values = [r.value for r in readings]
        return {
            "min": min(values),
            "max": max(values),
        }

    def clear_readings(self) -> None:
        """Clear all stored sensor readings."""
        self._readings.clear()

    def generate_code(self, platform: str = "arduino") -> str:
        """
        Generate platform-specific sensor monitoring code.
        
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
        """Generate Arduino sensor monitoring code."""
        code = f"""// Sensor Monitoring Configuration
#ifdef __cplusplus
extern "C" {{
#endif
uint8_t temprature_sens_read();
#ifdef __cplusplus
}}
#endif

#define LDR_PIN {self.LDR_PIN}

// Temperature sensor
float readTemperature() {{
    // ESP32 internal temperature sensor
    return (temprature_sens_read() - 32) / 1.8;
}}

// Light sensor (LDR)
int readLightLevel() {{
    return analogRead(LDR_PIN);
}}

// System stats
void getSystemStats() {{
    Serial.println("=== System Statistics ===");
    
    // Temperature
    float temp = readTemperature();
    Serial.print("Temperature: ");
    Serial.print(temp);
    Serial.println(" C");
    
    // Light level
    int light = readLightLevel();
    Serial.print("Light Level: ");
    Serial.println(light);
    
    // Heap
    Serial.print("Free Heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    
    // CPU frequency
    Serial.print("CPU Frequency: ");
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(" MHz");
    
    Serial.println("========================");
}}

void setupSensors() {{
    // Configure LDR pin
    pinMode(LDR_PIN, INPUT);
}}
"""
        return code.strip()

    def _generate_esp_idf_code(self) -> str:
        """Generate ESP-IDF sensor monitoring code."""
        code = f"""// Sensor Monitoring Configuration for ESP-IDF
#include "driver/adc.h"
#include "driver/temp_sensor.h"
#include "esp_system.h"

#define LDR_ADC_CHANNEL ADC1_CHANNEL_6  // GPIO{self.LDR_PIN}

static temp_sensor_handle_t temp_sensor = NULL;

void sensors_init() {{
    // Initialize temperature sensor
    temp_sensor_config_t temp_config = TEMP_SENSOR_CONFIG_DEFAULT(-10, 80);
    temp_sensor_install(&temp_config, &temp_sensor);
    temp_sensor_enable(temp_sensor);
    
    // Initialize ADC for LDR
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(LDR_ADC_CHANNEL, ADC_ATTEN_DB_11);
}}

float read_temperature() {{
    float temp;
    temp_sensor_read_celsius(temp_sensor, &temp);
    return temp;
}}

int read_light_level() {{
    return adc1_get_raw(LDR_ADC_CHANNEL);
}}

void get_system_stats() {{
    printf("=== System Statistics ===\\n");
    printf("Temperature: %.2f C\\n", read_temperature());
    printf("Light Level: %d\\n", read_light_level());
    printf("Free Heap: %lu bytes\\n", esp_get_free_heap_size());
    printf("CPU Frequency: %d MHz\\n", esp_clk_cpu_freq() / 1000000);
    printf("========================\\n");
}}
"""
        return code.strip()

    def _generate_micropython_code(self) -> str:
        """Generate MicroPython sensor monitoring code."""
        code = f"""# Sensor Monitoring Configuration for MicroPython
from machine import ADC, Pin
import esp32
import gc

LDR_PIN = {self.LDR_PIN}

# Initialize sensors
ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

def read_temperature():
    \"\"\"Read internal temperature sensor.\"\"\"
    # ESP32 internal temperature (F to C conversion)
    temp_f = esp32.raw_temperature()
    return (temp_f - 32) * 5.0 / 9.0

def read_light_level():
    \"\"\"Read ambient light level from LDR.\"\"\"
    return ldr.read()

def get_system_stats():
    \"\"\"Get comprehensive system statistics.\"\"\"
    stats = {{
        'temperature_c': read_temperature(),
        'light_level': read_light_level(),
        'free_memory': gc.mem_free(),
        'allocated_memory': gc.mem_alloc(),
        'cpu_frequency': esp32.cpu_freq(),
    }}
    return stats

def print_system_stats():
    \"\"\"Print system statistics.\"\"\"
    stats = get_system_stats()
    print("=== System Statistics ===")
    print(f"Temperature: {{stats['temperature_c']:.2f}} C")
    print(f"Light Level: {{stats['light_level']}}")
    print(f"Free Memory: {{stats['free_memory']}} bytes")
    print(f"Allocated Memory: {{stats['allocated_memory']}} bytes")
    print(f"CPU Frequency: {{stats['cpu_frequency']}} Hz")
    print("========================")
"""
        return code.strip()
