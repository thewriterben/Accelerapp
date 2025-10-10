#!/usr/bin/env python3
"""
Demonstration of Accelerapp Phase 1-2 capabilities.
Shows platform abstraction, hardware abstraction layer, and template system.
"""

import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from accelerapp.platforms import get_platform
from accelerapp.hardware import HardwareAbstractionLayer, ComponentFactory
from accelerapp.templates import TemplateManager
from accelerapp.agents import AIAgent, FirmwareAgent


def demo_platform_abstraction():
    """Demonstrate platform abstraction layer."""
    print("=" * 60)
    print("PLATFORM ABSTRACTION DEMO")
    print("=" * 60)
    
    platforms = ['arduino', 'esp32', 'stm32', 'micropython']
    
    for platform_name in platforms:
        platform = get_platform(platform_name)
        info = platform.get_platform_info()
        
        print(f"\n{info['display_name']}:")
        print(f"  Capabilities: {', '.join(info['capabilities'][:3])}...")
        print(f"  Languages: {', '.join(info['languages'])}")
        print(f"  Build System: {info.get('build_system', 'N/A')}")


def demo_hardware_abstraction():
    """Demonstrate hardware abstraction layer."""
    print("\n" + "=" * 60)
    print("HARDWARE ABSTRACTION LAYER DEMO")
    print("=" * 60)
    
    hal = HardwareAbstractionLayer()
    
    # Add components
    components = [
        ComponentFactory.create_component('led', {'name': 'led1', 'pin': 13}),
        ComponentFactory.create_component('button', {'name': 'btn1', 'pin': 2}),
        ComponentFactory.create_component('sensor', {'name': 'temp', 'pin': 'A0'}),
    ]
    
    for comp in components:
        success = hal.add_component(comp)
        print(f"\nAdded {comp.component_type} '{comp.component_id}': {success}")
    
    # Try to add conflicting component
    conflict = ComponentFactory.create_component('led', {'name': 'led2', 'pin': 13})
    success = hal.add_component(conflict)
    print(f"\nAttempted to add conflicting LED on pin 13: {success}")
    
    # Show statistics
    stats = hal.get_stats()
    print(f"\nHAL Statistics:")
    print(f"  Total components: {stats['total_components']}")
    print(f"  Pins used: {stats['pins_used']}")
    print(f"  Components by type: {stats['components_by_type']}")


def demo_template_system():
    """Demonstrate template system."""
    print("\n" + "=" * 60)
    print("TEMPLATE SYSTEM DEMO")
    print("=" * 60)
    
    manager = TemplateManager()
    
    # Simple string rendering
    template = "Device: {{ name | pascal_case }}"
    result = manager.render_string(template, {'name': 'my_device'})
    print(f"\nTemplate: {template}")
    print(f"Result: {result}")
    
    # Test filters
    filters = [
        ('upper_snake_case', 'my device name', manager.render_string("{{ name | upper_snake_case }}", {'name': 'my device name'})),
        ('camel_case', 'my device name', manager.render_string("{{ name | camel_case }}", {'name': 'my device name'})),
        ('pascal_case', 'my device name', manager.render_string("{{ name | pascal_case }}", {'name': 'my device name'})),
    ]
    
    print("\nFilter demonstrations:")
    for filter_name, input_val, output in filters:
        print(f"  {filter_name}('{input_val}') = '{output}'")


def demo_agents():
    """Demonstrate specialized agents."""
    print("\n" + "=" * 60)
    print("SPECIALIZED AGENTS DEMO")
    print("=" * 60)
    
    # AI Agent
    print("\nAI Agent:")
    ai_agent = AIAgent()
    print(f"  Name: {ai_agent.name}")
    print(f"  Capabilities: {', '.join(ai_agent.capabilities[:3])}...")
    
    # Test code optimization
    spec = {
        'task_type': 'optimize',
        'code': 'delay(1000); Serial.println("test");',
        'platform': 'arduino',
    }
    result = ai_agent.generate(spec)
    if result['status'] == 'success':
        print(f"  Optimization suggestions: {result['count']}")
        if result['count'] > 0:
            print(f"    Example: {result['optimizations'][0]['suggestion']}")
    
    # Firmware Agent
    print("\nFirmware Agent:")
    firmware_agent = FirmwareAgent()
    print(f"  Name: {firmware_agent.name}")
    print(f"  Capabilities: {', '.join(firmware_agent.capabilities[:3])}...")
    
    # Test platform support
    support = firmware_agent.get_platform_support()
    print(f"  Platform expertise:")
    for platform, level in support.items():
        print(f"    {platform}: {level}")


def demo_code_generation():
    """Demonstrate complete code generation."""
    print("\n" + "=" * 60)
    print("CODE GENERATION DEMO")
    print("=" * 60)
    
    spec = {
        'device_name': 'Demo Device',
        'platform': 'arduino',
        'peripherals': [
            {'type': 'led', 'pin': 13, 'description': 'Status LED'},
            {'type': 'sensor', 'pin': 'A0', 'description': 'Temperature sensor'},
        ],
        'pins': {'LED_PIN': 13, 'SENSOR_PIN': 'A0'},
        'timing': {'BAUD_RATE': 9600},
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        # Generate using platform
        platform = get_platform('arduino')
        result = platform.generate_code(spec, output_dir)
        
        print(f"\nGeneration result:")
        print(f"  Status: {result['status']}")
        print(f"  Platform: {result['platform']}")
        print(f"  Files generated: {len(result['files_generated'])}")
        
        # Show generated files
        for file_path in result['files_generated']:
            file = Path(file_path)
            if file.exists():
                print(f"\n  {file.name}:")
                content = file.read_text()
                # Show first few lines
                lines = content.split('\n')[:5]
                for line in lines:
                    print(f"    {line}")
                if len(content.split('\n')) > 5:
                    print(f"    ... ({len(content.split('\n'))} total lines)")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  ACCELERAPP COMPREHENSIVE UPGRADE DEMONSTRATION".center(58) + "║")
    print("║" + "  Phases 1-2 Implementation".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    demo_platform_abstraction()
    demo_hardware_abstraction()
    demo_template_system()
    demo_agents()
    demo_code_generation()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nAll Phase 1-2 capabilities demonstrated successfully!")
    print()


if __name__ == '__main__':
    main()
