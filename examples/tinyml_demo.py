#!/usr/bin/env python3
"""
TinyML Integration Demo

This example demonstrates the TinyML and Edge AI capabilities
of Accelerapp, including:
- Neural network inference code generation
- Model conversion and optimization
- Federated learning setup
- Adaptive behavior generation
"""

from pathlib import Path
from accelerapp.agents import TinyMLAgent


def demo_inference_generation():
    """Demonstrate inference code generation."""
    print("=" * 70)
    print("Demo 1: TinyML Inference Code Generation")
    print("=" * 70)

    agent = TinyMLAgent()

    # Example: Image classification on Arduino
    spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_type": "classification",
        "input_shape": [1, 96, 96, 1],  # 96x96 grayscale image
        "num_classes": 5,  # 5 classes to classify
        "model_size_mb": 0.8,
    }

    result = agent.generate(spec)

    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Platform: {result['platform']}")
    print(f"✓ Model Type: {result['model_type']}")
    print(f"\n✓ Generated Files:")
    for filename in result["files"].keys():
        print(f"  - {filename}")

    print(f"\n✓ Memory Estimate:")
    for key, value in result["memory_estimate"].items():
        print(f"  - {key}: {value}")

    print(f"\n✓ Performance Estimate:")
    for key, value in result["performance_estimate"].items():
        print(f"  - {key}: {value}")

    # Show a snippet of generated code
    print(f"\n✓ Sample Header Code (ml_inference.h):")
    header_lines = result["files"]["ml_inference.h"].split("\n")[:15]
    for line in header_lines:
        print(f"  {line}")
    print("  ...")

    return result


def demo_model_conversion():
    """Demonstrate model conversion and optimization."""
    print("\n" + "=" * 70)
    print("Demo 2: Model Conversion and Optimization")
    print("=" * 70)

    agent = TinyMLAgent()

    # Example: Convert and optimize model for ESP32
    spec = {
        "task_type": "model_conversion",
        "platform": "esp32",
        "model_path": "/path/to/trained/model.h5",
        "optimization_level": "aggressive",
    }

    result = agent.generate(spec)

    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Platform: {result['platform']}")
    print(f"✓ Optimization Level: {result['optimization_level']}")
    print(f"✓ Size Reduction: {result['size_reduction']}")
    print(f"✓ Output Format: {result['output_format']}")

    print(f"\n✓ Conversion Steps:")
    for i, step in enumerate(result["conversion_steps"], 1):
        print(f"  {i}. {step}")

    print(f"\n✓ Generated Files:")
    for filename in result["files"].keys():
        print(f"  - {filename}")

    return result


def demo_federated_learning():
    """Demonstrate federated learning setup."""
    print("\n" + "=" * 70)
    print("Demo 3: Federated Learning Infrastructure")
    print("=" * 70)

    agent = TinyMLAgent()

    # Example: Setup federated learning for STM32
    spec = {
        "task_type": "federated_learning",
        "platform": "stm32",
        "aggregation_method": "federated_averaging",
        "privacy_level": "differential_privacy",
    }

    result = agent.generate(spec)

    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Platform: {result['platform']}")

    print(f"\n✓ Features:")
    for feature in result["features"]:
        print(f"  - {feature}")

    print(f"\n✓ Generated Files:")
    for filename in result["files"].keys():
        print(f"  - {filename}")

    # Show a snippet of federated learning code
    print(f"\n✓ Sample Header Code (federated_learning.h):")
    header_lines = result["files"]["federated_learning.h"].split("\n")[:12]
    for line in header_lines:
        print(f"  {line}")
    print("  ...")

    return result


def demo_adaptive_behavior():
    """Demonstrate adaptive behavior generation."""
    print("\n" + "=" * 70)
    print("Demo 4: Adaptive Behavior with Online Learning")
    print("=" * 70)

    agent = TinyMLAgent()

    # Example: Generate adaptive behavior for ESP32
    spec = {
        "task_type": "adaptive_behavior",
        "platform": "esp32",
        "adaptation_type": "online_learning",
    }

    result = agent.generate(spec)

    print(f"\n✓ Status: {result['status']}")
    print(f"✓ Platform: {result['platform']}")
    print(f"✓ Adaptation Type: {result['adaptation_type']}")

    print(f"\n✓ Features:")
    for feature in result["features"]:
        print(f"  - {feature}")

    print(f"\n✓ Generated Files:")
    for filename in result["files"].keys():
        print(f"  - {filename}")

    return result


def demo_multi_platform_comparison():
    """Compare TinyML performance across platforms."""
    print("\n" + "=" * 70)
    print("Demo 5: Multi-Platform Comparison")
    print("=" * 70)

    agent = TinyMLAgent()
    platforms = ["arduino", "esp32", "stm32", "raspberry_pi_pico"]

    print("\n✓ Comparing TinyML inference across platforms:")
    print(f"\n{'Platform':<20} {'Inference Time':<20} {'Power':<15}")
    print("-" * 55)

    for platform in platforms:
        spec = {
            "task_type": "inference",
            "platform": platform,
            "model_type": "classification",
        }

        result = agent.generate(spec)
        perf = result["performance_estimate"]
        print(
            f"{platform:<20} {perf['inference_time']:<20} {perf['power']:<15}"
        )


