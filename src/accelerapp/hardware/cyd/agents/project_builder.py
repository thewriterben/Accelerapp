"""
Automated project builder for CYD applications.

Provides end-to-end project generation and setup automation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BuildSystem(Enum):
    """Build system types."""
    PLATFORMIO = "platformio"
    ARDUINO_CLI = "arduino-cli"
    ESP_IDF = "esp-idf"
    MAKEFILE = "makefile"


@dataclass
class ProjectSpec:
    """Project specification."""
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    license: str = "MIT"
    build_system: BuildSystem = BuildSystem.PLATFORMIO
    features: List[str] = None
    dependencies: List[str] = None


@dataclass
class ProjectStructure:
    """Generated project structure."""
    root_dir: str
    source_files: Dict[str, str]
    config_files: Dict[str, str]
    docs: Dict[str, str]
    scripts: Dict[str, str]


class ProjectBuilder:
    """
    Automated project builder for CYD.
    
    Provides:
    - Complete project scaffolding
    - Build system configuration
    - Dependency management
    - Documentation generation
    - Testing framework setup
    - CI/CD configuration
    """

    def __init__(self):
        """Initialize project builder."""
        pass

    def create_project(self, spec: ProjectSpec, output_dir: str) -> ProjectStructure:
        """
        Create complete project structure.
        
        Args:
            spec: Project specification
            output_dir: Output directory path
            
        Returns:
            Generated project structure
        """
        structure = ProjectStructure(
            root_dir=output_dir,
            source_files={},
            config_files={},
            docs={},
            scripts={},
        )
        
        # Generate source files
        structure.source_files["main.cpp"] = self._generate_main_file(spec)
        structure.source_files["config.h"] = self._generate_config_header(spec)
        
        # Generate configuration
        if spec.build_system == BuildSystem.PLATFORMIO:
            structure.config_files["platformio.ini"] = self._generate_platformio_ini(spec)
        elif spec.build_system == BuildSystem.ARDUINO_CLI:
            structure.config_files["sketch.json"] = self._generate_arduino_json(spec)
        
        # Generate documentation
        structure.docs["README.md"] = self._generate_readme(spec)
        structure.docs["LICENSE"] = self._generate_license(spec)
        
        # Generate utility scripts
        structure.scripts["build.sh"] = self._generate_build_script(spec)
        structure.scripts["upload.sh"] = self._generate_upload_script(spec)
        
        return structure

    def _generate_main_file(self, spec: ProjectSpec) -> str:
        """Generate main source file."""
        features = spec.features or []
        has_display = "display" in features
        has_touch = "touch" in features
        has_wifi = "wifi" in features
        
        code = f"""/*
 * {spec.name} - {spec.description}
 * Author: {spec.author}
 * Version: {spec.version}
 * License: {spec.license}
 */

#include "config.h"
#include <Arduino.h>
"""
        
        if has_display:
            code += "#include <Adafruit_ILI9341.h>\n#include <SPI.h>\n"
        if has_touch:
            code += "#include <XPT2046_Touchscreen.h>\n"
        if has_wifi:
            code += "#include <WiFi.h>\n"
        
        code += "\n"
        
        if has_display:
            code += "Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);\n"
        if has_touch:
            code += "XPT2046_Touchscreen touch(TOUCH_CS, TOUCH_IRQ);\n"
        
        code += """
void setup() {
    Serial.begin(115200);
    delay(100);
    
    Serial.println("=================================");
    Serial.printf("Starting %s\\n", PROJECT_NAME);
    Serial.printf("Version: %s\\n", PROJECT_VERSION);
    Serial.println("=================================");
    
""" % (spec.name, spec.version)
        
        if has_display:
            code += """    // Initialize display
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);
    tft.begin();
    tft.setRotation(1);
    tft.fillScreen(ILI9341_BLACK);
    Serial.println("Display initialized");
    
"""
        
        if has_touch:
            code += """    // Initialize touch
    touch.begin();
    touch.setRotation(1);
    Serial.println("Touch initialized");
    
"""
        
        if has_wifi:
            code += """    // Initialize WiFi
    WiFi.mode(WIFI_STA);
    Serial.println("WiFi initialized");
    
"""
        
        code += """    Serial.println("Setup complete!");
}

void loop() {
    // Main application loop
    
"""
        
        if has_touch:
            code += """    // Handle touch input
    if (touch.touched()) {
        TS_Point p = touch.getPoint();
        int x = map(p.x, 200, 3800, 0, 320);
        int y = map(p.y, 200, 3800, 0, 240);
        Serial.printf("Touch at (%d, %d)\\n", x, y);
    }
    
"""
        
        code += """    delay(10);
}
"""
        
        return code.strip()

    def _generate_config_header(self, spec: ProjectSpec) -> str:
        """Generate configuration header file."""
        return f"""/*
 * Configuration for {spec.name}
 */

#ifndef CONFIG_H
#define CONFIG_H

// Project information
#define PROJECT_NAME "{spec.name}"
#define PROJECT_VERSION "{spec.version}"
#define PROJECT_AUTHOR "{spec.author}"

