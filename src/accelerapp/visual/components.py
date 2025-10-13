"""
Component library for visual specification builder.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ComponentDefinition:
    """
    Defines a component type available in the library.
    """
    type: str
    name: str
    description: str
    category: str
    properties: Dict[str, Any] = field(default_factory=dict)
    ports: List[Dict[str, str]] = field(default_factory=list)
    icon: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'properties': self.properties,
            'ports': self.ports,
            'icon': self.icon,
        }


class ComponentLibrary:
    """
    Library of available components for the visual builder.
    """
    
    def __init__(self):
        """Initialize component library with default components."""
        self.components: Dict[str, ComponentDefinition] = {}
        self._load_default_components()
    
    def _load_default_components(self):
        """Load default hardware and software components."""
        
        # Hardware components
        self.add_component(ComponentDefinition(
            type='led',
            name='LED',
            description='Light Emitting Diode',
            category='output',
            properties={
                'pin': {'type': 'integer', 'required': True},
                'color': {'type': 'string', 'default': 'red'},
                'active_high': {'type': 'boolean', 'default': True},
            },
            ports=[
                {'name': 'control', 'direction': 'input', 'type': 'digital'},
            ],
            icon='💡'
        ))
        
        self.add_component(ComponentDefinition(
            type='button',
            name='Button',
            description='Push button input',
            category='input',
            properties={
                'pin': {'type': 'integer', 'required': True},
                'pull_up': {'type': 'boolean', 'default': True},
            },
            ports=[
                {'name': 'output', 'direction': 'output', 'type': 'digital'},
            ],
            icon='🔘'
        ))
        
        self.add_component(ComponentDefinition(
            type='sensor',
            name='Analog Sensor',
            description='Generic analog sensor',
            category='input',
            properties={
                'pin': {'type': 'string', 'required': True},
                'sensor_type': {'type': 'string', 'default': 'temperature'},
                'min_value': {'type': 'float', 'default': 0.0},
                'max_value': {'type': 'float', 'default': 100.0},
            },
            ports=[
                {'name': 'output', 'direction': 'output', 'type': 'analog'},
            ],
            icon='🌡️'
        ))
        
        self.add_component(ComponentDefinition(
            type='motor',
            name='Motor',
            description='DC motor',
            category='output',
            properties={
                'pin_enable': {'type': 'integer', 'required': True},
                'pin_direction': {'type': 'integer', 'required': True},
            },
            ports=[
                {'name': 'speed', 'direction': 'input', 'type': 'pwm'},
                {'name': 'direction', 'direction': 'input', 'type': 'digital'},
            ],
            icon='⚙️'
        ))
        
        # Communication components
        self.add_component(ComponentDefinition(
            type='serial',
            name='Serial Port',
            description='UART serial communication',
            category='communication',
            properties={
                'baud_rate': {'type': 'integer', 'default': 9600},
                'tx_pin': {'type': 'integer'},
                'rx_pin': {'type': 'integer'},
            },
            ports=[
                {'name': 'tx', 'direction': 'output', 'type': 'serial'},
                {'name': 'rx', 'direction': 'input', 'type': 'serial'},
            ],
            icon='📡'
        ))
        
        self.add_component(ComponentDefinition(
            type='wifi',
            name='WiFi Module',
            description='WiFi connectivity',
            category='communication',
            properties={
                'ssid': {'type': 'string'},
                'password': {'type': 'string'},
            },
            ports=[
                {'name': 'data', 'direction': 'bidirectional', 'type': 'network'},
            ],
            icon='📶'
        ))
        
        # Controller components
        self.add_component(ComponentDefinition(
            type='microcontroller',
            name='Microcontroller',
            description='Main microcontroller unit',
            category='controller',
            properties={
                'platform': {'type': 'string', 'required': True},
                'clock_speed': {'type': 'string', 'default': '16MHz'},
            },
            ports=[],
            icon='🖥️'
        ))
    
    def add_component(self, component: ComponentDefinition) -> bool:
        """
        Add a component definition to the library.
        
        Args:
            component: Component definition
            
        Returns:
            True if added successfully
        """
        if component.type in self.components:
            return False
        
        self.components[component.type] = component
        return True
    
    def get_component(self, component_type: str) -> Optional[ComponentDefinition]:
        """
        Get a component definition.
        
        Args:
            component_type: Component type
            
        Returns:
            ComponentDefinition or None
        """
        return self.components.get(component_type)
    
    def list_components(
        self,
        category: Optional[str] = None
    ) -> List[ComponentDefinition]:
        """
        List all components, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of component definitions
        """
        components = list(self.components.values())
        
        if category:
            components = [c for c in components if c.category == category]
        
        return components
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of category names
        """
        categories = set(c.category for c in self.components.values())
        return sorted(categories)
    
    def search_components(self, query: str) -> List[ComponentDefinition]:
        """
        Search components by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching components
        """
        query_lower = query.lower()
        return [
            c for c in self.components.values()
            if query_lower in c.name.lower() or
               query_lower in c.description.lower() or
               query_lower in c.type.lower()
        ]
