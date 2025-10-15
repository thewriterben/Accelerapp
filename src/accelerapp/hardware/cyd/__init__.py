"""
ESP32 Cheap Yellow Display (CYD) ecosystem integration for Accelerapp.

Provides comprehensive hardware control and code generation capabilities
for the ESP32-2432S028 (CYD) and related hardware variants.

Features:
- Hardware Abstraction Layer (HAL) for display, touch, GPIO, power, and sensors
- Multi-language bindings (Python, MicroPython, C++, Rust, JavaScript/TypeScript)
- Community project integration and templates
- Agentic code generation and optimization
- Digital twin support for hardware simulation
- TinyML integration for on-device AI
- Predictive maintenance capabilities
"""

from .hal import (
    DisplayDriver,
    TouchController,
    GPIOManager,
    PowerManager,
    SensorMonitor,
)

from .community import (
    CommunityIntegration,
    TemplateManager,
    ExampleLoader,
)

from .agents import (
    CYDCodeGenerator,
    HardwareOptimizer,
    ProjectBuilder,
)

from .digital_twin import (
    CYDSimulator,
    CYDTwinModel,
    CYDMonitor,
)

__all__ = [
    # HAL Components
    "DisplayDriver",
    "TouchController",
    "GPIOManager",
    "PowerManager",
    "SensorMonitor",
    # Community
    "CommunityIntegration",
    "TemplateManager",
    "ExampleLoader",
    # Agents
    "CYDCodeGenerator",
    "HardwareOptimizer",
    "ProjectBuilder",
    # Digital Twin
    "CYDSimulator",
    "CYDTwinModel",
    "CYDMonitor",
]

__version__ = "1.0.0"
