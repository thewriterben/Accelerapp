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

from .agents import (
    BuildSystem,
    CodeStyle,
    CYDCodeGenerator,
    GeneratedCode,
    GenerationRequest,
    HardwareOptimizer,
    OptimizationGoal,
    OptimizationResult,
    ProjectBuilder,
    ProjectSpec,
    ProjectStructure,
)
from .community import (
    CommunityIntegration,
    Example,
    ExampleCategory,
    ExampleLoader,
    ProjectInfo,
    ProjectType,
    Template,
    TemplateManager,
    TemplateType,
)
from .digital_twin import (
    Alert,
    AlertLevel,
    CYDMonitor,
    CYDSimulator,
    CYDTwinModel,
    DisplayState,
    Metric,
    PowerState,
    SimulatedState,
    SimulationMode,
    SystemState,
    TouchState,
    TwinStatus,
)
from .hal import (
    ColorDepth,
    DisplayConfig,
    DisplayDriver,
    DisplayRotation,
    GPIOManager,
    PinConfig,
    PinMode,
    PinState,
    PowerConfig,
    PowerManager,
    PowerMode,
    SensorMonitor,
    SensorReading,
    SensorType,
    TouchConfig,
    TouchController,
    TouchEvent,
    TouchPoint,
)

__all__ = [
    # HAL Components
    "DisplayDriver",
    "TouchController",
    "GPIOManager",
    "PowerManager",
    "SensorMonitor",
    "DisplayRotation",
    "ColorDepth",
    "DisplayConfig",
    "TouchEvent",
    "TouchPoint",
    "TouchConfig",
    "PinMode",
    "PinState",
    "PinConfig",
    "PowerMode",
    "PowerConfig",
    "SensorType",
    "SensorReading",
    # Community
    "CommunityIntegration",
    "TemplateManager",
    "ExampleLoader",
    "ProjectType",
    "ProjectInfo",
    "TemplateType",
    "Template",
    "ExampleCategory",
    "Example",
    # Agents
    "CYDCodeGenerator",
    "HardwareOptimizer",
    "ProjectBuilder",
    "CodeStyle",
    "GenerationRequest",
    "GeneratedCode",
    "OptimizationGoal",
    "OptimizationResult",
    "BuildSystem",
    "ProjectSpec",
    "ProjectStructure",
    # Digital Twin
    "CYDSimulator",
    "CYDTwinModel",
    "CYDMonitor",
    "SimulationMode",
    "SimulatedState",
    "TwinStatus",
    "DisplayState",
    "TouchState",
    "PowerState",
    "SystemState",
    "AlertLevel",
    "Alert",
    "Metric",
]

__version__ = "1.0.0"
