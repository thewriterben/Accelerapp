"""
Command-line interface for Accelerapp.
"""

import click
from pathlib import Path
from .core import AccelerappCore


@click.group()
@click.version_option(version='0.1.0')
def main():
    """
    Accelerapp - Next Generation Hardware Control Platform
    
    Generate firmware, software, and UI from hardware specifications.
    """
    pass


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='./generated_output', 
              help='Output directory for generated code')
@click.option('--firmware-only', is_flag=True, help='Generate only firmware')
@click.option('--software-only', is_flag=True, help='Generate only software')
@click.option('--ui-only', is_flag=True, help='Generate only UI')
def generate(config_file, output, firmware_only, software_only, ui_only):
    """
    Generate code from a hardware specification file.
    
    CONFIG_FILE: Path to YAML configuration file with hardware specs
    """
    click.echo(f"Loading configuration from: {config_file}")
    
    # Initialize core
    core = AccelerappCore(Path(config_file))
    output_dir = Path(output)
    
    # Determine what to generate
    if not (firmware_only or software_only or ui_only):
        # Generate everything
        click.echo("Generating complete stack: firmware, software, and UI...")
        results = core.generate_all(output_dir)
        
        click.echo("\n✓ Generation complete!")
        for component, result in results.items():
            if result['status'] == 'success':
                click.echo(f"  {component}: {result['output_dir']}")
            else:
                click.echo(f"  {component}: ERROR - {result.get('error', 'Unknown error')}")
    else:
        # Generate specific components
        if firmware_only:
            click.echo("Generating firmware...")
            result = core.generate_firmware(output_dir / 'firmware')
            if result['status'] == 'success':
                click.echo(f"✓ Firmware generated: {result['output_dir']}")
            else:
                click.echo(f"✗ Error: {result.get('error')}")
        
        if software_only:
            click.echo("Generating software...")
            result = core.generate_software(output_dir / 'software')
            if result['status'] == 'success':
                click.echo(f"✓ Software generated: {result['output_dir']}")
            else:
                click.echo(f"✗ Error: {result.get('error')}")
        
        if ui_only:
            click.echo("Generating UI...")
            result = core.generate_ui(output_dir / 'ui')
            if result['status'] == 'success':
                click.echo(f"✓ UI generated: {result['output_dir']}")
            else:
                click.echo(f"✗ Error: {result.get('error')}")


@main.command()
@click.argument('output_file', type=click.Path())
def init(output_file):
    """
    Create a sample configuration file.
    
    OUTPUT_FILE: Path where the sample config will be created
    """
    sample_config = """# Accelerapp Hardware Configuration
device_name: "My Custom Device"
platform: "arduino"  # Options: arduino, stm32, esp32
software_language: "python"  # Options: python, cpp, javascript
ui_framework: "react"  # Options: react, vue, html

# Hardware specifications
hardware:
  mcu: "ATmega328P"
  clock_speed: "16MHz"
  memory: "32KB"

# Pin definitions
pins:
  LED_PIN: 13
  SENSOR_PIN: A0
  BUTTON_PIN: 2

# Timing configurations
timing:
  BAUD_RATE: 9600
  SAMPLE_RATE: 100

# Peripheral definitions
peripherals:
  - type: "led"
    pin: 13
    description: "Status LED"
  
  - type: "sensor"
    pin: "A0"
    description: "Analog sensor input"
  
  - type: "button"
    pin: 2
    description: "User input button"

# Communication settings
communication:
  protocol: "serial"
  baudrate: 9600
  data_format: "json"
"""
    
    output_path = Path(output_file)
    output_path.write_text(sample_config)
    click.echo(f"✓ Sample configuration created: {output_file}")
    click.echo("\nEdit this file with your hardware specifications, then run:")
    click.echo(f"  accelerapp generate {output_file}")


@main.command()
def info():
    """Display information about Accelerapp."""
    click.echo("Accelerapp v0.1.0")
    click.echo("\nNext Generation Hardware Control Platform")
    click.echo("\nFeatures:")
    click.echo("  • Firmware generation for multiple platforms")
    click.echo("  • Software SDK generation (Python, C++, JavaScript)")
    click.echo("  • UI generation (React, Vue, HTML)")
    click.echo("  • Agentic coding swarm architecture")
    click.echo("\nSupported Platforms:")
    click.echo("  • Arduino")
    click.echo("  • STM32")
    click.echo("  • ESP32")
    click.echo("\nFor more information, visit:")
    click.echo("  https://github.com/thewriterben/Accelerapp")


if __name__ == '__main__':
    main()
