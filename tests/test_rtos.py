"""
Tests for RTOS support (FreeRTOS, Zephyr, ThreadX).
"""

import pytest


def test_rtos_module_import():
    """Test RTOS module can be imported."""
    from accelerapp.rtos import FreeRTOSTaskGenerator, FreeRTOSConfigGenerator, IPCPrimitives
    assert FreeRTOSTaskGenerator is not None
    assert FreeRTOSConfigGenerator is not None
    assert IPCPrimitives is not None


def test_freertos_task_generator():
    """Test FreeRTOS task generation."""
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    task_config = {
        "name": "sensor_task",
        "priority": "TASK_PRIORITY_NORMAL",
        "stack_size": 256,
        "period_ms": 100,
        "type": "sensor_read"
    }
    
    task_code = generator.generate_task_function(task_config)
    
    assert "sensor_task_task" in task_code
    assert "vTaskDelayUntil" in task_code
    assert "100" in task_code or "pdMS_TO_TICKS" in task_code


def test_freertos_task_handle():
    """Test FreeRTOS task handle generation."""
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    task_config = {"name": "led_task"}
    handle = generator.generate_task_handle(task_config)
    
    assert "TaskHandle_t" in handle
    assert "led_task_handle" in handle


def test_freertos_task_creation():
    """Test FreeRTOS task creation code."""
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    task_config = {
        "name": "control_task",
        "priority": "tskIDLE_PRIORITY + 2",
        "stack_size": 512
    }
    
    creation_code = generator.generate_task_creation(task_config)
    
    assert "xTaskCreate" in creation_code
    assert "control_task" in creation_code
    assert "512" in creation_code


def test_freertos_all_tasks_generation():
    """Test generating multiple FreeRTOS tasks."""
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    tasks = [
        {"name": "task1", "priority": "tskIDLE_PRIORITY + 1", "stack_size": 128, "period_ms": 100},
        {"name": "task2", "priority": "tskIDLE_PRIORITY + 2", "stack_size": 256, "period_ms": 500},
    ]
    
    all_tasks_code = generator.generate_all_tasks(tasks)
    
    assert "task1_task" in all_tasks_code
    assert "task2_task" in all_tasks_code
    assert "vTaskStartScheduler" in all_tasks_code
    assert "FreeRTOS.h" in all_tasks_code


def test_freertos_config_generator():
    """Test FreeRTOS configuration generation."""
    from accelerapp.rtos.freertos import FreeRTOSConfigGenerator
    
    generator = FreeRTOSConfigGenerator("stm32")
    
    config = {
        "cpu_clock_hz": 84000000,
        "tick_rate_hz": 1000,
        "max_priorities": 5,
        "use_mutexes": True,
        "use_timers": True
    }
    
    config_code = generator.generate_config(config)
    
    assert "#define configCPU_CLOCK_HZ" in config_code
    assert "84000000" in config_code
    assert "#define configUSE_MUTEXES" in config_code
    assert "FREERTOS_CONFIG_H" in config_code


def test_freertos_config_stm32_specific():
    """Test STM32-specific FreeRTOS configuration."""
    from accelerapp.rtos.freertos import FreeRTOSConfigGenerator
    
    generator = FreeRTOSConfigGenerator("stm32")
    config_code = generator.generate_config({})
    
    # Should include STM32-specific definitions
    assert "configPRIO_BITS" in config_code or "NVIC" in config_code or "Cortex-M" in config_code


def test_freertos_config_nrf_specific():
    """Test nRF-specific FreeRTOS configuration."""
    from accelerapp.rtos.freertos import FreeRTOSConfigGenerator
    
    generator = FreeRTOSConfigGenerator("nrf52")
    config_code = generator.generate_config({})
    
    # Should include nRF-specific definitions
    assert "Nordic" in config_code or "nRF" in config_code or "configPRIO_BITS" in config_code


