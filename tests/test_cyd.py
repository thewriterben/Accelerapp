"""
Tests for CYD (Cheap Yellow Display) ecosystem integration.
"""

import pytest
from datetime import datetime


def test_cyd_module_import():
    """Test CYD module can be imported."""
    from accelerapp.hardware import cyd
    assert cyd is not None


def test_hal_imports():
    """Test HAL components can be imported."""
    from accelerapp.hardware.cyd import (
        DisplayDriver,
        TouchController,
        GPIOManager,
        PowerManager,
        SensorMonitor,
    )
    
    assert DisplayDriver is not None
    assert TouchController is not None
    assert GPIOManager is not None
    assert PowerManager is not None
    assert SensorMonitor is not None


def test_community_imports():
    """Test community integration can be imported."""
    from accelerapp.hardware.cyd import (
        CommunityIntegration,
        TemplateManager,
        ExampleLoader,
    )
    
    assert CommunityIntegration is not None
    assert TemplateManager is not None
    assert ExampleLoader is not None


def test_agents_imports():
    """Test agent components can be imported."""
    from accelerapp.hardware.cyd import (
        CYDCodeGenerator,
        HardwareOptimizer,
        ProjectBuilder,
    )
    
    assert CYDCodeGenerator is not None
    assert HardwareOptimizer is not None
    assert ProjectBuilder is not None


def test_digital_twin_imports():
    """Test digital twin components can be imported."""
    from accelerapp.hardware.cyd import (
        CYDSimulator,
        CYDTwinModel,
        CYDMonitor,
    )
    
    assert CYDSimulator is not None
    assert CYDTwinModel is not None
    assert CYDMonitor is not None


# HAL Tests

def test_display_driver_initialization():
    """Test DisplayDriver initialization."""
    from accelerapp.hardware.cyd.hal import DisplayDriver
    
    driver = DisplayDriver()
    assert driver is not None
    assert driver.config.width == 320
    assert driver.config.height == 240


def test_display_driver_code_generation():
    """Test DisplayDriver code generation."""
    from accelerapp.hardware.cyd.hal import DisplayDriver
    
    driver = DisplayDriver()
    
    arduino_code = driver.generate_code("arduino")
    assert "Adafruit_ILI9341" in arduino_code
    assert "TFT_DC" in arduino_code
    
    esp_idf_code = driver.generate_code("esp-idf")
    assert "spi_bus_config_t" in esp_idf_code
    
    micropython_code = driver.generate_code("micropython")
    assert "import ili9341" in micropython_code


def test_touch_controller_initialization():
    """Test TouchController initialization."""
    from accelerapp.hardware.cyd.hal import TouchController
    
    controller = TouchController()
    assert controller is not None
    assert controller.config.cs_pin == 33


def test_touch_controller_code_generation():
    """Test TouchController code generation."""
    from accelerapp.hardware.cyd.hal import TouchController
    
    controller = TouchController()
    
    arduino_code = controller.generate_code("arduino")
    assert "XPT2046_Touchscreen" in arduino_code
    assert "TOUCH_CS" in arduino_code


def test_gpio_manager():
    """Test GPIOManager functionality."""
    from accelerapp.hardware.cyd.hal import GPIOManager, PinMode, PinState
    
    manager = GPIOManager()
    
    # Test pin configuration
    result = manager.configure_pin(22, PinMode.OUTPUT, PinState.LOW, "LED")
    assert result is True
    
    # Test reserved pin rejection
    result = manager.configure_pin(2, PinMode.OUTPUT)  # TFT_DC is reserved
    assert result is False
    
    # Test digital write
    result = manager.digital_write(22, PinState.HIGH)
    assert result is True
    
    # Test digital read
    state = manager.digital_read(22)
    assert state == PinState.HIGH


def test_gpio_manager_code_generation():
    """Test GPIOManager code generation."""
    from accelerapp.hardware.cyd.hal import GPIOManager, PinMode, PinState
    
    manager = GPIOManager()
    manager.configure_pin(22, PinMode.OUTPUT, PinState.LOW, "LED")
    
    arduino_code = manager.generate_code("arduino")
    assert "pinMode(22, OUTPUT)" in arduino_code
    
    esp_idf_code = manager.generate_code("esp-idf")
    assert "gpio_set_direction" in esp_idf_code