// Pin definitions for CYD (ESP32-2432S028)
#define TFT_DC 2
#define TFT_CS 15
#define TFT_RST -1
#define TFT_BL 21
#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_MISO 12

#define TOUCH_CS 33
#define TOUCH_IRQ 36
#define TOUCH_MOSI 32
#define TOUCH_MISO 39
#define TOUCH_SCLK 25

#define SD_CS 5
#define LED_PIN 17
#define LDR_PIN 34

// Display settings
#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 240
#define SCREEN_ROTATION 1

// Application settings
#define SERIAL_BAUD 115200
#define LOOP_DELAY_MS 10

#endif // CONFIG_H
"""

    def _generate_platformio_ini(self, spec: ProjectSpec) -> str:
        """Generate PlatformIO configuration."""
        deps = spec.dependencies or []
        
        config = f"""; PlatformIO Project Configuration for {spec.name}

[env:esp32]
platform = espressif32
board = esp32dev
framework = arduino

; Serial Monitor
monitor_speed = 115200
monitor_filters = esp32_exception_decoder

; Upload settings
upload_speed = 921600

; Build flags
build_flags = 
    -D PROJECT_NAME=\\"{spec.name}\\"
    -D PROJECT_VERSION=\\"{spec.version}\\"

; Dependencies
lib_deps = 
    adafruit/Adafruit ILI9341 @ ^1.5.12
    adafruit/Adafruit GFX Library @ ^1.11.5
    paulstoffregen/XPT2046_Touchscreen @ ^1.4
"""
        
        for dep in deps:
            config += f"    {dep}\n"
        
        return config.strip()

    def _generate_arduino_json(self, spec: ProjectSpec) -> str:
        """Generate Arduino CLI configuration."""
        return f"""{{
  "name": "{spec.name}",
  "version": "{spec.version}",
  "author": "{spec.author}",
  "license": "{spec.license}",
  "description": "{spec.description}",
  "dependencies": {{
    "Adafruit ILI9341": "1.5.12",
    "Adafruit GFX Library": "1.11.5",
    "XPT2046_Touchscreen": "1.4"
  }}
}}
"""

    def _generate_readme(self, spec: ProjectSpec) -> str:
        """Generate README documentation."""
        features = spec.features or []
        
        return f"""# {spec.name}

{spec.description}

## Features

{chr(10).join(f"- {f.title()}" for f in features)}

## Hardware Requirements

- ESP32-2432S028 (CYD) board
- USB cable for programming and power

## Software Requirements

- PlatformIO or Arduino IDE
- Required libraries (automatically installed via PlatformIO)

## Installation

### Using PlatformIO

```bash
# Clone or download this project
cd {spec.name.lower().replace(" ", "_")}

# Build the project
pio run

# Upload to board
pio run --target upload

# Open serial monitor
pio device monitor
```

### Using Arduino IDE

1. Open `{spec.name.lower().replace(" ", "_")}.ino`
2. Install required libraries via Library Manager
3. Select board: "ESP32 Dev Module"
4. Select correct COM port
5. Click Upload

## Configuration

Edit `config.h` to customize:
- Pin assignments
- Display settings
- Application parameters

## Usage

[Add specific usage instructions here]

## Development

Built with Accelerapp CYD Code Generator

- Version: {spec.version}
- Author: {spec.author}
- License: {spec.license}

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the {spec.license} License - see the LICENSE file for details.

## Acknowledgments

- ESP32 community
- Adafruit for display libraries
- witnessmenow for CYD reference designs
"""

    def _generate_license(self, spec: ProjectSpec) -> str:
        """Generate LICENSE file."""
        if spec.license == "MIT":
            return f"""MIT License

Copyright (c) 2025 {spec.author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        return f"{spec.license} License\n\nCopyright (c) 2025 {spec.author}\n"

    def _generate_build_script(self, spec: ProjectSpec) -> str:
        """Generate build script."""
        if spec.build_system == BuildSystem.PLATFORMIO:
            return """#!/bin/bash
# Build script for PlatformIO

echo "Building project..."
pio run

if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
"""
        return "# Build script not configured\n"

    def _generate_upload_script(self, spec: ProjectSpec) -> str:
        """Generate upload script."""
        if spec.build_system == BuildSystem.PLATFORMIO:
            return """#!/bin/bash
# Upload script for PlatformIO

echo "Uploading to device..."
pio run --target upload

if [ $? -eq 0 ]; then
    echo "Upload successful!"
    echo "Opening serial monitor..."
    pio device monitor
else
    echo "Upload failed!"
    exit 1
fi
"""
        return "# Upload script not configured\n"

    def validate_project(self, structure: ProjectStructure) -> List[str]:
        """
        Validate generated project.
        
        Args:
            structure: Project structure to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if "main.cpp" not in structure.source_files:
            errors.append("Missing main source file")
        
        if "README.md" not in structure.docs:
            errors.append("Missing README documentation")
        
        if not structure.config_files:
            errors.append("Missing build configuration")
        
        return errors
