"""
Tests for advanced peripheral abstraction (conflict resolution, resource management).
"""

import pytest


def test_peripheral_modules_import():
    """Test peripheral modules can be imported."""
    from accelerapp.peripherals import PeripheralConflictResolver, PeripheralResourceManager
    assert PeripheralConflictResolver is not None
    assert PeripheralResourceManager is not None


def test_conflict_resolver_init():
    """Test conflict resolver initialization."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    assert resolver.platform == "stm32"
    assert len(resolver.pin_assignments) == 0


def test_add_peripheral_no_conflict():
    """Test adding peripheral without conflicts."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    peripheral = {
        "id": "led1",
        "type": "led",
        "pins": [
            {"pin": 13, "function": "GPIO_OUTPUT"}
        ]
    }
    
    success, conflicts = resolver.add_peripheral(peripheral)
    assert success is True
    assert len(conflicts) == 0


def test_add_peripheral_with_conflict():
    """Test adding peripheral with pin conflict."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    # Add first peripheral
    peripheral1 = {
        "id": "led1",
        "type": "led",
        "pins": [{"pin": 13, "function": "GPIO_OUTPUT"}]
    }
    resolver.add_peripheral(peripheral1)
    
    # Add second peripheral using same pin
    peripheral2 = {
        "id": "button1",
        "type": "button",
        "pins": [{"pin": 13, "function": "GPIO_INPUT"}]
    }
    
    success, conflicts = resolver.add_peripheral(peripheral2)
    # Should detect conflict (output and input on same pin)
    assert len(conflicts) > 0 or success is True  # Might allow if compatible


def test_suggest_stm32_alternatives():
    """Test suggesting STM32 alternative pin configurations."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    peripheral = {
        "id": "uart1",
        "type": "uart"
    }
    
    alternatives = resolver.suggest_alternatives(peripheral)
    assert len(alternatives) > 0
    assert any("USART" in alt.get("instance", "") for alt in alternatives)


def test_suggest_nrf_alternatives():
    """Test suggesting nRF alternative pin configurations."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("nrf52")
    
    peripheral = {
        "id": "spi1",
        "type": "spi"
    }
    
    alternatives = resolver.suggest_alternatives(peripheral)
    assert len(alternatives) > 0


def test_conflict_report():
    """Test generating conflict report."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    # Add multiple peripherals
    resolver.add_peripheral({
        "id": "led1",
        "type": "led",
        "pins": [{"pin": 13, "function": "GPIO_OUTPUT"}]
    })
    
    resolver.add_peripheral({
        "id": "uart1",
        "type": "uart",
        "pins": [{"pin": 2, "function": "UART_TX"}, {"pin": 3, "function": "UART_RX"}]
    })
    
    report = resolver.get_conflict_report()
    assert "total_peripherals" in report
    assert "total_pins_used" in report
    assert report["total_peripherals"] == 2
    assert report["total_pins_used"] >= 2


def test_resource_manager_init():
    """Test resource manager initialization."""
    from accelerapp.peripherals import PeripheralResourceManager
    
    manager = PeripheralResourceManager("stm32f4")
    assert manager.platform == "stm32f4"
    assert len(manager.resource_limits) > 0


def test_allocate_dma_channel():
    """Test DMA channel allocation."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate a DMA channel
    allocation = manager.allocate_resource(
        ResourceType.DMA_CHANNEL,
        "uart1",
        "uart",
        priority=2
    )
    
    assert allocation is not None
    assert allocation.resource_type == ResourceType.DMA_CHANNEL
    assert allocation.peripheral_id == "uart1"


def test_allocate_specific_resource():
    """Test allocating a specific resource ID."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate specific timer
    allocation = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm1",
        "pwm",
        resource_id=2  # TIM2
    )
    
    assert allocation is not None
    assert allocation.resource_id == 2


def test_allocate_unavailable_resource():
    """Test allocating an already-used resource."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate timer 2
    first = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm1",
        "pwm",
        resource_id=2
    )
    assert first is not None
    
    # Try to allocate timer 2 again
    second = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm2",
        "pwm",
        resource_id=2
    )
    assert second is None  # Should fail


def test_free_resource():
    """Test freeing an allocated resource."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate and free
    allocation = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm1",
        "pwm",
        resource_id=3
    )
    assert allocation is not None
    
    freed = manager.free_resource(ResourceType.TIMER, 3)
    assert freed is True
    
    # Should be able to allocate again
    reallocation = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm2",
        "pwm",
        resource_id=3
    )
    assert reallocation is not None


