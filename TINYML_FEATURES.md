# TinyML & Edge AI Features

## Overview

Accelerapp now includes comprehensive TinyML (Tiny Machine Learning) and Edge AI capabilities, enabling developers to generate optimized machine learning code for microcontrollers and embedded systems.

## Key Features

### 🧠 On-Device Inference
Generate optimized neural network inference code for resource-constrained devices:
- Automatic code generation for Arduino, ESP32, STM32, and more
- Optimized for low memory footprint (32-128KB tensor arena)
- Supports int8 quantization for 4x size reduction
- Performance estimates for each platform

### 🔧 Model Optimization
Convert and optimize trained models for edge deployment:
- Quantization (int8, reducing model size by ~75%)
- Pruning (removing unnecessary weights)
- Knowledge distillation
- Weight sharing
- TensorFlow Lite Micro compatible output

### 🔒 Federated Learning
Privacy-preserving distributed learning infrastructure:
- Local training on device data
- Gradient aggregation without sharing raw data
- Differential privacy support
- Secure communication protocols
- Suitable for privacy-sensitive applications

### 🎯 Adaptive Behavior
Enable devices to learn and adapt in real-time:
- Online learning capabilities
- Environment adaptation
- Behavior optimization based on sensor data
- Resource-aware execution
- Perfect for smart IoT devices

## Supported Platforms

| Platform | Devices | RAM | Flash | Status |
|----------|---------|-----|-------|--------|
| **Arduino** | Nano 33 BLE, Portenta H7, Nano RP2040 | 256KB - 8MB | 1MB - 16MB | ✅ Full Support |
| **ESP32** | ESP32, ESP32-S3 | 520KB | 4MB - 16MB | ✅ Full Support |
| **STM32** | F4, F7, H7 series | 192KB - 1MB | 1MB - 2MB | ✅ Full Support |
| **Nordic** | nRF52840, nRF5340 | 256KB - 1MB | 1MB - 2MB | ✅ Full Support |
| **Raspberry Pi Pico** | RP2040 | 264KB | 2MB | ✅ Full Support |

## Quick Start

### Installation

```bash
pip install accelerapp
```

### Basic Usage

```python
from accelerapp.agents import TinyMLAgent

# Initialize the agent
agent = TinyMLAgent()

# Generate inference code
spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 96, 96, 1],  # 96x96 grayscale image
    "num_classes": 5
}

result = agent.generate(spec)

# Save generated files
with open("ml_inference.h", "w") as f:
    f.write(result["files"]["ml_inference.h"])
    
with open("ml_inference.c", "w") as f:
    f.write(result["files"]["ml_inference.c"])

print(f"✓ Memory required: {result['memory_estimate']['total_estimated']}")
print(f"✓ Inference time: {result['performance_estimate']['inference_time']}")
```

### Integration with Firmware Generator

```python
from accelerapp.firmware.generator import FirmwareGenerator
from pathlib import Path

# Hardware specification with ML
hardware_spec = {
    "platform": "arduino",
    "device_name": "SmartCamera",
    "peripherals": [
        {"type": "camera", "interface": "i2c"}
    ],
    "ml_config": {
        "task_type": "inference",
        "model_type": "classification",
        "num_classes": 3
    }
}

# Generate complete firmware with ML
generator = FirmwareGenerator(hardware_spec)
result = generator.generate(Path("./output"))

print(f"✓ Generated {len(result['files_generated'])} files")
print(f"✓ ML enabled: {result['ml_enabled']}")
```

## Use Cases

### 1. Smart Home Devices
- Voice command recognition
- Gesture control
- Occupancy detection
- Energy usage prediction

### 2. Industrial IoT
- Predictive maintenance
- Anomaly detection
- Quality control
- Process optimization

### 3. Healthcare Devices
- Vital signs monitoring
- Fall detection
- Sleep pattern analysis
- ECG classification

### 4. Agricultural IoT
- Crop disease detection
- Soil moisture prediction
- Pest identification
- Weather forecasting

### 5. Environmental Monitoring
- Air quality sensing
- Water quality analysis
- Wildlife tracking
- Climate monitoring

## Performance Benchmarks

### Inference Time (Classification Model)

| Platform | Small Model | Medium Model | Large Model |
|----------|-------------|--------------|-------------|
| Arduino Nano 33 BLE | 100-200ms | 300-500ms | 1-2s |
| ESP32 | 50-100ms | 150-300ms | 500ms-1s |
| STM32F4 | 50-100ms | 200-400ms | 800ms-1.5s |
| STM32H7 | 20-50ms | 100-200ms | 300-600ms |

### Memory Requirements

| Model Size | Original (FP32) | Quantized (INT8) | Reduction |
|------------|----------------|------------------|-----------|
| Small | 500 KB | 125 KB | 75% |
| Medium | 2 MB | 500 KB | 75% |
| Large | 5 MB | 1.25 MB | 75% |

