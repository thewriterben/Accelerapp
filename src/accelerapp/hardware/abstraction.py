"""
Hardware abstraction layer core implementation.
Provides unified interface for hardware components and conflict detection.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class HardwareComponent:
    """
    Represents a hardware component in the system.
    """
    component_id: str
    component_type: str
    pins: List[int] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    
    def uses_pin(self, pin: int) -> bool:
        """Check if component uses a specific pin."""
        return pin in self.pins
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.component_id,
            'type': self.component_type,
            'pins': self.pins,
            'config': self.config,
            'capabilities': self.capabilities,
        }


class ComponentFactory:
    """
    Factory for creating hardware components.
    """
    
    @staticmethod
    def create_component(component_type: str, config: Dict[str, Any]) -> HardwareComponent:
        """
        Create a hardware component from configuration.
        
        Args:
            component_type: Type of component to create
            config: Component configuration
            
        Returns:
            HardwareComponent instance
        """
        # Extract pins from config
        pins = []
        if 'pin' in config:
            pin_value = config['pin']
            if isinstance(pin_value, int):
                pins = [pin_value]
            elif isinstance(pin_value, list):
                pins = pin_value
        
        # Generate component ID
        component_id = config.get('name', f"{component_type}_{id(config)}")
        
        # Determine capabilities based on type
        capabilities = ComponentFactory._get_capabilities(component_type)
        
        return HardwareComponent(
            component_id=component_id,
            component_type=component_type,
            pins=pins,
            config=config,
            capabilities=capabilities,
        )
    
    @staticmethod
    def _get_capabilities(component_type: str) -> List[str]:
        """Get capabilities for a component type."""
        capability_map = {
            'led': ['digital_output'],
            'button': ['digital_input'],
            'sensor': ['analog_input'],
            'motor': ['pwm_output'],
            'servo': ['pwm_output'],
            'display': ['i2c', 'spi'],
            'camera': ['camera', 'i2c'],
            'wifi_module': ['wifi', 'network'],
            'bluetooth_module': ['bluetooth', 'wireless'],
        }
        return capability_map.get(component_type, [])


class HardwareAbstractionLayer:
    """
    Hardware abstraction layer for managing components and detecting conflicts.
    """
    
    def __init__(self):
        """Initialize HAL."""
        self.components: Dict[str, HardwareComponent] = {}
        self.pin_usage: Dict[int, List[str]] = {}
    
    def add_component(self, component: HardwareComponent) -> bool:
        """
        Add a component to the HAL.
        
        Args:
            component: Component to add
            
        Returns:
            True if added successfully, False if conflicts detected
        """
        # Check for pin conflicts
        conflicts = self.check_pin_conflicts(component)
        if conflicts:
            return False
        
        # Add component
        self.components[component.component_id] = component
        
        # Update pin usage
        for pin in component.pins:
            if pin not in self.pin_usage:
                self.pin_usage[pin] = []
            self.pin_usage[pin].append(component.component_id)
        
        return True
    
    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component from the HAL.
        
        Args:
            component_id: ID of component to remove
            
        Returns:
            True if removed, False if not found
        """
        if component_id not in self.components:
            return False
        
        component = self.components[component_id]
        
        # Remove from pin usage
        for pin in component.pins:
            if pin in self.pin_usage:
                self.pin_usage[pin].remove(component_id)
                if not self.pin_usage[pin]:
                    del self.pin_usage[pin]
        
        # Remove component
        del self.components[component_id]
        return True
    
    def check_pin_conflicts(self, component: HardwareComponent) -> List[str]:
        """
        Check for pin conflicts with existing components.
        
        Args:
            component: Component to check
            
        Returns:
            List of conflict descriptions (empty if no conflicts)
        """
        conflicts = []
        
        for pin in component.pins:
            if pin in self.pin_usage:
                for existing_id in self.pin_usage[pin]:
                    existing = self.components[existing_id]
                    conflicts.append(
                        f"Pin {pin} conflict: {component.component_id} vs {existing.component_id}"
                    )
        
        return conflicts
    
    def get_component(self, component_id: str) -> Optional[HardwareComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component or None if not found
        """
        return self.components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> List[HardwareComponent]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List of matching components
        """
        return [
            comp for comp in self.components.values()
            if comp.component_type == component_type
        ]
    
    def get_used_pins(self) -> Set[int]:
        """
        Get set of all used pins.
        
        Returns:
            Set of pin numbers
        """
        return set(self.pin_usage.keys())
    
    def get_available_pins(self, all_pins: List[int]) -> List[int]:
        """
        Get list of available (unused) pins.
        
        Args:
            all_pins: List of all possible pins
            
        Returns:
            List of unused pins
        """
        used = self.get_used_pins()
        return [pin for pin in all_pins if pin not in used]
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the entire hardware configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for components without pins
        for comp in self.components.values():
            if not comp.pins and comp.component_type not in ['wifi_module', 'bluetooth_module']:
                errors.append(f"Component {comp.component_id} has no pins assigned")
        
        # Check for duplicate component IDs (shouldn't happen but validate)
        component_ids = [comp.component_id for comp in self.components.values()]
        duplicates = [cid for cid in component_ids if component_ids.count(cid) > 1]
        if duplicates:
            errors.append(f"Duplicate component IDs: {duplicates}")
        
        return errors
    
    def generate_component_code(self, platform: str) -> str:
        """
        Generate platform-specific code for all components.
        
        Args:
            platform: Target platform name
            
        Returns:
            Generated code string
        """
        lines = [
            f"// Component initialization for {platform}",
            "",
        ]
        
        for component in self.components.values():
            lines.append(f"// Initialize {component.component_id} ({component.component_type})")
            for pin in component.pins:
                lines.append(f"//   Pin: {pin}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the hardware configuration.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_components': len(self.components),
            'pins_used': len(self.pin_usage),
            'component_types': len(set(c.component_type for c in self.components.values())),
            'components_by_type': {
                ctype: len(self.get_components_by_type(ctype))
                for ctype in set(c.component_type for c in self.components.values())
            },
        }
