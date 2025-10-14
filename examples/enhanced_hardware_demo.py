"""
Accelerapp v2.0 Enhanced Hardware Support Demo
Demonstrates new STM32, Nordic nRF, RTOS, and peripheral management features.
"""

from pathlib import Path
import tempfile


def demo_stm32_platform():
    """Demonstrate STM32F4 and H7 platform support."""
    print("=" * 70)
    print("STM32 Enhanced Platform Demo")
    print("=" * 70)
    
    from accelerapp.platforms.stm32 import STM32F4Platform, STM32H7Platform
    
    # STM32F4 Platform
    print("\n1. STM32F4 Platform:")
    stm32f4 = STM32F4Platform()
    info = stm32f4.get_platform_info()
    print(f"   Series: {info['series']}")
    print(f"   Core: {info['core']}")
    print(f"   Max Clock: {info['max_clock']} MHz")
    print(f"   FPU: {info['fpu']}")
    
    # STM32H7 Platform
    print("\n2. STM32H7 Platform:")
    stm32h7 = STM32H7Platform()
    info = stm32h7.get_platform_info()
    print(f"   Series: {info['series']}")
    print(f"   Core: {info['core']}")
    print(f"   Max Clock: {info['max_clock']} MHz")
    print(f"   FPU: {info['fpu']}")
    print(f"   Cache: {info.get('cache_config', {})}")


def demo_hal_generation():
    """Demonstrate STM32 HAL code generation."""
    print("\n" + "=" * 70)
    print("STM32 HAL Code Generation Demo")
    print("=" * 70)
    
    from accelerapp.platforms.stm32.hal_generator import STM32HALGenerator
    
    generator = STM32HALGenerator("F4")
    
    # GPIO configuration
    print("\n1. GPIO Initialization Code:")
    gpio_config = {
        "ports": ["A", "B"],
        "pins": [
            {"port": "A", "pin": 5, "mode": "OUTPUT_PP", "pull": "NOPULL", "speed": "FREQ_LOW"}
        ]
    }
    gpio_code = generator.generate_gpio_init(gpio_config)
    print(gpio_code[:300] + "...")
    
    # UART configuration
    print("\n2. UART Initialization Code:")
    uart_config = {
        "instance": "USART2",
        "baudrate": 115200
    }
    uart_code = generator.generate_uart_init(uart_config)
    print(uart_code[:300] + "...")


def demo_nordic_platform():
    """Demonstrate Nordic nRF platform support."""
    print("\n" + "=" * 70)
    print("Nordic nRF Platform Demo")
    print("=" * 70)
    
    from accelerapp.platforms.nordic import NRF52Platform, NRF53Platform
    
    # nRF52 Platform
    print("\n1. nRF52 Platform:")
    nrf52 = NRF52Platform()
    info = nrf52.get_platform_info()
    print(f"   Name: {info['display_name']}")
    print(f"   Core: {info['core']}")
    print(f"   Wireless: {info['wireless']['ble']}")
    print(f"   Protocols: {', '.join(info['wireless']['protocols'])}")
    
    # nRF53 Platform
    print("\n2. nRF53 Platform:")
    nrf53 = NRF53Platform()
    info = nrf53.get_platform_info()
    print(f"   Name: {info['display_name']}")
    print(f"   Core: {info['core']}")
    print(f"   Wireless: {info['wireless']['ble']}")
    print(f"   Security: {', '.join(info['security'])}")


def demo_ble_stack():
    """Demonstrate BLE stack generation."""
    print("\n" + "=" * 70)
    print("BLE Stack Generation Demo")
    print("=" * 70)
    
    from accelerapp.platforms.nordic.ble_stack import BLEStack
    
    stack = BLEStack("s140")
    
    # Generate custom service
    print("\n1. Custom BLE Service:")
    service_config = {
        "name": "environmental_sensing",
        "uuid": "0x181A",
        "characteristics": [
            {"name": "temperature", "uuid": "0x2A6E"},
            {"name": "humidity", "uuid": "0x2A6F"}
        ]
    }
    
    service_code = stack.generate_service(service_config)
    print(service_code[:400] + "...")
    
    # Generate advertising
    print("\n2. BLE Advertising Configuration:")
    adv_config = {
        "device_name": "EnvSensor",
        "interval": 300,
        "timeout": 180
    }
    
    adv_code = stack.generate_advertising(adv_config)
    print(adv_code[:300] + "...")


