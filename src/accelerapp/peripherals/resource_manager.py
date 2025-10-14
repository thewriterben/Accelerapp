"""
Peripheral resource manager.
Manages peripheral instances, DMA channels, timers, and other shared resources.
"""

from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class ResourceType(Enum):
    """Types of peripheral resources."""
    PIN = "pin"
    DMA_CHANNEL = "dma_channel"
    TIMER = "timer"
    UART_INSTANCE = "uart_instance"
    I2C_INSTANCE = "i2c_instance"
    SPI_INSTANCE = "spi_instance"
    ADC_CHANNEL = "adc_channel"
    PWM_CHANNEL = "pwm_channel"
    INTERRUPT = "interrupt"


@dataclass
class ResourceAllocation:
    """Represents an allocated resource."""
    resource_type: ResourceType
    resource_id: Any  # Could be int, str, tuple, etc.
    peripheral_id: str
    peripheral_type: str
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PeripheralResourceManager:
    """
    Manages allocation of shared peripheral resources.
    Ensures efficient utilization and prevents conflicts.
    """

    def __init__(self, platform: str = "stm32"):
        """
        Initialize resource manager.
        
        Args:
            platform: Target platform for platform-specific resource limits
        """
        self.platform = platform
        self.allocations: Dict[ResourceType, List[ResourceAllocation]] = {
            res_type: [] for res_type in ResourceType
        }
        self.resource_limits = self._get_platform_limits()
        
    def _get_platform_limits(self) -> Dict[ResourceType, int]:
        """Get platform-specific resource limits."""
        if self.platform in ["stm32f4", "stm32"]:
            return {
                ResourceType.DMA_CHANNEL: 16,  # DMA1: 8 channels, DMA2: 8 channels
                ResourceType.TIMER: 14,  # TIM1-TIM14
                ResourceType.UART_INSTANCE: 6,  # USART1-6
                ResourceType.I2C_INSTANCE: 3,  # I2C1-3
                ResourceType.SPI_INSTANCE: 4,  # SPI1-4
                ResourceType.ADC_CHANNEL: 16,  # Per ADC
                ResourceType.PWM_CHANNEL: 56,  # Multiple timers with multiple channels
            }
        elif self.platform == "stm32h7":
            return {
                ResourceType.DMA_CHANNEL: 32,  # DMA1/2: 16 channels each
                ResourceType.TIMER: 17,
                ResourceType.UART_INSTANCE: 8,
                ResourceType.I2C_INSTANCE: 4,
                ResourceType.SPI_INSTANCE: 6,
                ResourceType.ADC_CHANNEL: 20,
                ResourceType.PWM_CHANNEL: 68,
            }
        elif self.platform in ["nrf52", "nrf53"]:
            return {
                ResourceType.DMA_CHANNEL: 8,  # EasyDMA
                ResourceType.TIMER: 5,
                ResourceType.UART_INSTANCE: 2,
                ResourceType.I2C_INSTANCE: 2,
                ResourceType.SPI_INSTANCE: 3,
                ResourceType.ADC_CHANNEL: 8,
                ResourceType.PWM_CHANNEL: 16,
            }
        else:
            # Generic defaults
            return {
                ResourceType.DMA_CHANNEL: 8,
                ResourceType.TIMER: 4,
                ResourceType.UART_INSTANCE: 2,
                ResourceType.I2C_INSTANCE: 2,
                ResourceType.SPI_INSTANCE: 2,
                ResourceType.ADC_CHANNEL: 8,
                ResourceType.PWM_CHANNEL: 16,
            }
    
    def allocate_resource(
        self,
        resource_type: ResourceType,
        peripheral_id: str,
        peripheral_type: str,
        resource_id: Optional[Any] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ResourceAllocation]:
        """
        Allocate a resource to a peripheral.
        
        Args:
            resource_type: Type of resource to allocate
            peripheral_id: ID of the peripheral requesting the resource
            peripheral_type: Type of peripheral
            resource_id: Specific resource ID (auto-allocated if None)
            priority: Allocation priority (higher = more important)
            metadata: Additional metadata about the allocation
            
        Returns:
            ResourceAllocation if successful, None if failed
        """
        # Check if specific resource is requested
        if resource_id is not None:
            if self._is_resource_available(resource_type, resource_id):
                allocation = ResourceAllocation(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    peripheral_id=peripheral_id,
                    peripheral_type=peripheral_type,
                    priority=priority,
                    metadata=metadata or {}
                )
                self.allocations[resource_type].append(allocation)
                return allocation
            else:
                return None
        
        # Auto-allocate next available resource
        next_id = self._find_next_available(resource_type)
        if next_id is not None:
            allocation = ResourceAllocation(
                resource_type=resource_type,
                resource_id=next_id,
                peripheral_id=peripheral_id,
                peripheral_type=peripheral_type,
                priority=priority,
                metadata=metadata or {}
            )
            self.allocations[resource_type].append(allocation)
            return allocation
        
        return None
    
    def _is_resource_available(self, resource_type: ResourceType, resource_id: Any) -> bool:
        """Check if a specific resource is available."""
        for allocation in self.allocations[resource_type]:
            if allocation.resource_id == resource_id:
                return False
        return True
    
    def _find_next_available(self, resource_type: ResourceType) -> Optional[Any]:
        """Find the next available resource ID of a given type."""
        limit = self.resource_limits.get(resource_type, 0)
        if limit == 0:
            return None
        
        # Get currently allocated IDs
        allocated_ids = {alloc.resource_id for alloc in self.allocations[resource_type]}
        
        # Find first available ID
        for i in range(limit):
            if i not in allocated_ids:
                return i
        
        return None
    
    def free_resource(self, resource_type: ResourceType, resource_id: Any) -> bool:
        """
        Free an allocated resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of resource to free
            
        Returns:
            True if freed, False if not found
        """
        allocations = self.allocations[resource_type]
        for i, alloc in enumerate(allocations):
            if alloc.resource_id == resource_id:
                allocations.pop(i)
                return True
        return False
    
    def get_allocation(self, resource_type: ResourceType, resource_id: Any) -> Optional[ResourceAllocation]:
        """Get allocation details for a specific resource."""
        for alloc in self.allocations[resource_type]:
            if alloc.resource_id == resource_id:
                return alloc
        return None
    
    def get_peripheral_resources(self, peripheral_id: str) -> List[ResourceAllocation]:
        """Get all resources allocated to a specific peripheral."""
        resources = []
        for allocations in self.allocations.values():
            for alloc in allocations:
                if alloc.peripheral_id == peripheral_id:
                    resources.append(alloc)
        return resources
    
    def get_utilization(self) -> Dict[str, Any]:
        """
        Get resource utilization statistics.
        
        Returns:
            Dictionary with utilization percentages and details
        """
        utilization = {}
        
        for resource_type in ResourceType:
            allocated_count = len(self.allocations[resource_type])
            limit = self.resource_limits.get(resource_type, 0)
            
            if limit > 0:
                percentage = (allocated_count / limit) * 100
            else:
                percentage = 0
            
            utilization[resource_type.value] = {
                "allocated": allocated_count,
                "limit": limit,
                "available": limit - allocated_count,
                "utilization_percent": percentage
            }
        
        return utilization
    
    def suggest_dma_allocation(self, peripheral_type: str, data_rate: int) -> Optional[Dict[str, Any]]:
        """
        Suggest optimal DMA channel allocation for a peripheral.
        
        Args:
            peripheral_type: Type of peripheral (uart, spi, adc, etc.)
            data_rate: Expected data rate in bytes/second
            
        Returns:
            DMA allocation suggestion
        """
        # Determine priority based on data rate
        if data_rate > 1000000:  # > 1MB/s
            priority = 3
        elif data_rate > 100000:  # > 100KB/s
            priority = 2
        else:
            priority = 1
        
        # Check available DMA channels
        available = self._find_next_available(ResourceType.DMA_CHANNEL)
        
        if available is not None:
            return {
                "dma_channel": available,
                "priority": priority,
                "recommendation": "DMA recommended for high throughput" if data_rate > 100000 else "DMA optional",
                "estimated_cpu_savings": min(80, (data_rate / 10000) * 10)  # Simplified calculation
            }
        else:
            return {
                "dma_channel": None,
                "priority": priority,
                "recommendation": "No DMA channels available - use polling or interrupts",
                "estimated_cpu_savings": 0
            }
    
    def optimize_timer_allocation(self, pwm_channels_needed: int) -> Dict[str, Any]:
        """
        Optimize timer allocation for PWM channels.
        
        Args:
            pwm_channels_needed: Number of PWM channels required
            
        Returns:
            Optimization suggestions
        """
        suggestions = {
            "timers_needed": 0,
            "allocations": [],
            "notes": []
        }
        
        # Most timers have 4 channels
        channels_per_timer = 4
        timers_needed = (pwm_channels_needed + channels_per_timer - 1) // channels_per_timer
        
        suggestions["timers_needed"] = timers_needed
        
        # Find available timers
        for i in range(timers_needed):
            timer_id = self._find_next_available(ResourceType.TIMER)
            if timer_id is not None:
                suggestions["allocations"].append({
                    "timer": timer_id,
                    "channels": min(channels_per_timer, pwm_channels_needed - i * channels_per_timer)
                })
            else:
                suggestions["notes"].append(f"Insufficient timers available. Need {timers_needed}, only {i} available")
                break
        
        return suggestions
    
    def generate_resource_report(self) -> str:
        """
        Generate a human-readable resource allocation report.
        
        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "PERIPHERAL RESOURCE ALLOCATION REPORT",
            f"Platform: {self.platform}",
            "=" * 60,
            ""
        ]
        
        utilization = self.get_utilization()
        
        for resource_type, stats in utilization.items():
            lines.extend([
                f"{resource_type.upper()}:",
                f"  Allocated: {stats['allocated']}/{stats['limit']}",
                f"  Available: {stats['available']}",
                f"  Utilization: {stats['utilization_percent']:.1f}%",
                ""
            ])
        
        lines.extend([
            "DETAILED ALLOCATIONS:",
            "-" * 60,
        ])
        
        for resource_type in ResourceType:
            allocations = self.allocations[resource_type]
            if allocations:
                lines.append(f"\n{resource_type.value.upper()}:")
                for alloc in allocations:
                    lines.append(f"  [{alloc.resource_id}] -> {alloc.peripheral_id} ({alloc.peripheral_type})")
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
