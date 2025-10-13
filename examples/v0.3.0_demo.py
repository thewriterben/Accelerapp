#!/usr/bin/env python3
"""
Demonstration of Accelerapp v0.3.0 features.
Shows cloud service, marketplace, visual builder, and HIL testing capabilities.
"""

import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from accelerapp.cloud import CloudGenerationService, CloudAPIHandler, AuthenticationManager, JobQueue
from accelerapp.cloud.api import HTTPMethod
from accelerapp.marketplace import TemplateRegistry, TemplateMetadata, TemplatePackage, TemplateSearch
from accelerapp.visual import VisualSpecification, ComponentLibrary, SpecificationExporter
from accelerapp.hil import HILTestFramework, TestCase, TestRunner, DeviceAdapter, SimulatedHardware


def demo_cloud_service():
    """Demonstrate cloud generation service."""
    print("\n" + "=" * 70)
    print("DEMO 1: Cloud Generation Service")
    print("=" * 70)
    
    # Initialize service
    service = CloudGenerationService()
    service.start()
    print("✓ Cloud service started")
    
    # Submit jobs
    spec1 = {'device_name': 'LED Controller', 'platform': 'arduino'}
    job1_id = service.submit_job(spec1, priority='high')
    print(f"✓ Submitted high priority job: {job1_id[:8]}...")
    
    spec2 = {'device_name': 'Sensor Array', 'platform': 'esp32'}
    job2_id = service.submit_job(spec2, priority='normal')
    print(f"✓ Submitted normal priority job: {job2_id[:8]}...")
    
    # Check status
    health = service.get_service_health()
    print(f"\n  Service Health:")
    print(f"    Active: {health['active']}")
    print(f"    Total jobs: {health['total_jobs']}")
    print(f"    Queued: {health['queued_jobs']}")
    
    # API Handler
    api = CloudAPIHandler(service)
    response = api.handle_request('/health', HTTPMethod.GET)
    print(f"\n✓ API health check: {response['status']}")
    
    service.stop()
    print("✓ Service stopped")


def demo_marketplace():
    """Demonstrate template marketplace."""
    print("\n" + "=" * 70)
    print("DEMO 2: Template Marketplace")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize registry
        registry = TemplateRegistry(storage_path=Path(tmpdir))
        print("✓ Template registry initialized")
        
        # Create templates
        templates = [
            TemplateMetadata(
                id='arduino-blink',
                name='Arduino Blink',
                description='Simple LED blink template',
                author='Accelerapp Team',
                version='1.0.0',
                category='embedded',
                tags=['arduino', 'led', 'beginner'],
                platforms=['arduino'],
                rating=4.8,
                downloads=1500
            ),
            TemplateMetadata(
                id='esp32-wifi',
                name='ESP32 WiFi Setup',
                description='WiFi configuration for ESP32',
                author='Accelerapp Team',
                version='2.1.0',
                category='embedded',
                tags=['esp32', 'wifi', 'iot'],
                platforms=['esp32'],
                rating=4.9,
                downloads=2300
            ),
            TemplateMetadata(
                id='stm32-motor',
                name='STM32 Motor Control',
                description='PWM motor control for STM32',
                author='Accelerapp Team',
                version='1.5.0',
                category='embedded',
                tags=['stm32', 'motor', 'pwm'],
                platforms=['stm32'],
                rating=4.7,
                downloads=890
            ),
        ]
        
        for metadata in templates:
            package = TemplatePackage(metadata)
            package.add_file('main.cpp', f'// Template: {metadata.name}')
            package.add_file('README.md', f'# {metadata.name}\n\n{metadata.description}')
            registry.register_template(package)
        
        print(f"✓ Registered {len(templates)} templates")
        
        # Search templates
        search = TemplateSearch(registry.list_templates())
        
        results = search.search(query='wifi')
        print(f"\n  Search 'wifi': {len(results)} result(s)")
        for r in results:
            print(f"    - {r.name} (★{r.rating}, ↓{r.downloads})")
        
        results = search.search(platform='arduino')
        print(f"\n  Platform 'arduino': {len(results)} result(s)")
        
        popular = search.get_popular(limit=2)
        print(f"\n  Most popular templates:")
        for r in popular:
            print(f"    - {r.name}: {r.downloads} downloads")
        
        # Statistics
        stats = registry.get_statistics()
        print(f"\n  Registry Statistics:")
        print(f"    Total templates: {stats['total_templates']}")
        print(f"    Total downloads: {stats['total_downloads']}")
        print(f"    Categories: {list(stats['categories'].keys())}")


