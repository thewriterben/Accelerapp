"""
Code generation templates for CYD projects.

Provides templates for common CYD application patterns.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class TemplateType(Enum):
    """Template types for CYD projects."""
    IOT_DASHBOARD = "iot_dashboard"
    SENSOR_DISPLAY = "sensor_display"
    WEATHER_STATION = "weather_station"
    MEDIA_CONTROLLER = "media_controller"
    HOME_AUTOMATION = "home_automation"
    GAME_PLATFORM = "game_platform"


@dataclass
class Template:
    """Code generation template."""
    name: str
    template_type: TemplateType
    description: str
    code: str
    requirements: List[str]


class TemplateManager:
    """
    Manager for CYD code generation templates.
    
    Provides pre-built templates for common CYD applications.
    """

    def __init__(self):
        """Initialize template manager."""
        self._templates: Dict[TemplateType, Template] = self._load_templates()

    def _load_templates(self) -> Dict[TemplateType, Template]:
        """Load built-in templates."""
        return {
            TemplateType.IOT_DASHBOARD: Template(
                name="IoT Dashboard",
                template_type=TemplateType.IOT_DASHBOARD,
                description="Real-time IoT sensor dashboard with graphs",
                code=self._get_iot_dashboard_template(),
                requirements=["WiFi", "Display", "Touch", "JSON"],
            ),
            TemplateType.SENSOR_DISPLAY: Template(
                name="Sensor Display",
                template_type=TemplateType.SENSOR_DISPLAY,
                description="Simple sensor value display",
                code=self._get_sensor_display_template(),
                requirements=["Display"],
            ),
            TemplateType.WEATHER_STATION: Template(
                name="Weather Station",
                template_type=TemplateType.WEATHER_STATION,
                description="Weather display with API integration",
                code=self._get_weather_station_template(),
                requirements=["WiFi", "Display", "JSON", "HTTP"],
            ),
        }

    def get_template(self, template_type: TemplateType) -> Optional[Template]:
        """
        Get a template by type.
        
        Args:
            template_type: Type of template
            
        Returns:
            Template or None if not found
        """
        return self._templates.get(template_type)

    def list_templates(self) -> List[Template]:
        """
        List all available templates.
        
        Returns:
            List of templates
        """
        return list(self._templates.values())

    def generate_project(
        self,
        template_type: TemplateType,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate project code from template.
        
        Args:
            template_type: Type of template
            config: Project configuration
            
        Returns:
            Generated code
        """
        template = self.get_template(template_type)
        if not template:
            return ""
        
        code = template.code
        
        # Apply configuration substitutions
        if config:
            for key, value in config.items():
                code = code.replace(f"{{{{{key}}}}}", str(value))
        
        return code

    def _get_iot_dashboard_template(self) -> str:
        """Get IoT dashboard template code."""
        return """// IoT Dashboard Template for CYD
#include <WiFi.h>
#include <Adafruit_ILI9341.h>
#include <XPT2046_Touchscreen.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* WIFI_SSID = "{{wifi_ssid}}";
const char* WIFI_PASSWORD = "{{wifi_password}}";

// Dashboard state
struct DashboardData {
    float temperature;
    float humidity;
    int lightLevel;
    bool deviceStatus;
};

DashboardData data;

void setupDashboard() {
    // Initialize display
    setupDisplay();
    
    // Connect to WiFi
    connectWiFi();
    
    // Draw dashboard layout
    drawDashboard();
}

void connectWiFi() {
    tft.setCursor(10, 100);
    tft.print("Connecting WiFi...");
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    
    tft.fillScreen(ILI9341_BLACK);
    tft.setCursor(10, 100);
    tft.print("Connected!");
    delay(1000);
}

void drawDashboard() {
    tft.fillScreen(ILI9341_BLACK);
    
    // Title
    tft.setTextSize(2);
    tft.setTextColor(ILI9341_CYAN);
    tft.setCursor(10, 10);
    tft.println("IoT Dashboard");
    
    // Sensor sections
    tft.setTextSize(1);
    tft.setTextColor(ILI9341_WHITE);
    
    // Temperature
    tft.setCursor(10, 50);
    tft.print("Temperature:");
    
    // Humidity
    tft.setCursor(10, 90);
    tft.print("Humidity:");
    
    // Light
    tft.setCursor(10, 130);
    tft.print("Light:");
    
    // Status
    tft.setCursor(10, 170);
    tft.print("Status:");
}

void updateDashboard() {
    // Update temperature
    tft.fillRect(150, 50, 100, 16, ILI9341_BLACK);
    tft.setCursor(150, 50);
    tft.setTextColor(ILI9341_GREEN);
    tft.printf("%.1f C", data.temperature);
    
    // Update humidity
    tft.fillRect(150, 90, 100, 16, ILI9341_BLACK);
    tft.setCursor(150, 90);
    tft.setTextColor(ILI9341_BLUE);
    tft.printf("%.1f %%", data.humidity);
    
    // Update light
    tft.fillRect(150, 130, 100, 16, ILI9341_BLACK);
    tft.setCursor(150, 130);
    tft.setTextColor(ILI9341_YELLOW);
    tft.printf("%d", data.lightLevel);
    
    // Update status
    tft.fillRect(150, 170, 100, 16, ILI9341_BLACK);
    tft.setCursor(150, 170);
    tft.setTextColor(data.deviceStatus ? ILI9341_GREEN : ILI9341_RED);
    tft.print(data.deviceStatus ? "ONLINE" : "OFFLINE");
}

void loop() {
    // Read sensors
    data.temperature = readTemperature();
    data.humidity = readHumidity();
    data.lightLevel = readLightLevel();
    data.deviceStatus = true;
    
    // Update display
    updateDashboard();
    
    delay(2000);
}
"""

    def _get_sensor_display_template(self) -> str:
        """Get sensor display template code."""
        return """// Sensor Display Template for CYD
#include <Adafruit_ILI9341.h>

struct SensorData {
    const char* name;
    float value;
    const char* unit;
    uint16_t color;
};

SensorData sensors[] = {
    {"Temperature", 0.0, "C", ILI9341_RED},
    {"Humidity", 0.0, "%", ILI9341_BLUE},
    {"Pressure", 0.0, "hPa", ILI9341_GREEN},
    {"Light", 0.0, "lux", ILI9341_YELLOW}
};

const int NUM_SENSORS = sizeof(sensors) / sizeof(sensors[0]);

void setupSensorDisplay() {
    setupDisplay();
    
    // Draw layout
    tft.fillScreen(ILI9341_BLACK);
    tft.setTextSize(2);
    tft.setTextColor(ILI9341_CYAN);
    tft.setCursor(10, 10);
    tft.println("Sensor Monitor");
    
    // Draw sensor labels
    int y = 50;
    for (int i = 0; i < NUM_SENSORS; i++) {
        tft.setTextSize(1);
        tft.setTextColor(ILI9341_WHITE);
        tft.setCursor(10, y);
        tft.print(sensors[i].name);
        y += 40;
    }
}

void updateSensorDisplay() {
    int y = 50;
    for (int i = 0; i < NUM_SENSORS; i++) {
        // Clear old value
        tft.fillRect(150, y, 150, 20, ILI9341_BLACK);
        
        // Draw new value
        tft.setTextSize(2);
        tft.setTextColor(sensors[i].color);
        tft.setCursor(150, y);
        tft.printf("%.1f %s", sensors[i].value, sensors[i].unit);
        
        y += 40;
    }
}

void loop() {
    // Read sensors
    sensors[0].value = readTemperature();
    sensors[1].value = readHumidity();
    sensors[2].value = readPressure();
    sensors[3].value = readLightLevel();
    
    // Update display
    updateSensorDisplay();
    
    delay(1000);
}
"""

    def _get_weather_station_template(self) -> str:
        """Get weather station template code."""
        return """// Weather Station Template for CYD
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_ILI9341.h>

// Configuration
const char* WIFI_SSID = "{{wifi_ssid}}";
const char* WIFI_PASSWORD = "{{wifi_password}}";
const char* API_KEY = "{{api_key}}";
const char* CITY = "{{city}}";
const char* API_URL = "http://api.openweathermap.org/data/2.5/weather";

struct WeatherData {
    String description;
    float temperature;
    float humidity;
    int pressure;
    float windSpeed;
    String icon;
};

WeatherData weather;

void setupWeatherStation() {
    setupDisplay();
    connectWiFi();
    
    drawWeatherUI();
}

void connectWiFi() {
    tft.setCursor(10, 100);
    tft.setTextSize(1);
    tft.print("Connecting to WiFi...");
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    
    tft.fillScreen(ILI9341_BLACK);
}

void drawWeatherUI() {
    tft.fillScreen(ILI9341_BLACK);
    
    // Title
    tft.setTextSize(2);
    tft.setTextColor(ILI9341_CYAN);
    tft.setCursor(10, 10);
    tft.print("Weather Station");
    
    // City
    tft.setTextSize(1);
    tft.setCursor(10, 35);
    tft.print(CITY);
}

void fetchWeather() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        String url = String(API_URL) + "?q=" + CITY + 
                     "&appid=" + API_KEY + "&units=metric";
        
        http.begin(url);
        int httpCode = http.GET();
        
        if (httpCode == 200) {
            String payload = http.getString();
            parseWeatherData(payload);
        }
        
        http.end();
    }
}

void parseWeatherData(String json) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, json);
    
    weather.description = doc["weather"][0]["description"].as<String>();
    weather.temperature = doc["main"]["temp"];
    weather.humidity = doc["main"]["humidity"];
    weather.pressure = doc["main"]["pressure"];
    weather.windSpeed = doc["wind"]["speed"];
}

void updateWeatherDisplay() {
    // Clear data area
    tft.fillRect(0, 60, 320, 180, ILI9341_BLACK);
    
    int y = 70;
    tft.setTextSize(1);
    tft.setTextColor(ILI9341_WHITE);
    
    // Description
    tft.setCursor(10, y);
    tft.print(weather.description);
    y += 30;
    
    // Temperature
    tft.setCursor(10, y);
    tft.setTextColor(ILI9341_RED);
    tft.setTextSize(3);
    tft.printf("%.1f C", weather.temperature);
    y += 40;
    
    // Humidity
    tft.setTextSize(1);
    tft.setTextColor(ILI9341_BLUE);
    tft.setCursor(10, y);
    tft.printf("Humidity: %.0f%%", weather.humidity);
    y += 20;
    
    // Pressure
    tft.setTextColor(ILI9341_GREEN);
    tft.setCursor(10, y);
    tft.printf("Pressure: %d hPa", weather.pressure);
    y += 20;
    
    // Wind
    tft.setTextColor(ILI9341_YELLOW);
    tft.setCursor(10, y);
    tft.printf("Wind: %.1f m/s", weather.windSpeed);
}

void loop() {
    fetchWeather();
    updateWeatherDisplay();
    delay(300000); // Update every 5 minutes
}
"""