def demo_agent_capabilities():
    """Demonstrate agent capabilities and information."""
    print("\n" + "=" * 70)
    print("Demo 6: TinyML Agent Capabilities")
    print("=" * 70)

    agent = TinyMLAgent()

    # Get agent info
    info = agent.get_info()

    print(f"\n✓ Agent Name: {info['name']}")
    print(f"✓ Agent Type: {info['type']}")
    print(f"✓ Version: {info['version']}")
    print(f"✓ Description: {info['description']}")

    print(f"\n✓ Capabilities:")
    for capability in info["capabilities"]:
        print(f"  - {capability}")

    print(f"\n✓ Supported Platforms:")
    for platform, devices in info["supported_platforms"].items():
        print(f"  - {platform}: {', '.join(devices)}")

    print(f"\n✓ Optimization Techniques:")
    for technique in info["optimization_techniques"]:
        print(f"  - {technique}")


def demo_save_generated_code():
    """Save generated code to files."""
    print("\n" + "=" * 70)
    print("Demo 7: Saving Generated Code")
    print("=" * 70)

    agent = TinyMLAgent()

    # Generate inference code
    spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_type": "classification",
    }

    result = agent.generate(spec)

    # Create output directory
    output_dir = Path("/tmp/tinyml_demo_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n✓ Saving generated files to: {output_dir}")

    # Save each generated file
    for filename, content in result["files"].items():
        filepath = output_dir / filename
        filepath.write_text(content)
        print(f"  ✓ Saved: {filename} ({len(content)} bytes)")

    print(f"\n✓ All files saved successfully!")
    print(f"✓ You can now integrate these files into your Arduino project")

    return output_dir


def demo_full_workflow():
    """Demonstrate complete TinyML workflow."""
    print("\n" + "=" * 70)
    print("Demo 8: Complete TinyML Workflow")
    print("=" * 70)

    agent = TinyMLAgent()

    print("\n✓ Step 1: Model Conversion")
    conversion_spec = {
        "task_type": "model_conversion",
        "platform": "arduino",
        "model_path": "/path/to/model.h5",
        "optimization_level": "standard",
    }
    conversion_result = agent.generate(conversion_spec)
    print(f"  ✓ Model converted with {conversion_result['size_reduction']} size reduction")

    print("\n✓ Step 2: Generate Inference Code")
    inference_spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_type": "classification",
    }
    inference_result = agent.generate(inference_spec)
    print(f"  ✓ Inference code generated for {inference_result['platform']}")

    print("\n✓ Step 3: Add Adaptive Behavior")
    adaptive_spec = {
        "task_type": "adaptive_behavior",
        "platform": "arduino",
        "adaptation_type": "online_learning",
    }
    adaptive_result = agent.generate(adaptive_spec)
    print(f"  ✓ Adaptive behavior enabled with {adaptive_result['adaptation_type']}")

    print("\n✓ Step 4: Setup Federated Learning (Optional)")
    federated_spec = {
        "task_type": "federated_learning",
        "platform": "arduino",
    }
    federated_result = agent.generate(federated_spec)
    print(f"  ✓ Federated learning infrastructure ready")

    print("\n✓ Complete workflow finished!")
    print("  Your Arduino device now has:")
    print("  - Optimized neural network inference")
    print("  - Adaptive learning capabilities")
    print("  - Federated learning support")


def main():
    """Run all TinyML demos."""
    print("\n" + "=" * 70)
    print("Accelerapp TinyML Integration Demo")
    print("=" * 70)
    print("\nThis demo showcases Edge AI and TinyML capabilities for")
    print("microcontrollers and embedded systems.")

    # Run all demos
    demo_inference_generation()
    demo_model_conversion()
    demo_federated_learning()
    demo_adaptive_behavior()
    demo_multi_platform_comparison()
    demo_agent_capabilities()
    output_dir = demo_save_generated_code()
    demo_full_workflow()

    # Summary
    print("\n" + "=" * 70)
    print("Demo Summary")
    print("=" * 70)
    print("\n✓ All TinyML features demonstrated successfully!")
    print("\n✓ Key Takeaways:")
    print("  - TinyML enables on-device machine learning")
    print("  - Models can be optimized for microcontrollers")
    print("  - Federated learning protects user privacy")
    print("  - Adaptive behavior allows online learning")
    print("  - Code is generated for multiple platforms")
    print(f"\n✓ Generated code saved to: {output_dir}")
    print("\n✓ Next Steps:")
    print("  1. Review generated code files")
    print("  2. Integrate into your embedded project")
    print("  3. Test on target hardware")
    print("  4. Customize for your specific use case")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
