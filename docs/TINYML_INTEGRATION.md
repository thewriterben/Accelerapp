# TinyML Integration Guide

## Overview

Accelerapp now includes comprehensive TinyML (Tiny Machine Learning) and Edge AI capabilities, enabling on-device machine learning and federated learning for microcontrollers and embedded systems.

## Features

### 1. TinyML Agent

The `TinyMLAgent` provides specialized capabilities for integrating machine learning models into embedded systems:

- **On-Device Inference**: Generate optimized neural network code for microcontrollers
- **Model Optimization**: Quantization, pruning, and compression for edge deployment
- **Federated Learning**: Privacy-preserving distributed learning infrastructure
- **Adaptive Behavior**: Online learning and environment adaptation

### 2. Supported Platforms

TinyML integration works with the following platforms:

- **Arduino**: Nano 33 BLE, Portenta H7, Nano RP2040
- **ESP32**: ESP32, ESP32-S3
- **STM32**: STM32F4, STM32F7, STM32H7
- **Nordic**: nRF52840, nRF5340
- **Raspberry Pi Pico**: RP2040

### 3. Optimization Techniques

- **Quantization**: Convert float32 models to int8 (4x size reduction)
- **Pruning**: Remove unnecessary weights
- **Knowledge Distillation**: Create smaller models from larger ones
- **Weight Sharing**: Reduce memory footprint

## Getting Started

### Basic Usage

```python
from accelerapp.agents import TinyMLAgent

# Initialize the agent
agent = TinyMLAgent()

# Check if agent can handle a task
if agent.can_handle("tinyml inference"):
    print("TinyML agent ready!")
```

### Inference Code Generation

Generate optimized inference code for your microcontroller:

```python
spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 28, 28, 1],  # e.g., 28x28 grayscale image
    "num_classes": 10,
}

result = agent.generate(spec)

# Access generated files
header_code = result["files"]["ml_inference.h"]
impl_code = result["files"]["ml_inference.c"]

# Check memory requirements
memory = result["memory_estimate"]
print(f"Memory required: {memory['total_estimated']}")
```

### Model Conversion

Convert and optimize your trained model for edge deployment:

```python
spec = {
    "task_type": "model_conversion",
    "platform": "esp32",
    "model_path": "/path/to/your/model.h5",
    "optimization_level": "aggressive",  # or "standard", "conservative"
}

result = agent.generate(spec)

# Conversion results
print(f"Size reduction: {result['size_reduction']}")
print(f"Output format: {result['output_format']}")
```

### Federated Learning

Set up federated learning infrastructure:

```python
spec = {
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",
    "privacy_level": "differential_privacy",
}

result = agent.generate(spec)

# Generated files include:
# - federated_learning.h: API definitions
# - federated_learning.c: Implementation
```

### Adaptive Behavior

Enable online learning and adaptive behavior:

```python
spec = {
    "task_type": "adaptive_behavior",
    "platform": "esp32",
    "adaptation_type": "online_learning",
}

result = agent.generate(spec)

# Features:
# - Real-time parameter updates
# - Environment adaptation
# - Resource-aware execution
```

## API Reference

### TinyMLAgent Class

#### Constructor

```python
agent = TinyMLAgent()
```

Initializes the TinyML agent with default capabilities.

#### Methods

##### `can_handle(task: str) -> bool`

Check if the agent can handle a specific task.

**Parameters:**
- `task`: Task description string

**Returns:**
- `True` if the agent can handle the task, `False` otherwise

**Example:**
```python
if agent.can_handle("neural network inference"):
    # Agent can handle this task
    pass
```

##### `generate(spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]`

Generate TinyML code based on specification.

**Parameters:**
- `spec`: Specification dictionary with the following keys:
  - `task_type`: One of "inference", "model_conversion", "federated_learning", "adaptive_behavior"
  - `platform`: Target platform (e.g., "arduino", "esp32", "stm32")
  - Additional task-specific parameters

- `context`: Optional additional context

**Returns:**
- Dictionary containing:
  - `status`: "success" or "error"
  - `files`: Generated code files
  - `memory_estimate`: Memory requirements
  - `performance_estimate`: Performance metrics
  - Task-specific results

**Example:**
```python
result = agent.generate({
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
})
```

##### `get_capabilities() -> List[str]`

Get list of agent capabilities.

**Returns:**
- List of capability strings

##### `get_info() -> Dict[str, Any]`

Get agent information.

**Returns:**
- Dictionary with agent metadata

## Integration with Orchestrator

The TinyML agent integrates seamlessly with the agent orchestrator:

```python
from accelerapp.agents import AgentOrchestrator, TinyMLAgent

orchestrator = AgentOrchestrator()
tinyml_agent = TinyMLAgent()
orchestrator.register_agent(tinyml_agent)

# Find agent for TinyML tasks
agent = orchestrator.find_agent("tinyml")
```

## Code Examples

### Example 1: Image Classification on Arduino

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