def demo_freertos_tasks():
    """Demonstrate FreeRTOS task generation."""
    print("\n" + "=" * 70)
    print("FreeRTOS Task Generation Demo")
    print("=" * 70)
    
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    # Define tasks
    tasks = [
        {
            "name": "sensor_read",
            "priority": "tskIDLE_PRIORITY + 2",
            "stack_size": 256,
            "period_ms": 100,
            "type": "sensor_read",
            "exec_time_ms": 10
        },
        {
            "name": "data_process",
            "priority": "tskIDLE_PRIORITY + 3",
            "stack_size": 512,
            "period_ms": 1000,
            "type": "actuator_control",
            "exec_time_ms": 50
        },
        {
            "name": "led_control",
            "priority": "tskIDLE_PRIORITY + 1",
            "stack_size": 128,
            "period_ms": 500,
            "type": "periodic",
            "exec_time_ms": 5
        }
    ]
    
    print("\n1. Task Definitions:")
    for task in tasks:
        print(f"   - {task['name']}: Priority={task['priority']}, "
              f"Period={task['period_ms']}ms, Stack={task['stack_size']}")
    
    # Analyze task timing
    print("\n2. Task Timing Analysis:")
    analysis = generator.analyze_task_timing(tasks)
    print(f"   Total Tasks: {analysis['total_tasks']}")
    print(f"   CPU Utilization: {analysis['utilization']:.1f}%")
    print(f"   Priority Distribution: {analysis['priorities']}")
    if analysis['warnings']:
        print(f"   Warnings: {', '.join(analysis['warnings'])}")
    
    # Generate sample task code
    print("\n3. Sample Task Code:")
    task_code = generator.generate_task_function(tasks[0])
    print(task_code[:400] + "...")


def demo_freertos_ipc():
    """Demonstrate FreeRTOS IPC primitives."""
    print("\n" + "=" * 70)
    print("FreeRTOS IPC Primitives Demo")
    print("=" * 70)
    
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    # Queue
    print("\n1. Queue Generation:")
    queue_config = {
        "name": "sensor_data_queue",
        "length": 10,
        "item_size": "sizeof(sensor_data_t)"
    }
    queue_code = ipc.generate_queue(queue_config)
    print(queue_code[:300] + "...")
    
    # Semaphore
    print("\n2. Semaphore Generation:")
    sem_config = {
        "name": "data_ready_sem",
        "type": "binary"
    }
    sem_code = ipc.generate_semaphore(sem_config)
    print(sem_code[:300] + "...")
    
    # Mutex
    print("\n3. Mutex Generation:")
    mutex_config = {
        "name": "i2c_mutex",
        "recursive": False
    }
    mutex_code = ipc.generate_mutex(mutex_config)
    print(mutex_code[:300] + "...")


def demo_conflict_resolution():
    """Demonstrate peripheral conflict detection and resolution."""
    print("\n" + "=" * 70)
    print("Peripheral Conflict Resolution Demo")
    print("=" * 70)
    
    from accelerapp.peripherals import PeripheralConflictResolver
    
    resolver = PeripheralConflictResolver("stm32")
    
    # Add peripherals
    print("\n1. Adding Peripherals:")
    
    peripheral1 = {
        "id": "uart1",
        "type": "uart",
        "pins": [
            {"pin": 2, "function": "UART_TX"},
            {"pin": 3, "function": "UART_RX"}
        ]
    }
    success, conflicts = resolver.add_peripheral(peripheral1)
    print(f"   UART1: {'✓ Success' if success else '✗ Conflict'}")
    
    peripheral2 = {
        "id": "i2c1",
        "type": "i2c",
        "pins": [
            {"pin": 4, "function": "I2C_SCL"},
            {"pin": 5, "function": "I2C_SDA"}
        ]
    }
    success, conflicts = resolver.add_peripheral(peripheral2)
    print(f"   I2C1: {'✓ Success' if success else '✗ Conflict'}")
    
    # Intentional conflict
    peripheral3 = {
        "id": "spi1",
        "type": "spi",
        "pins": [
            {"pin": 2, "function": "SPI_MOSI"},  # Conflicts with UART1 TX
            {"pin": 6, "function": "SPI_MISO"}
        ]
    }
    success, conflicts = resolver.add_peripheral(peripheral3)
    print(f"   SPI1: {'✓ Success' if success else '✗ Conflict'}")
    if conflicts:
        print(f"   Conflicts detected: {conflicts}")
    
    # Generate report
    print("\n2. Conflict Report:")
    report = resolver.get_conflict_report()
    print(f"   Total Peripherals: {report['total_peripherals']}")
    print(f"   Total Pins Used: {report['total_pins_used']}")
    print(f"   Conflicts: {len(report['conflicts'])}")
    
    # Get alternatives
    if report['conflicts']:
        print("\n3. Alternative Suggestions:")
        alternatives = resolver.suggest_alternatives(peripheral3)
        for i, alt in enumerate(alternatives[:3], 1):
            print(f"   Alternative {i}: {alt.get('description', alt)}")


