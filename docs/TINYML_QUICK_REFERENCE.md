# TinyML Quick Reference Card

## Quick Start

### Import the Agent
```python
from accelerapp.agents import TinyMLAgent
agent = TinyMLAgent()
```

## Task Types

### 1. Inference Code Generation
```python
spec = {
    "task_type": "inference",
    "platform": "arduino",  # or "esp32", "stm32", etc.
    "model_type": "classification",
    "input_shape": [1, 28, 28, 1],
    "num_classes": 10
}
result = agent.generate(spec)
```

### 2. Model Conversion
```python
spec = {
    "task_type": "model_conversion",
    "platform": "esp32",
    "model_path": "/path/to/model.h5",
    "optimization_level": "aggressive"  # or "standard", "conservative"
}
result = agent.generate(spec)
```

### 3. Federated Learning
```python
spec = {
    "task_type": "federated_learning",
    "platform": "stm32",
    "aggregation_method": "federated_averaging",
    "privacy_level": "differential_privacy"
}
result = agent.generate(spec)
```

### 4. Adaptive Behavior
```python
spec = {
    "task_type": "adaptive_behavior",
    "platform": "esp32",
    "adaptation_type": "online_learning"
}
result = agent.generate(spec)
```

## Firmware Integration

### With ML Support
```python
from accelerapp.firmware.generator import FirmwareGenerator

hardware_spec = {
    "platform": "arduino",
    "device_name": "SmartDevice",
    "ml_config": {
        "task_type": "inference",
        "model_type": "classification",
        "num_classes": 10
    }
}

generator = FirmwareGenerator(hardware_spec)
result = generator.generate(output_dir)
```

### Without ML Support
```python
hardware_spec = {
    "platform": "arduino",
    "device_name": "SimpleDevice",
    # No ml_config - ML will not be included
}

generator = FirmwareGenerator(hardware_spec)
result = generator.generate(output_dir)
```

## Supported Platforms

| Platform | Devices | Code |
|----------|---------|------|
| Arduino | Nano 33 BLE, Portenta H7 | `"arduino"` |
| ESP32 | ESP32, ESP32-S3 | `"esp32"` |
| STM32 | F4, F7, H7 series | `"stm32"` |
| Nordic | nRF52840, nRF5340 | `"nordic"` |
| Raspberry Pi Pico | RP2040 | `"raspberry_pi_pico"` |

## Response Structure

All responses contain:
```python
{
    "status": "success" or "error",
    "platform": "arduino",
    "files": {
        "ml_inference.h": "...",
        "ml_inference.c": "..."
    },
    # Task-specific fields
}
```

## Memory Estimates

Access memory requirements:
```python
result["memory_estimate"]
# {
#     "original_model": "0.5 MB",
#     "quantized_model": "0.12 MB",
#     "tensor_arena": "32 KB",
#     "total_estimated": "0.15 MB"
# }
```

## Performance Estimates

Access performance metrics:
```python
result["performance_estimate"]
# {
#     "inference_time": "100-500ms",
#     "power": "Low"
# }
```

## Common Patterns

### Check if Agent Can Handle Task
```python
if agent.can_handle("tinyml inference"):
    result = agent.generate(spec)
```

### Save Generated Files
```python
for filename, content in result["files"].items():
    with open(filename, "w") as f:
        f.write(content)
```

### Check Generation Status
```python
if result["status"] == "success":
    # Process result
    pass
else:
    print(f"Error: {result['message']}")
```

### Get Agent Capabilities
```python
capabilities = agent.get_capabilities()
# ['tinyml', 'edge_ai', 'neural_networks', ...]
```

### Get Agent Info
```python
info = agent.get_info()
# {
#     "name": "TinyML Agent",
#     "type": "tinyml_agent",
#     "capabilities": [...],
#     "supported_platforms": {...},
#     ...
# }
```

## Optimization Levels

### Model Conversion
- `"conservative"` - Minimal optimization, best accuracy
- `"standard"` - Balanced optimization (default)
- `"aggressive"` - Maximum optimization, smaller size

## Best Practices

1. **Always check status**: Verify `result["status"] == "success"`
2. **Review memory**: Check if target platform has sufficient memory
3. **Use quantization**: Always quantize models for embedded deployment
4. **Test on hardware**: Generated code should be tested on actual hardware
5. **Start conservative**: Use conservative optimization first, then optimize

## Error Handling

```python
result = agent.generate(spec)

if result["status"] == "error":
    print(f"Generation failed: {result['message']}")
else:
    # Process successful result
    pass
```

## Performance Benchmarks

### Inference Time (Classification)

| Platform | Small | Medium | Large |
|----------|-------|--------|-------|
| Arduino | 100-200ms | 300-500ms | 1-2s |
| ESP32 | 50-100ms | 150-300ms | 500ms-1s |
| STM32F4 | 50-100ms | 200-400ms | 800ms-1.5s |
| STM32H7 | 20-50ms | 100-200ms | 300-600ms |

### Memory Requirements

| Model Size | Original | Quantized | Arena |
|------------|----------|-----------|-------|
| Small | 500 KB | 125 KB | 32 KB |
| Medium | 2 MB | 500 KB | 64 KB |
| Large | 5 MB | 1.25 MB | 128 KB |

## Resources

- **Integration Guide**: [docs/TINYML_INTEGRATION.md](TINYML_INTEGRATION.md)
- **API Reference**: [docs/API_TINYML.md](API_TINYML.md)
- **Feature Overview**: [../TINYML_FEATURES.md](../TINYML_FEATURES.md)
- **Demo Script**: [../examples/tinyml_demo.py](../examples/tinyml_demo.py)
- **Real-World Example**: [../examples/smart_doorbell_tinyml.py](../examples/smart_doorbell_tinyml.py)

## Testing

### Run TinyML Tests
```bash
pytest tests/test_tinyml_agent.py -v
pytest tests/test_firmware_ml_integration.py -v
```

### Run Demos
```bash
python examples/tinyml_demo.py
python examples/smart_doorbell_tinyml.py
```

## Support

- **Issues**: https://github.com/thewriterben/Accelerapp/issues
- **Discussions**: https://github.com/thewriterben/Accelerapp/discussions

---

**Quick Tip**: Start with the basic inference example, then explore federated learning and adaptive behavior as needed!
