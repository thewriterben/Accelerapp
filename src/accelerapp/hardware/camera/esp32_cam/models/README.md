# TinyML Models for ESP32-CAM

This directory contains TinyML model files and utilities for ESP32-CAM AI processing.

## Supported Models

### Person Detection
- **Purpose**: Detect humans in camera frame
- **Input**: 96x96 grayscale image
- **Output**: Person detected (yes/no) with confidence
- **Model Size**: ~250KB
- **Inference Time**: ~100-200ms on ESP32

### Face Detection
- **Purpose**: Detect faces in camera frame
- **Input**: 96x96 grayscale image
- **Output**: Face bounding boxes and confidence
- **Model Size**: ~300KB
- **Inference Time**: ~150-250ms on ESP32

### Face Recognition
- **Purpose**: Identify specific individuals
- **Input**: 112x112 RGB image
- **Output**: Person ID and confidence
- **Model Size**: ~500KB
- **Inference Time**: ~200-300ms on ESP32

### Object Detection
- **Purpose**: Detect multiple object classes
- **Input**: 96x96 RGB image
- **Output**: Object classes, bounding boxes, confidence
- **Model Size**: ~400KB
- **Inference Time**: ~250-400ms on ESP32

### Gesture Recognition
- **Purpose**: Recognize hand gestures
- **Input**: 64x64 grayscale image
- **Output**: Gesture class and confidence
- **Model Size**: ~200KB
- **Inference Time**: ~80-150ms on ESP32

## Model Format

All models should be in TensorFlow Lite format (`.tflite`):

```
models/
├── person_detection.tflite
├── face_detection.tflite
├── face_recognition.tflite
├── object_detection.tflite
├── gesture_recognition.tflite
└── custom/
    └── your_model.tflite
```

## Converting Models

### From TensorFlow/Keras

```python
import tensorflow as tf

# Load your model
model = tf.keras.models.load_model('your_model.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable quantization for ESP32
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.int8]

# Convert
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Using Accelerapp TinyML Agent

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()

spec = {
    "task_type": "model_conversion",
    "platform": "esp32",
    "model_path": "your_model.h5",
    "optimization_level": "aggressive",
}

result = agent.generate(spec)
print(f"Converted model saved to: {result['output_path']}")
```

## Model Optimization

### Quantization

Reduce model size and improve inference speed:

```python
# INT8 quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.int8]

# Provide representative dataset
def representative_dataset():
    for _ in range(100):
        yield [np.random.rand(1, 96, 96, 1).astype(np.float32)]

converter.representative_dataset = representative_dataset
```

### Pruning

Remove unnecessary weights:

```python
import tensorflow_model_optimization as tfmot

# Apply pruning
pruning_params = {
    'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.0,
        final_sparsity=0.5,
        begin_step=0,
        end_step=1000
    )
}

model = tfmot.sparsity.keras.prune_low_magnitude(model, **pruning_params)
```

## Loading Models

### In Python (Accelerapp)

```python
from accelerapp.hardware.camera.esp32_cam import AIProcessor, ModelConfig

config = ModelConfig(
    model_path="models/person_detection.tflite",
    confidence_threshold=0.7,
)

ai = AIProcessor(camera, config)
ai.load_model()
```

### In ESP32 Firmware

```cpp
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "model_data.h"  // Generated from .tflite file

// Allocate memory
constexpr int kTensorArenaSize = 40000;
uint8_t tensor_arena[kTensorArenaSize];

// Load model
const tflite::Model* model = tflite::GetModel(model_data);

// Create interpreter
tflite::MicroInterpreter interpreter(
    model, resolver, tensor_arena, kTensorArenaSize
);

// Allocate tensors
interpreter.AllocateTensors();
```

## Model Performance

### Memory Requirements

| Model | Flash | RAM | PSRAM |
|-------|-------|-----|-------|
| Person Detection | 250KB | 40KB | Optional |
| Face Detection | 300KB | 50KB | Optional |
| Face Recognition | 500KB | 80KB | Recommended |
| Object Detection | 400KB | 60KB | Recommended |
| Gesture Recognition | 200KB | 35KB | Optional |

### Inference Speed

| Model | ESP32 (240MHz) | ESP32-S3 (240MHz) |
|-------|----------------|-------------------|
| Person Detection | 150ms | 80ms |
| Face Detection | 200ms | 100ms |
| Face Recognition | 250ms | 130ms |
| Object Detection | 300ms | 150ms |
| Gesture Recognition | 120ms | 60ms |

## Pre-trained Models

Download pre-trained models:

```bash
# Person detection
wget https://example.com/models/person_detection_int8.tflite

# Face detection
wget https://example.com/models/face_detection_int8.tflite
```

Or use models from:
- [TensorFlow Model Garden](https://github.com/tensorflow/models)
- [Edge Impulse](https://www.edgeimpulse.com/)
- [EloquentTinyML](https://github.com/eloquentarduino/EloquentTinyML)

## Custom Models

### Training Your Own Model

1. Collect training data
2. Train using TensorFlow/Keras
3. Convert to TFLite with quantization
4. Test on ESP32
5. Deploy via Accelerapp

Example:

```python
# Train model
model = create_model()
model.fit(train_data, train_labels, epochs=10)

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Test with Accelerapp
from accelerapp.hardware.camera.esp32_cam import AIProcessor, ModelConfig

config = ModelConfig(
    model_type=DetectionModel.CUSTOM,
    model_data=tflite_model,
)

ai = AIProcessor(camera, config)
ai.load_model()
detections = ai.detect()
```

## Model Testing

Test models before deployment:

```python
from accelerapp.hardware.camera.esp32_cam import AIProcessor

ai = AIProcessor(camera)
ai.load_model("models/your_model.tflite")

# Run inference
detections = ai.detect()

# Check performance
stats = ai.get_statistics()
print(f"Inference count: {stats['inference_count']}")
print(f"Detections: {stats['total_detections']}")
```

## Integration with TinyML Agent

Generate optimized code:

```python
from accelerapp.agents import TinyMLAgent

agent = TinyMLAgent()
ai_processor = AIProcessor(camera)

# Get integration spec
spec = ai_processor.integrate_with_tinyml_agent()

# Generate optimized code
result = agent.generate(spec)
```

## Resources

- [TensorFlow Lite Micro](https://www.tensorflow.org/lite/microcontrollers)
- [ESP-NN Library](https://github.com/espressif/esp-nn)
- [EloquentTinyML](https://github.com/eloquentarduino/EloquentTinyML)
- [Edge Impulse](https://www.edgeimpulse.com/)
- [TensorFlow Model Garden](https://github.com/tensorflow/models)

## License

Models may have different licenses. Check individual model licenses before use.