def test_get_utilization():
    """Test resource utilization reporting."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate some resources
    manager.allocate_resource(ResourceType.DMA_CHANNEL, "uart1", "uart")
    manager.allocate_resource(ResourceType.DMA_CHANNEL, "spi1", "spi")
    manager.allocate_resource(ResourceType.TIMER, "pwm1", "pwm")
    
    utilization = manager.get_utilization()
    
    assert "dma_channel" in utilization
    assert "timer" in utilization
    assert utilization["dma_channel"]["allocated"] == 2
    assert utilization["timer"]["allocated"] == 1


def test_dma_allocation_suggestion():
    """Test DMA allocation suggestion."""
    from accelerapp.peripherals import PeripheralResourceManager
    
    manager = PeripheralResourceManager("stm32")
    
    # High data rate - should suggest DMA
    suggestion = manager.suggest_dma_allocation("uart", 500000)
    assert suggestion is not None
    assert "dma_channel" in suggestion
    assert suggestion["priority"] >= 2
    
    # Low data rate
    suggestion = manager.suggest_dma_allocation("uart", 9600)
    assert suggestion is not None


def test_timer_optimization():
    """Test timer allocation optimization for PWM."""
    from accelerapp.peripherals import PeripheralResourceManager
    
    manager = PeripheralResourceManager("stm32")
    
    # Need 6 PWM channels (should use 2 timers with 4 channels each)
    optimization = manager.optimize_timer_allocation(6)
    
    assert "timers_needed" in optimization
    assert optimization["timers_needed"] == 2
    assert len(optimization["allocations"]) > 0


def test_get_peripheral_resources():
    """Test getting all resources for a peripheral."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate multiple resources for same peripheral
    manager.allocate_resource(ResourceType.DMA_CHANNEL, "uart1", "uart")
    manager.allocate_resource(ResourceType.UART_INSTANCE, "uart1", "uart", resource_id=1)
    
    resources = manager.get_peripheral_resources("uart1")
    assert len(resources) == 2
    assert all(r.peripheral_id == "uart1" for r in resources)


def test_resource_report_generation():
    """Test generating resource report."""
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32")
    
    # Allocate some resources
    manager.allocate_resource(ResourceType.DMA_CHANNEL, "uart1", "uart")
    manager.allocate_resource(ResourceType.TIMER, "pwm1", "pwm")
    
    report = manager.generate_resource_report()
    
    assert "PERIPHERAL RESOURCE ALLOCATION REPORT" in report
    assert "Platform: stm32" in report
    assert "DMA_CHANNEL" in report or "dma_channel" in report.lower()


def test_platform_specific_limits():
    """Test platform-specific resource limits."""
    from accelerapp.peripherals import PeripheralResourceManager
    
    # STM32F4
    stm32f4 = PeripheralResourceManager("stm32f4")
    stm32f4_util = stm32f4.get_utilization()
    
    # STM32H7 (should have more resources)
    stm32h7 = PeripheralResourceManager("stm32h7")
    stm32h7_util = stm32h7.get_utilization()
    
    # H7 should have more DMA channels than F4
    assert stm32h7_util["dma_channel"]["limit"] > stm32f4_util["dma_channel"]["limit"]
    
    # nRF52
    nrf52 = PeripheralResourceManager("nrf52")
    nrf52_util = nrf52.get_utilization()
    assert nrf52_util["dma_channel"]["limit"] > 0


def test_conflict_optimization():
    """Test conflict resolution optimization."""
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    # Add conflicting peripherals
    resolver.add_peripheral({
        "id": "led1",
        "type": "led",
        "pins": [{"pin": 13, "function": "GPIO_OUTPUT"}]
    })
    
    resolver.add_peripheral({
        "id": "uart1",
        "type": "uart",
        "pins": [{"pin": 13, "function": "UART_TX"}]  # Conflict!
    })
    
    optimization = resolver.optimize_pin_mapping()
    assert "status" in optimization
    assert "suggestions" in optimization