def test_ipc_queue_generation():
    """Test FreeRTOS queue generation."""
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    queue_config = {
        "name": "sensor_queue",
        "length": 10,
        "item_size": "sizeof(sensor_data_t)"
    }
    
    queue_code = ipc.generate_queue(queue_config)
    
    assert "QueueHandle_t" in queue_code
    assert "sensor_queue" in queue_code
    assert "xQueueCreate" in queue_code
    assert "10" in queue_code


def test_ipc_semaphore_generation():
    """Test FreeRTOS semaphore generation."""
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    # Binary semaphore
    sem_config = {
        "name": "data_ready",
        "type": "binary"
    }
    
    sem_code = ipc.generate_semaphore(sem_config)
    
    assert "SemaphoreHandle_t" in sem_code
    assert "data_ready" in sem_code
    assert "xSemaphoreCreateBinary" in sem_code
    
    # Counting semaphore
    counting_config = {
        "name": "buffer_count",
        "type": "counting",
        "max_count": 5,
        "initial_count": 0
    }
    
    counting_code = ipc.generate_semaphore(counting_config)
    assert "xSemaphoreCreateCounting" in counting_code
    assert "5" in counting_code


def test_ipc_mutex_generation():
    """Test FreeRTOS mutex generation."""
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    mutex_config = {
        "name": "spi_mutex",
        "recursive": False
    }
    
    mutex_code = ipc.generate_mutex(mutex_config)
    
    assert "SemaphoreHandle_t" in mutex_code
    assert "spi_mutex" in mutex_code
    assert "xSemaphoreCreateMutex" in mutex_code
    
    # Recursive mutex
    recursive_config = {
        "name": "recursive_lock",
        "recursive": True
    }
    
    recursive_code = ipc.generate_mutex(recursive_config)
    assert "xSemaphoreCreateRecursiveMutex" in recursive_code


def test_ipc_event_group_generation():
    """Test FreeRTOS event group generation."""
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    event_config = {
        "name": "system_events",
        "bits": {
            "ready": 0,
            "error": 1,
            "complete": 2
        }
    }
    
    event_code = ipc.generate_event_group(event_config)
    
    assert "EventGroupHandle_t" in event_code
    assert "system_events" in event_code
    assert "READY_BIT" in event_code
    assert "ERROR_BIT" in event_code
    assert "xEventGroupCreate" in event_code


def test_ipc_all_generation():
    """Test generating all IPC primitives together."""
    from accelerapp.rtos.freertos import IPCPrimitives
    
    ipc = IPCPrimitives()
    
    ipc_config = {
        "queues": [
            {"name": "data_queue", "length": 5, "item_size": "sizeof(int)"}
        ],
        "semaphores": [
            {"name": "sync_sem", "type": "binary"}
        ],
        "mutexes": [
            {"name": "resource_mutex", "recursive": False}
        ],
        "event_groups": [
            {"name": "flags", "bits": {"flag1": 0, "flag2": 1}}
        ]
    }
    
    all_code = ipc.generate_all_ipc(ipc_config)
    
    assert "data_queue" in all_code
    assert "sync_sem" in all_code
    assert "resource_mutex" in all_code
    assert "flags" in all_code
    assert "ipc_init" in all_code


def test_task_timing_analysis():
    """Test FreeRTOS task timing analysis."""
    from accelerapp.rtos.freertos import FreeRTOSTaskGenerator
    
    generator = FreeRTOSTaskGenerator()
    
    tasks = [
        {
            "name": "fast_task",
            "priority": "tskIDLE_PRIORITY + 3",
            "period_ms": 10,
            "exec_time_ms": 2
        },
        {
            "name": "slow_task",
            "priority": "tskIDLE_PRIORITY + 1",
            "period_ms": 100,
            "exec_time_ms": 10
        }
    ]
    
    analysis = generator.analyze_task_timing(tasks)
    
    assert analysis["total_tasks"] == 2
    assert "utilization" in analysis
    assert "warnings" in analysis
    assert "priorities" in analysis
