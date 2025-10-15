"""
Example loader for CYD projects.

Provides access to community examples and tutorials.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ExampleCategory(Enum):
    """Example categories."""
    BASIC = "basic"
    DISPLAY = "display"
    TOUCH = "touch"
    NETWORKING = "networking"
    SENSORS = "sensors"
    GRAPHICS = "graphics"
    GAMES = "games"


@dataclass
class Example:
    """Code example."""
    name: str
    category: ExampleCategory
    description: str
    code: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    tags: List[str]


class ExampleLoader:
    """
    Loader for CYD code examples.
    
    Provides curated examples for learning and reference.
    """

    def __init__(self):
        """Initialize example loader."""
        self._examples: Dict[str, Example] = self._load_examples()

    def _load_examples(self) -> Dict[str, Example]:
        """Load built-in examples."""
        examples = {}
        
        # Basic examples
        examples["hello_world"] = Example(
            name="Hello World",
            category=ExampleCategory.BASIC,
            description="Display text on CYD screen",
            code=self._get_hello_world_example(),
            difficulty="beginner",
            tags=["display", "text", "basics"],
        )
        
        examples["touch_demo"] = Example(
            name="Touch Demo",
            category=ExampleCategory.TOUCH,
            description="Demonstrate touch input with visual feedback",
            code=self._get_touch_demo_example(),
            difficulty="beginner",
            tags=["touch", "input", "graphics"],
        )
        
        examples["wifi_scanner"] = Example(
            name="WiFi Scanner",
            category=ExampleCategory.NETWORKING,
            description="Scan and display nearby WiFi networks",
            code=self._get_wifi_scanner_example(),
            difficulty="intermediate",
            tags=["wifi", "networking", "scanner"],
        )
        
        return examples

    def get_example(self, name: str) -> Optional[Example]:
        """
        Get example by name.
        
        Args:
            name: Example name
            
        Returns:
            Example or None if not found
        """
        return self._examples.get(name)

    def list_examples(
        self,
        category: Optional[ExampleCategory] = None,
        difficulty: Optional[str] = None
    ) -> List[Example]:
        """
        List examples with optional filtering.
        
        Args:
            category: Filter by category
            difficulty: Filter by difficulty
            
        Returns:
            List of examples
        """
        examples = list(self._examples.values())
        
        if category:
            examples = [e for e in examples if e.category == category]
        
        if difficulty:
            examples = [e for e in examples if e.difficulty == difficulty]
        
        return examples

    def search_examples(self, query: str) -> List[Example]:
        """
        Search examples by keyword.
        
        Args:
            query: Search query
            
        Returns:
            List of matching examples
        """
        query = query.lower()
        results = []
        
        for example in self._examples.values():
            if (query in example.name.lower() or
                query in example.description.lower() or
                any(query in tag for tag in example.tags)):
                results.append(example)
        
        return results

    def _get_hello_world_example(self) -> str:
        """Get hello world example code."""
        return """// Hello World for CYD
#include <Adafruit_ILI9341.h>
#include <SPI.h>

// Display pins
#define TFT_DC 2
#define TFT_CS 15
#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_MISO 12
#define TFT_BL 21

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);

void setup() {
    // Turn on backlight
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    
    // Initialize display
    tft.begin();
    tft.setRotation(1);
    
    // Clear screen
    tft.fillScreen(ILI9341_BLACK);
    
    // Display hello world
    tft.setTextSize(3);
    tft.setTextColor(ILI9341_WHITE);
    tft.setCursor(40, 100);
    tft.println("Hello, CYD!");
}

void loop() {
    // Nothing to do
}
"""

    def _get_touch_demo_example(self) -> str:
        """Get touch demo example code."""
        return """// Touch Demo for CYD
#include <Adafruit_ILI9341.h>
#include <XPT2046_Touchscreen.h>
#include <SPI.h>

// Display pins
#define TFT_DC 2
#define TFT_CS 15
#define TFT_BL 21

// Touch pins
#define TOUCH_CS 33
#define TOUCH_IRQ 36

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
XPT2046_Touchscreen touch(TOUCH_CS, TOUCH_IRQ);

void setup() {
    // Initialize backlight
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    
    // Initialize display
    tft.begin();
    tft.setRotation(1);
    tft.fillScreen(ILI9341_BLACK);
    
    // Initialize touch
    touch.begin();
    touch.setRotation(1);
    
    // Draw instructions
    tft.setTextSize(2);
    tft.setTextColor(ILI9341_WHITE);
    tft.setCursor(10, 10);
    tft.println("Touch the screen!");
}

void loop() {
    if (touch.touched()) {
        TS_Point p = touch.getPoint();
        
        // Map touch coordinates to display
        int x = map(p.x, 200, 3800, 0, 320);
        int y = map(p.y, 200, 3800, 0, 240);
        
        // Constrain to screen bounds
        x = constrain(x, 0, 319);
        y = constrain(y, 0, 239);
        
        // Draw a circle at touch point
        tft.fillCircle(x, y, 5, ILI9341_CYAN);
        
        // Display coordinates
        tft.fillRect(0, 220, 320, 20, ILI9341_BLACK);
        tft.setTextSize(1);
        tft.setTextColor(ILI9341_GREEN);
        tft.setCursor(10, 225);
        tft.printf("X: %d  Y: %d", x, y);
    }
    
    delay(50);
}
"""

    def _get_wifi_scanner_example(self) -> str:
        """Get WiFi scanner example code."""
        return """// WiFi Scanner for CYD
#include <WiFi.h>
#include <Adafruit_ILI9341.h>
#include <SPI.h>

// Display pins
#define TFT_DC 2
#define TFT_CS 15
#define TFT_BL 21

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);

void setup() {
    // Initialize backlight
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    
    // Initialize display
    tft.begin();
    tft.setRotation(1);
    tft.fillScreen(ILI9341_BLACK);
    
    // Set WiFi to station mode
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);
    
    // Display title
    tft.setTextSize(2);
    tft.setTextColor(ILI9341_CYAN);
    tft.setCursor(10, 10);
    tft.println("WiFi Scanner");
}

void loop() {
    // Start scan
    tft.fillRect(0, 40, 320, 200, ILI9341_BLACK);
    tft.setTextSize(1);
    tft.setTextColor(ILI9341_WHITE);
    tft.setCursor(10, 45);
    tft.println("Scanning...");
    
    int n = WiFi.scanNetworks();
    
    tft.fillRect(0, 40, 320, 200, ILI9341_BLACK);
    tft.setCursor(10, 45);
    tft.printf("Found %d networks\\n\\n", n);
    
    // Display networks
    int y = 65;
    for (int i = 0; i < n && i < 8; i++) {
        // Choose color based on signal strength
        uint16_t color;
        int rssi = WiFi.RSSI(i);
        if (rssi > -50) {
            color = ILI9341_GREEN;
        } else if (rssi > -70) {
            color = ILI9341_YELLOW;
        } else {
            color = ILI9341_RED;
        }
        
        tft.setCursor(10, y);
        tft.setTextColor(color);
        
        // Display SSID and RSSI
        String ssid = WiFi.SSID(i);
        if (ssid.length() > 20) {
            ssid = ssid.substring(0, 20) + "...";
        }
        tft.printf("%s (%d)\\n", ssid.c_str(), rssi);
        
        y += 20;
    }
    
    // Wait before next scan
    delay(5000);
}
"""
