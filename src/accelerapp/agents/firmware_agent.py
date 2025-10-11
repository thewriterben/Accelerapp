"""
Firmware Agent specialized in embedded systems development.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_agent import BaseAgent


class FirmwareAgent(BaseAgent):
    """
    Specialized agent for firmware generation and embedded systems.
    Expert in low-level hardware control and real-time systems.
    """
    
    def __init__(self):
        """Initialize firmware agent."""
        capabilities = [
            'firmware_generation',
            'embedded_systems',
            'hardware_control',
            'real_time_systems',
            'interrupt_handling',
            'peripheral_drivers',
            'power_management',
        ]
        super().__init__("Firmware Agent", capabilities)
        
        # Platform-specific expertise
        self.platform_expertise = {
            'arduino': 'expert',
            'esp32': 'expert',
            'stm32': 'advanced',
            'micropython': 'intermediate',
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Check if agent can handle a task.
        
        Args:
            task: Task identifier
            
        Returns:
            True if agent can handle this task
        """
        firmware_keywords = [
            'firmware',
            'embedded',
            'microcontroller',
            'mcu',
            'peripheral',
            'driver',
            'interrupt',
            'real-time',
            'hardware',
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in firmware_keywords)
    
    def generate(self, spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate firmware code.
        
        Args:
            spec: Firmware specification
            
        Returns:
            Generated firmware
        """
        platform = spec.get('platform', 'arduino')
        task_type = spec.get('task_type', 'generate')
        
        if task_type == 'generate':
            return self._generate_firmware(spec)
        elif task_type == 'optimize':
            return self._optimize_firmware(spec)
        elif task_type == 'analyze':
            return self._analyze_firmware(spec)
        else:
            return {
                'status': 'error',
                'message': f'Unknown task type: {task_type}'
            }
    
    def _generate_firmware(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete firmware.
        
        Args:
            spec: Firmware specification
            
        Returns:
            Generated firmware code
        """
        platform = spec.get('platform', 'arduino')
        peripherals = spec.get('peripherals', [])
        
        # Use platform-specific generation
        from ..platforms import get_platform
        
        try:
            platform_impl = get_platform(platform)
            
            # Create temporary output directory
            output_dir = Path('/tmp/firmware_gen')
            result = platform_impl.generate_code(spec, output_dir)
            
            return {
                'status': 'success',
                'platform': platform,
                'result': result,
                'agent': self.name,
            }
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e),
                'agent': self.name,
            }
    
    def _optimize_firmware(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize firmware for performance and size.
        
        Args:
            spec: Firmware specification
            
        Returns:
            Optimization recommendations
        """
        code = spec.get('code', '')
        platform = spec.get('platform', 'arduino')
        
        optimizations = []
        
        # Memory optimization
        if 'String' in code:
            optimizations.append({
                'type': 'memory',
                'suggestion': 'Use char arrays instead of String objects to save RAM',
                'impact': 'high',
                'platform': platform,
            })
        
        # Performance optimization
        if 'float' in code and platform in ['arduino', 'stm32']:
            optimizations.append({
                'type': 'performance',
                'suggestion': 'Consider using fixed-point arithmetic instead of float',
                'impact': 'medium',
                'platform': platform,
            })
        
        # Power optimization
        if 'delay(' in code:
            optimizations.append({
                'type': 'power',
                'suggestion': 'Use sleep modes instead of busy-wait delays',
                'impact': 'high',
                'platform': platform,
            })
        
        # Interrupt handling
        if 'attachInterrupt' not in code and any(p.get('type') == 'button' for p in spec.get('peripherals', [])):
            optimizations.append({
                'type': 'responsiveness',
                'suggestion': 'Consider using interrupts for button handling',
                'impact': 'medium',
                'platform': platform,
            })
        
        return {
            'status': 'success',
            'optimizations': optimizations,
            'count': len(optimizations),
            'agent': self.name,
        }
    
    def _analyze_firmware(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze firmware architecture and constraints.
        
        Args:
            spec: Firmware specification
            
        Returns:
            Analysis results
        """
        platform = spec.get('platform', 'arduino')
        peripherals = spec.get('peripherals', [])
        
        analysis = {
            'platform': platform,
            'expertise_level': self.platform_expertise.get(platform, 'basic'),
            'complexity': 'low',
            'resource_usage': {},
            'constraints': [],
            'recommendations': [],
        }
        
        # Analyze peripheral count
        peripheral_count = len(peripherals)
        if peripheral_count > 5:
            analysis['complexity'] = 'medium'
        if peripheral_count > 10:
            analysis['complexity'] = 'high'
            analysis['recommendations'].append(
                'High peripheral count: consider using peripheral multiplexing'
            )
        
        # Platform-specific analysis
        if platform == 'arduino':
            analysis['constraints'].append('Limited RAM (2KB on Uno)')
            analysis['constraints'].append('8-bit AVR architecture')
            analysis['recommendations'].append('Minimize String usage')
            
        elif platform == 'esp32':
            analysis['constraints'].append('3.3V logic levels')
            analysis['recommendations'].append('Leverage dual-core for parallel tasks')
            analysis['recommendations'].append('Use WiFi/Bluetooth capabilities')
            
        elif platform == 'stm32':
            analysis['constraints'].append('32-bit ARM architecture')
            analysis['recommendations'].append('Use DMA for high-speed peripherals')
            analysis['recommendations'].append('Leverage hardware timers')
        
        # Analyze peripheral types
        peripheral_types = {}
        for peripheral in peripherals:
            ptype = peripheral.get('type', 'unknown')
            peripheral_types[ptype] = peripheral_types.get(ptype, 0) + 1
        
        analysis['resource_usage']['peripherals'] = peripheral_types
        
        # Check for real-time requirements
        if any(p.get('type') in ['motor', 'servo'] for p in peripherals):
            analysis['recommendations'].append(
                'Real-time control detected: ensure consistent timing'
            )
        
        return {
            'status': 'success',
            'analysis': analysis,
            'agent': self.name,
        }
    
    def get_platform_support(self) -> Dict[str, str]:
        """
        Get platform support levels.
        
        Returns:
            Dictionary of platform support levels
        """
        return self.platform_expertise.copy()
    
    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities.
        
        Returns:
            List of capabilities
        """
        return self.capabilities.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.
        
        Returns:
            Agent info dictionary
        """
        return {
            'name': self.name,
            'type': 'firmware_agent',
            'capabilities': self.capabilities,
            'platform_expertise': self.platform_expertise,
            'version': '1.0.0',
            'description': 'Specialized firmware generation agent for embedded systems',
        }
