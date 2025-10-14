"""
FreeRTOS task generator.
Generates task functions, initialization, and scheduling code.
"""

from typing import Dict, Any, List


class FreeRTOSTaskGenerator:
    """
    Generator for FreeRTOS tasks and scheduling configuration.
    Creates task functions, handles, and initialization code.
    """

    def __init__(self):
        """Initialize FreeRTOS task generator."""
        self.tasks = []
        
    def generate_task_function(self, task_config: Dict[str, Any]) -> str:
        """
        Generate FreeRTOS task function.
        
        Args:
            task_config: Task configuration dictionary
            
        Returns:
            Generated C code for task function
        """
        task_name = task_config.get("name", "task")
        priority = task_config.get("priority", "tskIDLE_PRIORITY")
        stack_size = task_config.get("stack_size", 128)
        period_ms = task_config.get("period_ms", 1000)
        
        lines = [
            f"/* Task: {task_name} */",
            f"void {task_name}_task(void *pvParameters) {{",
            "    TickType_t xLastWakeTime;",
            f"    const TickType_t xFrequency = pdMS_TO_TICKS({period_ms});",
            "",
            "    /* Initialize the xLastWakeTime variable with the current time */",
            "    xLastWakeTime = xTaskGetTickCount();",
            "",
            "    while (1) {",
            f"        /* Task {task_name} logic */",
        ]
        
        # Add task-specific logic
        task_type = task_config.get("type", "periodic")
        if task_type == "sensor_read":
            lines.extend([
                "        /* Read sensor data */",
                "        sensor_read();",
            ])
        elif task_type == "actuator_control":
            lines.extend([
                "        /* Control actuator */",
                "        actuator_update();",
            ])
        elif task_type == "communication":
            lines.extend([
                "        /* Handle communication */",
                "        communication_process();",
            ])
        else:
            lines.append(f"        /* Custom {task_name} processing */")
        
        lines.extend([
            "",
            "        /* Wait for the next cycle */",
            "        vTaskDelayUntil(&xLastWakeTime, xFrequency);",
            "    }",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_task_handle(self, task_config: Dict[str, Any]) -> str:
        """
        Generate task handle declaration.
        
        Args:
            task_config: Task configuration
            
        Returns:
            Task handle declaration code
        """
        task_name = task_config.get("name", "task")
        return f"static TaskHandle_t {task_name}_handle = NULL;"
    
    def generate_task_creation(self, task_config: Dict[str, Any]) -> str:
        """
        Generate task creation code.
        
        Args:
            task_config: Task configuration
            
        Returns:
            Task creation code
        """
        task_name = task_config.get("name", "task")
        priority = task_config.get("priority", "tskIDLE_PRIORITY")
        stack_size = task_config.get("stack_size", 128)
        
        lines = [
            f"    /* Create {task_name} task */",
            f"    xTaskCreate(",
            f"        {task_name}_task,",
            f'        "{task_name}",',
            f"        {stack_size},",
            "        NULL,",
            f"        {priority},",
            f"        &{task_name}_handle",
            "    );",
            "",
        ]
        
        return "\n".join(lines)
    
    def generate_all_tasks(self, tasks_config: List[Dict[str, Any]]) -> str:
        """
        Generate all task functions and initialization.
        
        Args:
            tasks_config: List of task configurations
            
        Returns:
            Complete task generation code
        """
        lines = [
            "/* FreeRTOS Tasks */",
            '#include "FreeRTOS.h"',
            '#include "task.h"',
            "",
        ]
        
        # Generate task handles
        for task in tasks_config:
            lines.append(self.generate_task_handle(task))
        lines.append("")
        
        # Generate task functions
        for task in tasks_config:
            lines.append(self.generate_task_function(task))
        
        # Generate task initialization function
        lines.extend([
            "/* Initialize all tasks */",
            "void tasks_init(void) {",
        ])
        
        for task in tasks_config:
            lines.append(self.generate_task_creation(task))
        
        lines.extend([
            "    /* Start the scheduler */",
            "    vTaskStartScheduler();",
            "",
            "    /* Should never reach here */",
            "    while (1) {}",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_task_priorities(self, tasks_config: List[Dict[str, Any]]) -> str:
        """
        Generate task priority definitions.
        
        Args:
            tasks_config: List of task configurations
            
        Returns:
            Task priority definitions
        """
        lines = [
            "/* Task Priority Definitions */",
            "#define TASK_PRIORITY_IDLE     (tskIDLE_PRIORITY + 0)",
            "#define TASK_PRIORITY_LOW      (tskIDLE_PRIORITY + 1)",
            "#define TASK_PRIORITY_NORMAL   (tskIDLE_PRIORITY + 2)",
            "#define TASK_PRIORITY_HIGH     (tskIDLE_PRIORITY + 3)",
            "#define TASK_PRIORITY_CRITICAL (tskIDLE_PRIORITY + 4)",
            "",
        ]
        
        return "\n".join(lines)
    
    def analyze_task_timing(self, tasks_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze task timing and scheduling feasibility.
        
        Args:
            tasks_config: List of task configurations
            
        Returns:
            Timing analysis results
        """
        analysis = {
            "total_tasks": len(tasks_config),
            "priorities": {},
            "utilization": 0.0,
            "warnings": [],
        }
        
        # Analyze priorities
        for task in tasks_config:
            priority = task.get("priority", "tskIDLE_PRIORITY")
            analysis["priorities"][priority] = analysis["priorities"].get(priority, 0) + 1
        
        # Check for priority conflicts
        if len(analysis["priorities"]) < len(tasks_config):
            analysis["warnings"].append("Multiple tasks share the same priority")
        
        # Calculate CPU utilization (simplified)
        for task in tasks_config:
            period_ms = task.get("period_ms", 1000)
            exec_time_ms = task.get("exec_time_ms", 10)
            analysis["utilization"] += (exec_time_ms / period_ms) * 100
        
        if analysis["utilization"] > 80:
            analysis["warnings"].append(f"High CPU utilization: {analysis['utilization']:.1f}%")
        
        return analysis
