#!/usr/bin/env python3
"""
Smart Doorbell with TinyML Integration Example

This example demonstrates a complete real-world use case:
A smart doorbell with face detection and recognition using TinyML.

Features:
- Face detection using neural network
- On-device learning for new faces
- Privacy-preserving federated learning
- Low power consumption
"""

from pathlib import Path
from accelerapp.firmware.generator import FirmwareGenerator
from accelerapp.agents import TinyMLAgent


def generate_smart_doorbell():
    """Generate firmware for smart doorbell with TinyML."""
    
    print("=" * 70)
    print("Smart Doorbell with TinyML - Complete Example")
    print("=" * 70)
    
    # Hardware specification
    hardware_spec = {
        "platform": "esp32",
        "device_name": "SmartDoorbell",
        "pins": {
            "CAMERA_SDA": 21,
            "CAMERA_SCL": 22,
            "BUTTON": 0,
            "LED_STATUS": 2,
            "SPEAKER": 25,
        },
        "peripherals": [
            {
                "type": "camera",
                "interface": "i2c",
                "resolution": "96x96",
            },
            {
                "type": "button",
                "pin": 0,
                "mode": "input_pullup",
            },
            {
                "type": "led",
                "pin": 2,
                "mode": "output",
            },
            {
                "type": "speaker",
                "pin": 25,
                "mode": "output",
            },
        ],
        "timing": {
            "DEBOUNCE_MS": 50,
            "INFERENCE_INTERVAL_MS": 1000,
            "LEARNING_RATE": "0.01",
        },
        "ml_config": {
            "task_type": "inference",
            "model_type": "classification",
            "input_shape": [1, 96, 96, 1],  # 96x96 grayscale image
            "num_classes": 10,  # Up to 10 known faces
            "model_size_mb": 0.5,
        },
    }

    print("\n✓ Hardware Configuration:")
    print(f"  - Platform: {hardware_spec['platform'].upper()}")
    print(f"  - Device: {hardware_spec['device_name']}")
    print(f"  - Camera: {hardware_spec['peripherals'][0]['resolution']}")
    print(f"  - ML Classes: {hardware_spec['ml_config']['num_classes']} faces")

    # Generate firmware with ML integration
    print("\n✓ Generating firmware with TinyML integration...")
    generator = FirmwareGenerator(hardware_spec)
    
    output_dir = Path("/tmp/smart_doorbell_output")
    result = generator.generate(output_dir)

    if result["status"] == "success":
        print(f"\n✓ Generation successful!")
        print(f"  - ML Enabled: {result['ml_enabled']}")
        print(f"  - Files Generated: {len(result['files_generated'])}")
        print(f"  - Output Directory: {result['output_dir']}")
        
        print(f"\n✓ Generated Files:")
        for filepath in result["files_generated"]:
            filename = Path(filepath).name
            size = Path(filepath).stat().st_size
            print(f"  - {filename} ({size} bytes)")
    
    return result


def add_federated_learning():
    """Add federated learning for privacy-preserving updates."""
    
    print("\n" + "=" * 70)
    print("Adding Federated Learning Support")
    print("=" * 70)
    
    agent = TinyMLAgent()
    
    spec = {
        "task_type": "federated_learning",
        "platform": "esp32",
        "aggregation_method": "federated_averaging",
        "privacy_level": "differential_privacy",
    }
    
    result = agent.generate(spec)
    
    if result["status"] == "success":
        print("\n✓ Federated learning configured!")
        print("  Features:")
        for feature in result["features"]:
            print(f"  - {feature}")
        
        # Save federated learning files
        output_dir = Path("/tmp/smart_doorbell_output")
        for filename, content in result["files"].items():
            filepath = output_dir / filename
            filepath.write_text(content)
            print(f"\n✓ Saved: {filename}")
    
    return result


def add_adaptive_learning():
    """Add adaptive learning for continuous improvement."""
    
    print("\n" + "=" * 70)
    print("Adding Adaptive Learning")
    print("=" * 70)
    
    agent = TinyMLAgent()
    
    spec = {
        "task_type": "adaptive_behavior",
        "platform": "esp32",
        "adaptation_type": "online_learning",
    }
    
    result = agent.generate(spec)
    
    if result["status"] == "success":
        print("\n✓ Adaptive learning enabled!")
        print("  Features:")
        for feature in result["features"]:
            print(f"  - {feature}")
        
        # Save adaptive behavior files
        output_dir = Path("/tmp/smart_doorbell_output")
        for filename, content in result["files"].items():
            filepath = output_dir / filename
            filepath.write_text(content)
            print(f"\n✓ Saved: {filename}")
    
    return result


