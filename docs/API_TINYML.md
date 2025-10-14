# TinyML API Reference

This document provides a complete API reference for the TinyML integration in Accelerapp.

## Table of Contents

1. [TinyMLAgent Class](#tinymlAgent-class)
2. [Firmware Generator ML Integration](#firmware-generator-ml-integration)
3. [Specification Format](#specification-format)
4. [Response Format](#response-format)
5. [Examples](#examples)

## TinyMLAgent Class

### Constructor

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()
```

Creates a new TinyML agent instance with default capabilities.

**Returns:**
- `TinyMLAgent` instance

---

### Methods

#### `can_handle(task: str) -> bool`

Checks if the agent can handle a specific task based on keywords.

**Parameters:**
- `task` (str): Task description

**Returns:**
- `bool`: `True` if the agent can handle the task, `False` otherwise

**Keywords Detected:**
- tinyml
- edge ai
- neural network
- machine learning
- inference
- model
- quantization
- federated
- on-device

**Example:**
```python
agent = TinyMLAgent()
if agent.can_handle("tinyml inference"):
    print("Agent can handle this task")
```

---

#### `generate(spec: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]`

Generates TinyML code based on the provided specification.

**Parameters:**
- `spec` (dict): Specification dictionary (see [Specification Format](#specification-format))
- `context` (dict, optional): Additional context for generation

**Returns:**
- `dict`: Result dictionary (see [Response Format](#response-format))

**Supported Task Types:**
- `inference`: Generate inference code
- `model_conversion`: Convert and optimize models
- `federated_learning`: Setup federated learning
- `adaptive_behavior`: Generate adaptive behavior code

**Example:**
```python
spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 28, 28, 1],
    "num_classes": 10
}

result = agent.generate(spec)
```

---

#### `get_capabilities() -> List[str]`

Returns a list of agent capabilities.

**Returns:**
- `list`: List of capability strings

**Example:**
```python
capabilities = agent.get_capabilities()
print(capabilities)
# Output: ['tinyml', 'edge_ai', 'neural_networks', ...]
```

---

#### `get_info() -> Dict[str, Any]`

Returns detailed information about the agent.

**Returns:**
- `dict`: Agent information including:
  - `name`: Agent name
  - `type`: Agent type
  - `capabilities`: List of capabilities
  - `supported_platforms`: Dictionary of supported platforms
  - `optimization_techniques`: List of optimization techniques
  - `version`: Agent version
  - `description`: Agent description

**Example:**
```python
info = agent.get_info()
print(info["name"])  # Output: "TinyML Agent"
```

---

## Firmware Generator ML Integration

The `FirmwareGenerator` class now supports ML integration through the `ml_config` parameter.

### Constructor

```python
from accelerapp.firmware.generator import FirmwareGenerator

hardware_spec = {
    "platform": "arduino",
    "device_name": "SmartDevice",
    "ml_config": {
        "task_type": "inference",
        "model_type": "classification",
        "input_shape": [1, 28, 28, 1],
        "num_classes": 10
    }
}

generator = FirmwareGenerator(hardware_spec)
```

### ML Configuration

The `ml_config` parameter in the hardware specification enables ML integration:

```python
"ml_config": {
    "task_type": "inference",        # Required: inference, model_conversion, etc.
    "model_type": "classification",  # Optional: classification, regression, etc.
    "input_shape": [1, 28, 28, 1],  # Optional: Model input shape
    "num_classes": 10                # Optional: Number of output classes
}
```

### Generate Method

```python
from pathlib import Path

output_dir = Path("./output")
result = generator.generate(output_dir)

print(result["ml_enabled"])  # True if ML is enabled
```

**Returns:**
- `dict`: Generation result including:
  - `status`: Success or error status
  - `platform`: Target platform
  - `files_generated`: List of generated file paths
  - `output_dir`: Output directory path
  - `ml_enabled`: Boolean indicating if ML is enabled

---

## Specification Format

### Inference Task

```python
{
    "task_type": "inference",
    "platform": "arduino",           # Required: arduino, esp32, stm32, etc.
    "model_type": "classification",  # Optional: classification, regression, etc.
    "input_shape": [1, 28, 28, 1],  # Optional: [batch, height, width, channels]
    "num_classes": 10,               # Optional: Number of output classes
    "model_size_mb": 0.5            # Optional: Model size for estimation
}
```

### Model Conversion Task

```python
{
    "task_type": "model_conversion",
    "platform": "esp32",
    "model_path": "/path/to/model.h5",      # Required: Path to source model
    "optimization_level": "aggressive"       # Optional: standard, aggressive, conservative
}
```

### Federated Learning Task

```python
{
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",  # Optional: federated_averaging, etc.
    "privacy_level": "differential_privacy"       # Optional: differential_privacy, etc.
}
```

### Adaptive Behavior Task

```python
{
    "task_type": "adaptive_behavior",
    "platform": "esp32",
    "adaptation_type": "online_learning"  # Optional: online_learning, etc.
}
```

---

## Response Format

### Inference Response

```python
{
    "status": "success",
    "platform": "arduino",
    "model_type": "classification",
    "files": {
        "ml_inference.h": "...",  # Header file content
        "ml_inference.c": "..."   # Implementation file content
    },
    "memory_estimate": {
        "original_model": "0.5 MB",
        "quantized_model": "0.12 MB",
        "tensor_arena": "32 KB",
        "total_estimated": "0.15 MB"
    },
    "performance_estimate": {
        "inference_time": "100-500ms",
        "power": "Low"
    }
}
```

### Model Conversion Response

```python
{
    "status": "success",
    "platform": "esp32",
    "conversion_steps": [
        "Load source model",
        "Apply quantization (int8)",
        "Prune unnecessary weights",
        "Generate C array representation",
        "Create model header file"
    ],
    "optimization_level": "aggressive",
    "size_reduction": "75%",
    "output_format": "tflite_micro",
    "files": {
        "model_data.h": "...",
        "model_data.c": "..."
    }
}
```

### Federated Learning Response

```python
{
    "status": "success",
    "platform": "stm32",
    "features": [
        "Local model training",
        "Gradient aggregation",
        "Privacy-preserving updates",
        "Secure communication"
    ],
    "files": {
        "federated_learning.h": "...",
        "federated_learning.c": "..."
    }
}
```

### Adaptive Behavior Response

```python
{
    "status": "success",
    "platform": "esp32",
    "adaptation_type": "online_learning",
    "features": [
        "Online learning",
        "Environment adaptation",
        "Behavior optimization",
        "Resource-aware execution"
    ],
    "files": {
        "adaptive_behavior.h": "...",
        "adaptive_behavior.c": "..."
    }
}
```

### Error Response

```python
{
    "status": "error",
    "message": "Error description"
}
```

---

## Examples

### Example 1: Basic Inference

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

spec = {
    "task_type": "inference",
    "platform": "arduino",
    "model_type": "classification",
    "input_shape": [1, 28, 28, 1],
    "num_classes": 10
}

result = agent.generate(spec)

if result["status"] == "success":
    # Save generated files
    with open("ml_inference.h", "w") as f:
        f.write(result["files"]["ml_inference.h"])
    
    with open("ml_inference.c", "w") as f:
        f.write(result["files"]["ml_inference.c"])
    
    print(f"Memory required: {result['memory_estimate']['total_estimated']}")
```

### Example 2: Model Conversion

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

spec = {
    "task_type": "model_conversion",
    "platform": "esp32",
    "model_path": "/path/to/trained_model.h5",
    "optimization_level": "aggressive"
}

result = agent.generate(spec)

if result["status"] == "success":
    print(f"Size reduction: {result['size_reduction']}")
    print(f"Output format: {result['output_format']}")
```

### Example 3: Firmware with ML

```python
from accelerapp.firmware.generator import FirmwareGenerator
from pathlib import Path

hardware_spec = {
    "platform": "arduino",
    "device_name": "SmartSensor",
    "peripherals": [
        {"type": "sensor", "pin": 2}
    ],
    "ml_config": {
        "task_type": "inference",
        "model_type": "classification",
        "num_classes": 5
    }
}

generator = FirmwareGenerator(hardware_spec)
result = generator.generate(Path("./output"))

if result["status"] == "success":
    print(f"ML enabled: {result['ml_enabled']}")
    print(f"Files generated: {len(result['files_generated'])}")
```

### Example 4: Federated Learning

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

spec = {
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",
    "privacy_level": "differential_privacy"
}

result = agent.generate(spec)

if result["status"] == "success":
    for feature in result["features"]:
        print(f"✓ {feature}")
```

### Example 5: Multi-Platform Deployment

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()
platforms = ["arduino", "esp32", "stm32"]

for platform in platforms:
    spec = {
        "task_type": "inference",
        "platform": platform,
        "model_type": "classification"
    }
    
    result = agent.generate(spec)
    
    if result["status"] == "success":
        print(f"{platform}: {result['performance_estimate']['inference_time']}")
```

---

## Error Handling

Always check the `status` field in the response:

```python
result = agent.generate(spec)

if result["status"] == "error":
    print(f"Error: {result['message']}")
else:
    # Process successful result
    pass
```

---

## Platform Support

### Supported Platforms

| Platform | Devices | Status |
|----------|---------|--------|
| arduino | Nano 33 BLE, Portenta H7, Nano RP2040 | ✓ Supported |
| esp32 | ESP32, ESP32-S3 | ✓ Supported |
| stm32 | STM32F4, STM32F7, STM32H7 | ✓ Supported |
| nordic | nRF52840, nRF5340 | ✓ Supported |
| raspberry_pi_pico | RP2040 | ✓ Supported |

---

## Best Practices

1. **Always check the status**: Verify `result["status"] == "success"` before using the output
2. **Review memory estimates**: Ensure your target platform has sufficient memory
3. **Test on target hardware**: Generated code should be tested on actual hardware
4. **Use quantization**: Always use int8 quantization for embedded deployment
5. **Monitor performance**: Check inference times match your requirements

---

## Version Information

- **API Version**: 1.0.0
- **TinyML Agent Version**: 1.0.0
- **Last Updated**: 2025

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: See TINYML_INTEGRATION.md