### Power Consumption

| Platform | Inference Power | Idle Power | Deep Sleep |
|----------|----------------|------------|------------|
| Arduino | 20-50 mA | 5-10 mA | < 1 mA |
| ESP32 | 80-160 mA | 10-20 mA | < 1 mA |
| STM32F4 | 30-80 mA | 3-10 mA | < 1 µA |

## Example Applications

### Image Classification

```python
spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 96, 96, 3],  # RGB image
    "num_classes": 10
}
```

### Sensor Anomaly Detection

```python
spec = {
    "task_type": "adaptive_behavior",
    "platform": "esp32",
    "adaptation_type": "online_learning"
}
```

### Privacy-Preserving Learning

```python
spec = {
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",
    "privacy_level": "differential_privacy"
}
```

## Architecture

### Components

```
┌─────────────────────────────────────────────┐
│         Accelerapp TinyML Stack             │
├─────────────────────────────────────────────┤
│  TinyMLAgent                                │
│  ├── Inference Generation                   │
│  ├── Model Conversion                       │
│  ├── Federated Learning                     │
│  └── Adaptive Behavior                      │
├─────────────────────────────────────────────┤
│  Firmware Generator (ML Integration)        │
│  ├── ML Code Integration                    │
│  ├── Platform-Specific Optimization         │
│  └── Hardware Abstraction                   │
├─────────────────────────────────────────────┤
│  Platform Support                           │
│  ├── Arduino                                │
│  ├── ESP32                                  │
│  ├── STM32                                  │
│  ├── Nordic                                 │
│  └── Raspberry Pi Pico                      │
└─────────────────────────────────────────────┘
```

### Workflow

```
┌───────────┐     ┌──────────────┐     ┌─────────────┐
│  Train    │────▶│  Optimize    │────▶│  Generate   │
│  Model    │     │  & Convert   │     │  Code       │
└───────────┘     └──────────────┘     └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Deploy to  │
                                       │  Device     │
                                       └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  On-Device  │
                                       │  Inference  │
                                       └─────────────┘
```

## Documentation

- **[TinyML Integration Guide](docs/TINYML_INTEGRATION.md)** - Comprehensive guide with examples
- **[API Reference](docs/API_TINYML.md)** - Complete API documentation
- **[Demo Script](examples/tinyml_demo.py)** - Runnable examples

## Testing

Run the comprehensive test suite:

```bash
# Test TinyML agent
pytest tests/test_tinyml_agent.py -v

# Test firmware ML integration
pytest tests/test_firmware_ml_integration.py -v

# Run all tests
pytest tests/ -v
```

## Limitations & Considerations

### Memory Constraints
- Minimum RAM: 64KB (for very small models)
- Recommended RAM: 256KB or more
- Tensor arena: 32-128KB depending on model size

### Model Size
- Keep models under 2MB for best compatibility
- Use quantization to reduce size by ~75%
- Test on target hardware early

### Inference Speed
- Varies by platform (20ms - 2s)
- Depends on model complexity
- Consider using hardware accelerators when available

### Power Consumption
- Inference consumes more power than idle
- Use sleep modes between inferences
- Consider battery life in your design

## Roadmap

### Coming Soon
- [ ] Support for object detection models
- [ ] Image segmentation support
- [ ] Edge TPU and NPU acceleration
- [ ] AutoML integration
- [ ] Model monitoring and drift detection
- [ ] Over-the-air (OTA) model updates
- [ ] Multi-model inference
- [ ] Hardware profiling tools

### Future Enhancements
- [ ] ONNX model support
- [ ] Custom layer definitions
- [ ] Advanced pruning strategies
- [ ] Neural architecture search
- [ ] Automatic hardware selection

## Contributing

We welcome contributions! Areas where you can help:

1. **Platform Support**: Add support for new microcontrollers
2. **Optimization**: Improve quantization and pruning algorithms
3. **Examples**: Share your TinyML projects
4. **Documentation**: Improve guides and tutorials
5. **Testing**: Add more test cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Resources

### Learning
- [TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)
- [TinyML Book](https://www.oreilly.com/library/view/tinyml/9781492052036/)
- [Edge Impulse](https://www.edgeimpulse.com/)

### Community
- [TinyML Foundation](https://www.tinyml.org/)
- [GitHub Discussions](https://github.com/thewriterben/Accelerapp/discussions)
- [Project Examples](examples/)

## License

TinyML features are part of Accelerapp and are released under the MIT License.

## Support

- **Documentation**: See docs/TINYML_INTEGRATION.md
- **Issues**: https://github.com/thewriterben/Accelerapp/issues
- **Discussions**: https://github.com/thewriterben/Accelerapp/discussions

---

**Made with ❤️ by the Accelerapp team**

*Bringing Machine Learning to the Edge*
