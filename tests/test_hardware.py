"""
Tests for hardware abstraction layer.
"""

import pytest


def test_hardware_module_import():
    """Test hardware module can be imported."""
    from accelerapp.hardware import HardwareAbstractionLayer, HardwareComponent, ComponentFactory
    assert HardwareAbstractionLayer is not None
    assert HardwareComponent is not None
    assert ComponentFactory is not None


def test_hardware_component_creation():
    """Test creating a hardware component."""
    from accelerapp.hardware import HardwareComponent
    
    component = HardwareComponent(
        component_id='led1',
        component_type='led',
        pins=[13],
        config={'brightness': 255},
        capabilities=['digital_output'],
    )
    
    assert component.component_id == 'led1'
    assert component.component_type == 'led'
    assert component.uses_pin(13)
    assert not component.uses_pin(14)


def test_component_factory_create():
    """Test component factory creation."""
    from accelerapp.hardware import ComponentFactory
    
    config = {
        'name': 'led1',
        'pin': 13,
        'brightness': 255,
    }
    
    component = ComponentFactory.create_component('led', config)
    
    assert component.component_id == 'led1'
    assert component.component_type == 'led'
    assert 13 in component.pins


def test_component_factory_capabilities():
    """Test component factory assigns capabilities."""
    from accelerapp.hardware import ComponentFactory
    
    led = ComponentFactory.create_component('led', {'pin': 13})
    assert 'digital_output' in led.capabilities
    
    button = ComponentFactory.create_component('button', {'pin': 2})
    assert 'digital_input' in button.capabilities
    
    sensor = ComponentFactory.create_component('sensor', {'pin': 'A0'})
    assert 'analog_input' in sensor.capabilities


def test_hal_initialization():
    """Test HAL initialization."""
    from accelerapp.hardware import HardwareAbstractionLayer
    
    hal = HardwareAbstractionLayer()
    assert len(hal.components) == 0
    assert len(hal.pin_usage) == 0


def test_hal_add_component():
    """Test adding component to HAL."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    component = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    result = hal.add_component(component)
    
    assert result is True
    assert 'led1' in hal.components
    assert 13 in hal.pin_usage


def test_hal_pin_conflict_detection():
    """Test pin conflict detection."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    # Add first component
    led1 = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    hal.add_component(led1)
    
    # Try to add second component with same pin
    led2 = ComponentFactory.create_component('led', {'name': 'led2', 'pin': 13})
    result = hal.add_component(led2)
    
    assert result is False


def test_hal_remove_component():
    """Test removing component from HAL."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    component = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    hal.add_component(component)
    
    result = hal.remove_component('led1')
    assert result is True
    assert 'led1' not in hal.components
    assert 13 not in hal.pin_usage


def test_hal_get_component():
    """Test getting component from HAL."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    component = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    hal.add_component(component)
    
    retrieved = hal.get_component('led1')
    assert retrieved is not None
    assert retrieved.component_id == 'led1'


def test_hal_get_components_by_type():
    """Test getting components by type."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    # Add multiple LEDs
    led1 = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    led2 = ComponentFactory.create_component('led', {'name': 'led2', 'pin': 12})
    button = ComponentFactory.create_component('button', {'name': 'btn1', 'pin': 2})
    
    hal.add_component(led1)
    hal.add_component(led2)
    hal.add_component(button)
    
    leds = hal.get_components_by_type('led')
    assert len(leds) == 2
    
    buttons = hal.get_components_by_type('button')
    assert len(buttons) == 1


def test_hal_get_used_pins():
    """Test getting used pins."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    led = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    button = ComponentFactory.create_component('button', {'name': 'btn1', 'pin': 2})
    
    hal.add_component(led)
    hal.add_component(button)
    
    used_pins = hal.get_used_pins()
    assert 13 in used_pins
    assert 2 in used_pins


def test_hal_get_available_pins():
    """Test getting available pins."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    led = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    hal.add_component(led)
    
    all_pins = [2, 3, 4, 5, 13]
    available = hal.get_available_pins(all_pins)
    
    assert 13 not in available
    assert 2 in available


def test_hal_validation():
    """Test HAL configuration validation."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    # Add valid components
    led = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    hal.add_component(led)
    
    errors = hal.validate_configuration()
    assert len(errors) == 0


def test_hal_stats():
    """Test HAL statistics."""
    from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
    
    hal = HardwareAbstractionLayer()
    
    led = ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13})
    button = ComponentFactory.create_component('button', {'name': 'btn1', 'pin': 2})
    
    hal.add_component(led)
    hal.add_component(button)
    
    stats = hal.get_stats()
    
    assert stats['total_components'] == 2
    assert stats['pins_used'] == 2
    assert 'led' in stats['components_by_type']
    assert 'button' in stats['components_by_type']
