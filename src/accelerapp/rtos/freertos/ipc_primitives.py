"""
FreeRTOS IPC (Inter-Process Communication) primitives.
Generates code for queues, semaphores, mutexes, and event groups.
"""

from typing import Dict, Any, List


class IPCPrimitives:
    """
    Generator for FreeRTOS IPC primitives.
    Creates queues, semaphores, mutexes, and event groups.
    """

    def __init__(self):
        """Initialize IPC primitives generator."""
        pass
        
    def generate_queue(self, queue_config: Dict[str, Any]) -> str:
        """
        Generate queue creation and usage code.
        
        Args:
            queue_config: Queue configuration
            
        Returns:
            Generated C code
        """
        queue_name = queue_config.get("name", "queue")
        length = queue_config.get("length", 10)
        item_size = queue_config.get("item_size", "sizeof(uint32_t)")
        
        lines = [
            f"/* Queue: {queue_name} */",
            f"static QueueHandle_t {queue_name}_handle = NULL;",
            "",
            f"void {queue_name}_create(void) {{",
            f"    {queue_name}_handle = xQueueCreate({length}, {item_size});",
            f"    configASSERT({queue_name}_handle != NULL);",
            "}",
            "",
            f"BaseType_t {queue_name}_send(void *item, TickType_t timeout) {{",
            f"    return xQueueSend({queue_name}_handle, item, timeout);",
            "}",
            "",
            f"BaseType_t {queue_name}_receive(void *item, TickType_t timeout) {{",
            f"    return xQueueReceive({queue_name}_handle, item, timeout);",
            "}",
            "",
        ]
        
        return "\n".join(lines)
    
    def generate_semaphore(self, sem_config: Dict[str, Any]) -> str:
        """
        Generate semaphore creation and usage code.
        
        Args:
            sem_config: Semaphore configuration
            
        Returns:
            Generated C code
        """
        sem_name = sem_config.get("name", "semaphore")
        sem_type = sem_config.get("type", "binary")  # binary or counting
        max_count = sem_config.get("max_count", 1)
        initial_count = sem_config.get("initial_count", 0)
        
        lines = [
            f"/* Semaphore: {sem_name} */",
            f"static SemaphoreHandle_t {sem_name}_handle = NULL;",
            "",
            f"void {sem_name}_create(void) {{",
        ]
        
        if sem_type == "binary":
            lines.append(f"    {sem_name}_handle = xSemaphoreCreateBinary();")
        else:  # counting
            lines.append(f"    {sem_name}_handle = xSemaphoreCreateCounting({max_count}, {initial_count});")
        
        lines.extend([
            f"    configASSERT({sem_name}_handle != NULL);",
            "}",
            "",
            f"BaseType_t {sem_name}_take(TickType_t timeout) {{",
            f"    return xSemaphoreTake({sem_name}_handle, timeout);",
            "}",
            "",
            f"BaseType_t {sem_name}_give(void) {{",
            f"    return xSemaphoreGive({sem_name}_handle);",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_mutex(self, mutex_config: Dict[str, Any]) -> str:
        """
        Generate mutex creation and usage code.
        
        Args:
            mutex_config: Mutex configuration
            
        Returns:
            Generated C code
        """
        mutex_name = mutex_config.get("name", "mutex")
        recursive = mutex_config.get("recursive", False)
        
        lines = [
            f"/* Mutex: {mutex_name} */",
            f"static SemaphoreHandle_t {mutex_name}_handle = NULL;",
            "",
            f"void {mutex_name}_create(void) {{",
        ]
        
        if recursive:
            lines.append(f"    {mutex_name}_handle = xSemaphoreCreateRecursiveMutex();")
        else:
            lines.append(f"    {mutex_name}_handle = xSemaphoreCreateMutex();")
        
        lines.extend([
            f"    configASSERT({mutex_name}_handle != NULL);",
            "}",
            "",
            f"BaseType_t {mutex_name}_lock(TickType_t timeout) {{",
        ])
        
        if recursive:
            lines.append(f"    return xSemaphoreTakeRecursive({mutex_name}_handle, timeout);")
        else:
            lines.append(f"    return xSemaphoreTake({mutex_name}_handle, timeout);")
        
        lines.extend([
            "}",
            "",
            f"BaseType_t {mutex_name}_unlock(void) {{",
        ])
        
        if recursive:
            lines.append(f"    return xSemaphoreGiveRecursive({mutex_name}_handle);")
        else:
            lines.append(f"    return xSemaphoreGive({mutex_name}_handle);")
        
        lines.extend([
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_event_group(self, event_config: Dict[str, Any]) -> str:
        """
        Generate event group creation and usage code.
        
        Args:
            event_config: Event group configuration
            
        Returns:
            Generated C code
        """
        event_name = event_config.get("name", "events")
        event_bits = event_config.get("bits", {})
        
        lines = [
            f"/* Event Group: {event_name} */",
            f"static EventGroupHandle_t {event_name}_handle = NULL;",
            "",
        ]
        
        # Define event bits
        for i, (bit_name, bit_num) in enumerate(event_bits.items()):
            lines.append(f"#define {bit_name.upper()}_BIT (1 << {bit_num})")
        lines.append("")
        
        lines.extend([
            f"void {event_name}_create(void) {{",
            f"    {event_name}_handle = xEventGroupCreate();",
            f"    configASSERT({event_name}_handle != NULL);",
            "}",
            "",
            f"EventBits_t {event_name}_set_bits(EventBits_t bits) {{",
            f"    return xEventGroupSetBits({event_name}_handle, bits);",
            "}",
            "",
            f"EventBits_t {event_name}_wait_bits(",
            "    EventBits_t bits,",
            "    BaseType_t clear_on_exit,",
            "    BaseType_t wait_for_all,",
            "    TickType_t timeout) {",
            f"    return xEventGroupWaitBits({event_name}_handle, bits, clear_on_exit, wait_for_all, timeout);",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_all_ipc(self, ipc_config: Dict[str, Any]) -> str:
        """
        Generate all IPC primitives.
        
        Args:
            ipc_config: Complete IPC configuration
            
        Returns:
            Complete IPC code
        """
        lines = [
            "/* FreeRTOS IPC Primitives */",
            '#include "FreeRTOS.h"',
            '#include "task.h"',
            '#include "queue.h"',
            '#include "semphr.h"',
            '#include "event_groups.h"',
            "",
        ]
        
        # Generate queues
        for queue in ipc_config.get("queues", []):
            lines.append(self.generate_queue(queue))
        
        # Generate semaphores
        for semaphore in ipc_config.get("semaphores", []):
            lines.append(self.generate_semaphore(semaphore))
        
        # Generate mutexes
        for mutex in ipc_config.get("mutexes", []):
            lines.append(self.generate_mutex(mutex))
        
        # Generate event groups
        for event_group in ipc_config.get("event_groups", []):
            lines.append(self.generate_event_group(event_group))
        
        # Generate initialization function
        lines.extend([
            "/* Initialize all IPC primitives */",
            "void ipc_init(void) {",
        ])
        
        for queue in ipc_config.get("queues", []):
            lines.append(f"    {queue['name']}_create();")
        
        for semaphore in ipc_config.get("semaphores", []):
            lines.append(f"    {semaphore['name']}_create();")
        
        for mutex in ipc_config.get("mutexes", []):
            lines.append(f"    {mutex['name']}_create();")
        
        for event_group in ipc_config.get("event_groups", []):
            lines.append(f"    {event_group['name']}_create();")
        
        lines.extend([
            "}",
            "",
        ])
        
        return "\n".join(lines)