def demo_resource_management():
    """Demonstrate resource allocation and optimization."""
    print("\n" + "=" * 70)
    print("Resource Management Demo")
    print("=" * 70)
    
    from accelerapp.peripherals import PeripheralResourceManager
    from accelerapp.peripherals.resource_manager import ResourceType
    
    manager = PeripheralResourceManager("stm32f4")
    
    # Allocate resources
    print("\n1. Resource Allocation:")
    
    dma1 = manager.allocate_resource(
        ResourceType.DMA_CHANNEL,
        "uart1",
        "uart",
        priority=2
    )
    print(f"   DMA for UART1: Channel {dma1.resource_id if dma1 else 'N/A'}")
    
    dma2 = manager.allocate_resource(
        ResourceType.DMA_CHANNEL,
        "spi1",
        "spi",
        priority=3
    )
    print(f"   DMA for SPI1: Channel {dma2.resource_id if dma2 else 'N/A'}")
    
    timer1 = manager.allocate_resource(
        ResourceType.TIMER,
        "pwm1",
        "pwm",
        resource_id=2
    )
    print(f"   Timer for PWM1: TIM{timer1.resource_id if timer1 else 'N/A'}")
    
    # Get utilization
    print("\n2. Resource Utilization:")
    utilization = manager.get_utilization()
    for resource_type, stats in list(utilization.items())[:5]:
        print(f"   {resource_type}: {stats['allocated']}/{stats['limit']} "
              f"({stats['utilization_percent']:.1f}%)")
    
    # DMA suggestion
    print("\n3. DMA Allocation Suggestion:")
    suggestion = manager.suggest_dma_allocation("spi", 1000000)
    print(f"   Recommendation: {suggestion['recommendation']}")
    print(f"   CPU Savings: {suggestion['estimated_cpu_savings']}%")
    
    # Timer optimization
    print("\n4. Timer Optimization for 8 PWM Channels:")
    optimization = manager.optimize_timer_allocation(8)
    print(f"   Timers Needed: {optimization['timers_needed']}")
    for alloc in optimization['allocations']:
        print(f"   - Timer {alloc['timer']}: {alloc['channels']} channels")


def demo_complete_project_generation():
    """Demonstrate complete project generation."""
    print("\n" + "=" * 70)
    print("Complete Project Generation Demo")
    print("=" * 70)
    
    from accelerapp.platforms import get_platform
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "demo_project"
        
        # STM32F4 Project
        print("\n1. Generating STM32F4 Project:")
        stm32 = get_platform("stm32f4")
        
        spec = {
            "device_name": "IoTSensor",
            "peripherals": [
                {"type": "led", "pin": 13},
                {"type": "button", "pin": 0},
                {"type": "sensor", "pin": 2}
            ],
            "rtos": "freertos"
        }
        
        result = stm32.generate_code(spec, output_dir / "stm32_iot")
        print(f"   Status: {result['status']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Files Generated: {len(result['files_generated'])}")
        for file in result['files_generated'][:3]:
            print(f"     - {Path(file).name}")
        
        # nRF52 Project
        print("\n2. Generating nRF52 BLE Project:")
        nrf52 = get_platform("nrf52")
        
        spec = {
            "device_name": "BLEDevice",
            "peripherals": [
                {"type": "led", "pin": 13},
                {"type": "ble_peripheral"}
            ]
        }
        
        result = nrf52.generate_code(spec, output_dir / "nrf52_ble")
        print(f"   Status: {result['status']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Files Generated: {len(result['files_generated'])}")
        for file in result['files_generated']:
            print(f"     - {Path(file).name}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print(" Accelerapp v2.0 - Enhanced Hardware Support Demo")
    print("=" * 70)
    
    demos = [
        ("STM32 Platforms", demo_stm32_platform),
        ("HAL Generation", demo_hal_generation),
        ("Nordic nRF Platforms", demo_nordic_platform),
        ("BLE Stack", demo_ble_stack),
        ("FreeRTOS Tasks", demo_freertos_tasks),
        ("FreeRTOS IPC", demo_freertos_ipc),
        ("Conflict Resolution", demo_conflict_resolution),
        ("Resource Management", demo_resource_management),
        ("Complete Projects", demo_complete_project_generation),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Error in {name} demo: {e}")
    
    print("\n" + "=" * 70)
    print(" Demo Complete!")
    print("=" * 70)
    print("\nFor more information, see ENHANCED_HARDWARE_SUPPORT.md")


if __name__ == "__main__":
    main()