def analyze_performance():
    """Analyze performance characteristics."""
    
    print("\n" + "=" * 70)
    print("Performance Analysis")
    print("=" * 70)
    
    agent = TinyMLAgent()
    
    spec = {
        "task_type": "inference",
        "platform": "esp32",
        "model_type": "classification",
        "input_shape": [1, 96, 96, 1],
        "num_classes": 10,
        "model_size_mb": 0.5,
    }
    
    result = agent.generate(spec)
    
    print("\n✓ Memory Requirements:")
    for key, value in result["memory_estimate"].items():
        print(f"  - {key}: {value}")
    
    print("\n✓ Performance Estimates:")
    for key, value in result["performance_estimate"].items():
        print(f"  - {key}: {value}")
    
    print("\n✓ System Requirements:")
    print("  - RAM: 520 KB (ESP32)")
    print("  - Flash: 4 MB minimum")
    print("  - Camera: OV7670 or similar")
    print("  - Power: 5V/1A USB power")


def generate_usage_instructions():
    """Generate usage instructions."""
    
    print("\n" + "=" * 70)
    print("Usage Instructions")
    print("=" * 70)
    
    instructions = """
✓ How to Use Your Smart Doorbell:

1. Flash Firmware:
   - Open Arduino IDE or PlatformIO
   - Load the generated files from /tmp/smart_doorbell_output/
   - Connect ESP32 via USB
   - Upload firmware

2. Initial Setup:
   - Power on the device
   - Wait for initialization (LED blinks)
   - System is ready when LED stays solid

3. Training Mode (Learn New Faces):
   - Press the button for 3 seconds
   - LED blinks rapidly (training mode)
   - Stand in front of camera
   - Device captures and learns your face
   - LED blinks slowly when done

4. Recognition Mode (Normal Operation):
   - When someone approaches the door
   - Camera captures image
   - Neural network performs inference
   - If face is recognized:
     * LED turns green
     * Speaker plays welcome tone
     * Optional: Send notification
   - If face is unknown:
     * LED turns yellow
     * Speaker plays alert tone

5. Federated Learning Updates:
   - Device periodically uploads gradients (not raw images)
   - Privacy is preserved with differential privacy
   - Global model improves over time
   - Updates downloaded automatically

6. Power Management:
   - Device enters deep sleep when inactive
   - Wakes up on motion detection or button press
   - Battery life: ~7 days with 2500mAh battery

✓ LED Status Indicators:
   - Solid: Ready
   - Blinking slow: Processing
   - Blinking fast: Training mode
   - Green: Recognized face
   - Yellow: Unknown face
   - Red: Error

✓ Troubleshooting:
   - Red LED: Check camera connection
   - No inference: Verify model is loaded
   - High power usage: Reduce inference frequency
"""
    
    print(instructions)
    
    # Save instructions
    output_dir = Path("/tmp/smart_doorbell_output")
    instructions_file = output_dir / "README.txt"
    instructions_file.write_text(instructions)
    print(f"\n✓ Instructions saved to: {instructions_file}")


def main():
    """Main function."""
    
    print("\n" + "=" * 70)
    print("Smart Doorbell with TinyML")
    print("A Complete Real-World Example")
    print("=" * 70)
    
    # Step 1: Generate base firmware
    firmware_result = generate_smart_doorbell()
    
    # Step 2: Add federated learning
    fl_result = add_federated_learning()
    
    # Step 3: Add adaptive learning
    adaptive_result = add_adaptive_learning()
    
    # Step 4: Analyze performance
    analyze_performance()
    
    # Step 5: Generate instructions
    generate_usage_instructions()
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    print("\n✓ Complete smart doorbell firmware generated!")
    
    print("\n✓ Features Included:")
    print("  - Face detection and recognition")
    print("  - On-device learning for new faces")
    print("  - Federated learning for privacy")
    print("  - Adaptive behavior optimization")
    print("  - Low power consumption")
    print("  - LED and audio feedback")
    
    print("\n✓ Files Generated:")
    output_dir = Path("/tmp/smart_doorbell_output")
    files = sorted(output_dir.glob("*"))
    for filepath in files:
        size = filepath.stat().st_size
        print(f"  - {filepath.name} ({size} bytes)")
    
    print(f"\n✓ Output Directory: {output_dir}")
    
    print("\n✓ Next Steps:")
    print("  1. Review generated files")
    print("  2. Flash to ESP32 device")
    print("  3. Connect camera module")
    print("  4. Train with your faces")
    print("  5. Test recognition")
    
    print("\n✓ Privacy Features:")
    print("  - No raw images leave device")
    print("  - Differential privacy in federated learning")
    print("  - Secure local storage")
    print("  - Encrypted updates")
    
    print("\n" + "=" * 70)
    print("Smart Doorbell Generation Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