def test_power_manager():
    """Test PowerManager functionality."""
    from accelerapp.hardware.cyd.hal import PowerManager, PowerMode
    
    manager = PowerManager()
    
    assert manager.get_power_mode() == PowerMode.ACTIVE
    
    result = manager.set_power_mode(PowerMode.LIGHT_SLEEP)
    assert result is True
    assert manager.get_power_mode() == PowerMode.LIGHT_SLEEP
    
    stats = manager.get_statistics()
    assert "uptime_seconds" in stats
    assert "current_mode" in stats


def test_sensor_monitor():
    """Test SensorMonitor functionality."""
    from accelerapp.hardware.cyd.hal import SensorMonitor
    
    monitor = SensorMonitor()
    
    stats = monitor.get_system_stats()
    assert "temperature_c" in stats
    assert "cpu_frequency_mhz" in stats
    
    arduino_code = monitor.generate_code("arduino")
    assert "readTemperature" in arduino_code
    assert "LDR_PIN" in arduino_code


# Community Integration Tests

def test_community_integration():
    """Test CommunityIntegration."""
    from accelerapp.hardware.cyd.community import CommunityIntegration, ProjectType
    
    integration = CommunityIntegration()
    
    projects = integration.list_projects()
    assert len(projects) > 0
    
    marauder_info = integration.get_project_info(ProjectType.MARAUDER)
    assert marauder_info is not None
    assert marauder_info.name == "ESP32 Marauder"
    
    config = integration.generate_project_config(ProjectType.MARAUDER)
    assert "project_name" in config


def test_template_manager():
    """Test TemplateManager."""
    from accelerapp.hardware.cyd.community import TemplateManager, TemplateType
    
    manager = TemplateManager()
    
    templates = manager.list_templates()
    assert len(templates) > 0
    
    template = manager.get_template(TemplateType.IOT_DASHBOARD)
    assert template is not None
    assert template.name == "IoT Dashboard"
    
    code = manager.generate_project(TemplateType.IOT_DASHBOARD)
    assert "IoT Dashboard" in code


def test_example_loader():
    """Test ExampleLoader."""
    from accelerapp.hardware.cyd.community import ExampleLoader, ExampleCategory
    
    loader = ExampleLoader()
    
    examples = loader.list_examples()
    assert len(examples) > 0
    
    hello_world = loader.get_example("hello_world")
    assert hello_world is not None
    assert hello_world.category == ExampleCategory.BASIC
    
    basic_examples = loader.list_examples(category=ExampleCategory.BASIC)
    assert len(basic_examples) > 0


# Agent Tests

def test_code_generator():
    """Test CYDCodeGenerator."""
    from accelerapp.hardware.cyd.agents import CYDCodeGenerator, GenerationRequest, CodeStyle
    
    generator = CYDCodeGenerator()
    
    request = GenerationRequest(
        project_name="TestProject",
        description="Test project",
        requirements=["display", "touch"],
        style=CodeStyle.DOCUMENTED,
        platform="arduino",
    )
    
    result = generator.generate_project(request)
    assert result is not None
    assert "TestProject" in result.main_code
    assert len(result.dependencies) > 0


def test_hardware_optimizer():
    """Test HardwareOptimizer."""
    from accelerapp.hardware.cyd.agents import HardwareOptimizer, OptimizationGoal
    
    optimizer = HardwareOptimizer()
    
    config = {
        "display": {"refresh_rate": 60},
        "pins": {22: "LED", 23: "Button"},
    }
    
    analysis = optimizer.analyze_configuration(config)
    assert "performance_score" in analysis
    
    result = optimizer.optimize_for_goal(config, OptimizationGoal.PERFORMANCE)
    assert len(result.recommendations) > 0
    assert result.estimated_improvement > 0


def test_project_builder():
    """Test ProjectBuilder."""
    from accelerapp.hardware.cyd.agents import ProjectBuilder, ProjectSpec, BuildSystem
    
    builder = ProjectBuilder()
    
    spec = ProjectSpec(
        name="TestProject",
        description="Test description",
        author="Test Author",
        build_system=BuildSystem.PLATFORMIO,
        features=["display", "touch"],
    )
    
    structure = builder.create_project(spec, "/tmp/test_project")
    assert structure is not None
    assert "main.cpp" in structure.source_files
    assert "README.md" in structure.docs
    
    errors = builder.validate_project(structure)
    assert len(errors) == 0


# Digital Twin Tests