def demo_visual_builder():
    """Demonstrate visual specification builder."""
    print("\n" + "=" * 70)
    print("DEMO 3: Visual Specification Builder")
    print("=" * 70)
    
    # Create specification
    spec = VisualSpecification(
        name='LED Control System',
        description='Button controlled LED with visual specification'
    )
    print("✓ Created visual specification")
    
    # Add components
    mcu_id = spec.add_component(
        'microcontroller',
        'Arduino Uno',
        properties={'platform': 'arduino', 'clock_speed': '16MHz'},
        position={'x': 200, 'y': 100}
    )
    
    button_id = spec.add_component(
        'button',
        'Control Button',
        properties={'pin': 2, 'pull_up': True},
        position={'x': 50, 'y': 200}
    )
    
    led_id = spec.add_component(
        'led',
        'Status LED',
        properties={'pin': 13, 'color': 'red'},
        position={'x': 350, 'y': 200}
    )
    
    print(f"✓ Added {len(spec.components)} components")
    
    # Add connections
    conn1 = spec.add_connection(button_id, mcu_id, 'output', 'input')
    conn2 = spec.add_connection(mcu_id, led_id, 'output', 'control')
    print(f"✓ Added {len(spec.connections)} connections")
    
    # Validate
    errors = spec.validate()
    print(f"✓ Validation: {'Passed' if not errors else f'{len(errors)} errors'}")
    
    # Component library
    library = ComponentLibrary()
    categories = library.get_categories()
    print(f"\n  Component Library:")
    print(f"    Total components: {len(library.components)}")
    print(f"    Categories: {', '.join(categories)}")
    
    # Export
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = SpecificationExporter(spec)
        
        # Export to Accelerapp config
        config = exporter.to_accelerapp_config()
        print(f"\n  Exported to Accelerapp config:")
        print(f"    Device: {config['device_name']}")
        print(f"    Platform: {config['platform']}")
        print(f"    Peripherals: {len(config['peripherals'])}")
        
        # Save files
        json_path = Path(tmpdir) / 'spec.json'
        yaml_path = Path(tmpdir) / 'spec.yaml'
        config_path = Path(tmpdir) / 'accelerapp_config.yaml'
        
        exporter.save_json(json_path)
        exporter.save_yaml(yaml_path)
        exporter.save_accelerapp_config(config_path)
        
        print(f"\n  Saved files:")
        print(f"    ✓ {json_path.name}")
        print(f"    ✓ {yaml_path.name}")
        print(f"    ✓ {config_path.name}")


