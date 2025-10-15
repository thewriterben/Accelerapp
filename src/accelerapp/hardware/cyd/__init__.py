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
    DisplayRotation,
    ColorDepth,
    DisplayConfig,
    TouchEvent,
    TouchPoint,
    TouchConfig,
    PinMode,
    PinState,
    PinConfig,
    PowerMode,
    PowerConfig,
    SensorType,
    SensorReading,
)

from .community import (
    CommunityIntegration,
    TemplateManager,
    ExampleLoader,
    ProjectType,
    ProjectInfo,
    TemplateType,
    Template,
    ExampleCategory,
    Example,
)

from .agents import (
    CYDCodeGenerator,
    HardwareOptimizer,
    ProjectBuilder,
    CodeStyle,
    GenerationRequest,
    GeneratedCode,
    OptimizationGoal,
    OptimizationResult,
    BuildSystem,
    ProjectSpec,
    ProjectStructure,
)

from .digital_twin import (
    CYDSimulator,
    CYDTwinModel,
    CYDMonitor,
    SimulationMode,
    SimulatedState,
    TwinStatus,
    DisplayState,
    TouchState,
    PowerState,
    SystemState,
    AlertLevel,
    Alert,
    Metric,
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