# Generate inference code for image classification
spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 96, 96, 1],  # 96x96 grayscale
    "num_classes": 3,  # e.g., cat, dog, bird
}

result = agent.generate(spec)

# Save generated files
with open("ml_inference.h", "w") as f:
    f.write(result["files"]["ml_inference.h"])

with open("ml_inference.c", "w") as f:
    f.write(result["files"]["ml_inference.c"])

print(f"Memory required: {result['memory_estimate']['total_estimated']}")
print(f"Inference time: {result['performance_estimate']['inference_time']}")
```

### Example 2: Sensor Data Processing with Adaptive Learning

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

# Generate adaptive behavior for sensor processing
spec = {
    "task_type": "adaptive_behavior",
    "platform": "esp32",
    "adaptation_type": "online_learning",
}

result = agent.generate(spec)

# The generated code includes:
# - adaptive_init(): Initialize learning system
# - adaptive_update(): Update model with new data
# - adaptive_predict(): Make predictions
```

### Example 3: Privacy-Preserving Federated Learning

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

# Setup federated learning for multiple devices
spec = {
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",
    "privacy_level": "differential_privacy",
}

result = agent.generate(spec)

# Generated code provides:
# - Local training on device data
# - Gradient aggregation without sharing raw data
# - Privacy-preserving model updates
```

## Memory and Performance Considerations

### Memory Requirements

Typical memory requirements by platform:

| Platform | RAM | Flash | Tensor Arena |
|----------|-----|-------|--------------|
| Arduino Nano 33 BLE | 256 KB | 1 MB | 32 KB |
| ESP32 | 520 KB | 4 MB | 64 KB |
| STM32F4 | 192 KB | 1 MB | 32 KB |
| STM32H7 | 1 MB | 2 MB | 128 KB |

### Model Size Guidelines

- **Original model**: 0.5-5 MB (float32)
- **Quantized model**: 0.125-1.25 MB (int8, 4x reduction)
- **Tensor arena**: 32-128 KB (runtime memory)

### Performance Estimates

Inference times for typical models:

| Platform | Small Model | Medium Model | Large Model |
|----------|-------------|--------------|-------------|
| Arduino | 100-200ms | 300-500ms | 1-2s |
| ESP32 | 50-100ms | 150-300ms | 500ms-1s |
| STM32F4 | 50-100ms | 200-400ms | 800ms-1.5s |
| STM32H7 | 20-50ms | 100-200ms | 300-600ms |

## Best Practices

### 1. Model Optimization

- Always quantize models to int8 before deployment
- Use pruning to reduce model size
- Test on target hardware early in development

### 2. Memory Management

- Choose appropriate tensor arena size
- Monitor RAM usage during inference
- Use static allocation when possible

### 3. Power Efficiency

- Enable sleep modes between inferences
- Use hardware accelerators when available
- Batch predictions to reduce overhead

### 4. Federated Learning

- Minimize communication frequency
- Use differential privacy to protect user data
- Validate aggregated models before deployment

### 5. Testing

- Test with real sensor data
- Validate model accuracy on device
- Monitor inference latency and memory usage

## Troubleshooting

### Common Issues

**Issue**: Out of memory during inference
- **Solution**: Reduce model size or increase tensor arena

**Issue**: Slow inference times
- **Solution**: Use quantization and pruning, or upgrade to faster platform

**Issue**: Model accuracy degraded after quantization
- **Solution**: Use quantization-aware training or increase bit width

**Issue**: Communication failures in federated learning
- **Solution**: Check network connectivity and retry logic

## Advanced Topics

### Custom Model Architectures

The TinyML agent generates template code that can be customized for specific model architectures:

```c
// Custom layer implementation
void custom_layer_forward(const float* input, float* output, int size) {
    // Your custom layer logic
}
```

### TensorFlow Lite Micro Integration

For advanced use cases, integrate with TensorFlow Lite Micro:

```c
#define USE_TFLITE
#include "ml_inference.h"
// TFLite Micro code will be used
```

### Hardware Acceleration

On supported platforms, enable hardware acceleration:

```c
// Use ARM CMSIS-NN for acceleration
#define USE_CMSIS_NN
```

## Future Enhancements

Planned features for future releases:

- Support for more model types (object detection, segmentation)
- AutoML integration for model architecture search
- Edge TPU and NPU support
- Improved federated learning protocols
- Model monitoring and drift detection

## Resources

- [TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)
- [Edge Impulse](https://www.edgeimpulse.com/)
- [TinyML Book](https://www.oreilly.com/library/view/tinyml/9781492052036/)
- [Federated Learning: Collaborative Machine Learning](https://federated.withgoogle.com/)

## Contributing

We welcome contributions to improve TinyML integration:

1. Report issues on GitHub
2. Submit pull requests with new features
3. Share your TinyML projects and use cases

## License

TinyML integration is part of Accelerapp and is released under the MIT License.