def test_cyd_simulator():
    """Test CYDSimulator."""
    from accelerapp.hardware.cyd.digital_twin import CYDSimulator, SimulationMode
    
    simulator = CYDSimulator(SimulationMode.REALTIME)
    
    simulator.start()
    assert simulator._running is True
    
    # Test display operations
    simulator.set_pixel(100, 100, 0xFFFF)
    pixel = simulator.get_pixel(100, 100)
    assert pixel == 0xFFFF
    
    # Test touch simulation
    simulator.simulate_touch(160, 120)
    points = simulator.get_touch_points()
    assert len(points) == 1
    assert points[0] == (160, 120)
    
    # Test GPIO
    simulator.set_gpio(22, True)
    assert simulator.get_gpio(22) is True
    
    # Get statistics
    stats = simulator.get_statistics()
    assert "cpu_frequency_mhz" in stats
    assert "power_consumption_w" in stats
    
    simulator.stop()
    assert simulator._running is False


def test_cyd_twin_model():
    """Test CYDTwinModel."""
    from accelerapp.hardware.cyd.digital_twin import CYDTwinModel, TwinStatus
    
    model = CYDTwinModel(
        device_id="cyd-001",
        device_name="Test CYD"
    )
    
    assert model.device_id == "cyd-001"
    assert model.status == TwinStatus.CREATED
    
    # Update states
    model.update_display_state(brightness=200, backlight_on=True)
    assert model.display.brightness == 200
    
    model.update_system_state(cpu_frequency_mhz=160, temperature_c=45.0)
    assert model.system.cpu_frequency_mhz == 160
    
    # GPIO
    model.set_gpio(22, True)
    assert model.get_gpio(22) is True
    
    # Health check
    assert model.is_healthy() is True
    
    # Telemetry
    model.record_telemetry({"temperature": 45.0, "power": 150.0})
    telemetry = model.get_telemetry(limit=1)
    assert len(telemetry) == 1
    
    # Serialization
    data = model.to_dict()
    assert data["device_id"] == "cyd-001"


def test_cyd_monitor():
    """Test CYDMonitor."""
    from accelerapp.hardware.cyd.digital_twin import CYDMonitor, AlertLevel
    
    monitor = CYDMonitor()
    
    # Register device
    monitor.register_device("cyd-001", {"name": "Test CYD"})
    
    # Update with normal state
    monitor.update_device_state("cyd-001", {
        "temperature_c": 35.0,
        "power_consumption_mw": 150.0,
        "free_heap_bytes": 100000,
    })
    
    # Check alerts
    alerts = monitor.get_alerts(device_id="cyd-001")
    assert isinstance(alerts, list)
    
    # Update with warning state
    monitor.update_device_state("cyd-001", {
        "temperature_c": 65.0,  # Above warning threshold
    })
    
    alerts = monitor.get_alerts(device_id="cyd-001", level=AlertLevel.WARNING)
    assert len(alerts) > 0
    
    # Get metrics
    metrics = monitor.get_metrics(device_id="cyd-001", metric_name="temperature")
    assert len(metrics) > 0
    
    # Get summaries
    device_summary = monitor.get_device_summary("cyd-001")
    assert device_summary is not None
    assert device_summary["device_id"] == "cyd-001"
    
    system_summary = monitor.get_system_summary()
    assert system_summary["total_devices"] == 1


def test_hardware_module_exports():
    """Test that CYD components are exported from hardware module."""
    from accelerapp.hardware import (
        DisplayDriver,
        TouchController,
        GPIOManager,
        PowerManager,
        SensorMonitor,
        CommunityIntegration,
        TemplateManager,
        ExampleLoader,
        CYDCodeGenerator,
        HardwareOptimizer,
        ProjectBuilder,
        CYDSimulator,
        CYDTwinModel,
        CYDMonitor,
    )
    
    # Verify all imports work
    assert DisplayDriver is not None
    assert TouchController is not None
    assert GPIOManager is not None
    assert PowerManager is not None
    assert SensorMonitor is not None
    assert CommunityIntegration is not None
    assert TemplateManager is not None
    assert ExampleLoader is not None
    assert CYDCodeGenerator is not None
    assert HardwareOptimizer is not None
    assert ProjectBuilder is not None
    assert CYDSimulator is not None
    assert CYDTwinModel is not None
    assert CYDMonitor is not None