def demo_hil_testing():
    """Demonstrate HIL testing framework."""
    print("\n" + "=" * 70)
    print("DEMO 4: Hardware-in-the-Loop Testing")
    print("=" * 70)
    
    # Create test framework
    framework = HILTestFramework()
    print("✓ HIL test framework initialized")
    
    # Define test cases
    class LEDTest(TestCase):
        def execute(self):
            """Test LED functionality."""
            hardware = SimulatedHardware()
            hardware.connect()
            
            # Test digital write
            hardware.digital_write(13, True)
            state = hardware.digital_read(13)
            self.assert_true(state, "LED should be ON")
            
            hardware.digital_write(13, False)
            state = hardware.digital_read(13)
            self.assert_false(state, "LED should be OFF")
    
    class ButtonTest(TestCase):
        def execute(self):
            """Test button functionality."""
            hardware = SimulatedHardware()
            hardware.connect()
            
            # Simulate button press
            hardware.digital_write(2, True)
            state = hardware.digital_read(2)
            self.assert_true(state, "Button should be pressed")
    
    class SensorTest(TestCase):
        def execute(self):
            """Test analog sensor."""
            hardware = SimulatedHardware()
            hardware.connect()
            
            # Simulate sensor reading
            hardware.analog_write(0, 512)
            value = hardware.analog_read(0)
            self.assert_equal(value, 512, "Sensor should read 512")
    
    # Register tests
    framework.register_test(LEDTest('test_led', 'LED Functionality'))
    framework.register_test(ButtonTest('test_button', 'Button Input'))
    framework.register_test(SensorTest('test_sensor', 'Analog Sensor'))
    print(f"✓ Registered {len(framework.test_cases)} test cases")
    
    # Run tests
    runner = TestRunner(framework)
    report = runner.run_tests(verbose=True)
    
    # Print summary
    summary = report['summary']
    print(f"\n  Test Summary:")
    print(f"    Total: {summary['total']}")
    print(f"    Passed: {summary['passed']} ✓")
    print(f"    Failed: {summary['failed']}")
    print(f"    Errors: {summary['error']}")
    print(f"    Pass Rate: {summary['pass_rate']:.1f}%")
    
    # Save reports
    with tempfile.TemporaryDirectory() as tmpdir:
        json_report = Path(tmpdir) / 'test_report.json'
        html_report = Path(tmpdir) / 'test_report.html'
        
        runner.save_report(json_report, 'json')
        runner.save_report(html_report, 'html')
        
        print(f"\n  Reports saved:")
        print(f"    ✓ {json_report.name}")
        print(f"    ✓ {html_report.name}")


def demo_authentication():
    """Demonstrate authentication system."""
    print("\n" + "=" * 70)
    print("DEMO 5: Authentication & Authorization")
    print("=" * 70)
    
    auth = AuthenticationManager()
    print("✓ Authentication manager initialized")
    
    # Create users
    auth.create_user('developer', 'dev123', roles=['user', 'developer'])
    auth.create_user('admin', 'admin123', roles=['user', 'admin'])
    print("✓ Created 2 users")
    
    # Authenticate
    dev_token = auth.authenticate('developer', 'dev123')
    print(f"✓ Developer authenticated: {dev_token[:16]}...")
    
    # Check permissions
    has_user_perm = auth.check_permission(dev_token, 'user')
    has_admin_perm = auth.check_permission(dev_token, 'admin')
    
    print(f"\n  Developer permissions:")
    print(f"    User access: {'✓' if has_user_perm else '✗'}")
    print(f"    Admin access: {'✓' if has_admin_perm else '✗'}")
    
    # Validate token
    token_info = auth.validate_token(dev_token)
    print(f"\n  Token info:")
    print(f"    Username: {token_info['username']}")
    print(f"    Roles: {', '.join(token_info['roles'])}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Accelerapp v0.3.0 Feature Demo" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        demo_cloud_service()
        demo_marketplace()
        demo_visual_builder()
        demo_hil_testing()
        demo_authentication()
        
        print("\n" + "=" * 70)
        print("All demonstrations completed successfully! 🎉")
        print("=" * 70)
        print("\nVersion 0.3.0 foundation features:")
        print("  ✓ Cloud generation service with REST API")
        print("  ✓ Template marketplace with search")
        print("  ✓ Visual specification builder")
        print("  ✓ Hardware-in-the-loop testing")
        print("  ✓ Authentication & authorization")
        print("\nFor more information:")
        print("  - README: ../README.md")
        print("  - CHANGELOG: ../CHANGELOG.md")
        print("  - Tests: ../tests/test_*.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
