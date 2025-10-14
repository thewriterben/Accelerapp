"""
Tests for TinyML Agent.
"""

import pytest


def test_tinyml_agent_import():
    """Test TinyML agent import."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    assert TinyMLAgent is not None


def test_tinyml_agent_initialization():
    """Test TinyML agent initialization."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()
    assert agent.name == "TinyML Agent"
    assert "tinyml" in agent.capabilities
    assert "edge_ai" in agent.capabilities
    assert "neural_networks" in agent.capabilities


def test_tinyml_agent_can_handle():
    """Test TinyML agent task handling detection."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    # Should handle TinyML tasks
    assert agent.can_handle("tinyml model deployment")
    assert agent.can_handle("edge ai inference")
    assert agent.can_handle("neural network optimization")
    assert agent.can_handle("federated learning setup")

    # Should not handle unrelated tasks
    assert not agent.can_handle("web development")
    assert not agent.can_handle("database migration")


def test_tinyml_inference_generation():
    """Test inference code generation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_type": "classification",
        "input_shape": [1, 28, 28, 1],
        "num_classes": 10,
    }

    result = agent.generate(spec)

    assert result["status"] == "success"
    assert result["platform"] == "arduino"
    assert result["model_type"] == "classification"
    assert "ml_inference.h" in result["files"]
    assert "ml_inference.c" in result["files"]
    assert "memory_estimate" in result
    assert "performance_estimate" in result


def test_tinyml_model_conversion():
    """Test model conversion functionality."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "model_conversion",
        "platform": "esp32",
        "model_path": "/path/to/model.h5",
        "optimization_level": "aggressive",
    }

    result = agent.generate(spec)

    assert result["status"] == "success"
    assert result["platform"] == "esp32"
    assert "conversion_steps" in result
    assert "optimization_level" in result
    assert result["optimization_level"] == "aggressive"
    assert "model_data.h" in result["files"]


def test_tinyml_federated_learning():
    """Test federated learning code generation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "federated_learning",
        "platform": "stm32",
        "aggregation_method": "federated_averaging",
        "privacy_level": "differential_privacy",
    }

    result = agent.generate(spec)

    assert result["status"] == "success"
    assert result["platform"] == "stm32"
    assert "features" in result
    assert "Local model training" in result["features"]
    assert "Privacy-preserving updates" in result["features"]
    assert "federated_learning.h" in result["files"]
    assert "federated_learning.c" in result["files"]


def test_tinyml_adaptive_behavior():
    """Test adaptive behavior code generation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "adaptive_behavior",
        "platform": "esp32",
        "adaptation_type": "online_learning",
    }

    result = agent.generate(spec)

    assert result["status"] == "success"
    assert result["platform"] == "esp32"
    assert result["adaptation_type"] == "online_learning"
    assert "features" in result
    assert "Online learning" in result["features"]
    assert "adaptive_behavior.h" in result["files"]
    assert "adaptive_behavior.c" in result["files"]


def test_tinyml_supported_platforms():
    """Test supported platforms."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    assert "arduino" in agent.supported_platforms
    assert "esp32" in agent.supported_platforms
    assert "stm32" in agent.supported_platforms
    assert "raspberry_pi_pico" in agent.supported_platforms


def test_tinyml_optimization_techniques():
    """Test optimization techniques."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    assert "quantization" in agent.optimization_techniques
    assert "pruning" in agent.optimization_techniques
    assert "knowledge_distillation" in agent.optimization_techniques


def test_tinyml_agent_capabilities():
    """Test getting agent capabilities."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()
    capabilities = agent.get_capabilities()

    assert isinstance(capabilities, list)
    assert len(capabilities) > 0
    assert "tinyml" in capabilities
    assert "edge_ai" in capabilities


def test_tinyml_agent_info():
    """Test getting agent information."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()
    info = agent.get_info()

    assert info["name"] == "TinyML Agent"
    assert info["type"] == "tinyml_agent"
    assert "capabilities" in info
    assert "supported_platforms" in info
    assert "optimization_techniques" in info
    assert "version" in info


def test_tinyml_inference_header_generation():
    """Test inference header file generation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "inference",
        "platform": "arduino",
        "input_shape": [1, 28, 28, 1],
        "num_classes": 10,
    }

    result = agent.generate(spec)
    header = result["files"]["ml_inference.h"]

    assert "#ifndef ML_INFERENCE_H" in header
    assert "#define ML_INFERENCE_H" in header
    assert "ml_inference_init" in header
    assert "ml_inference_run" in header
    assert "ml_get_top_prediction" in header


def test_tinyml_inference_impl_generation():
    """Test inference implementation generation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "inference",
        "platform": "stm32",
        "model_type": "classification",
    }

    result = agent.generate(spec)
    impl = result["files"]["ml_inference.c"]

    assert '#include "ml_inference.h"' in impl
    assert "ml_inference_init" in impl
    assert "ml_inference_run" in impl
    assert "ml_get_top_prediction" in impl


def test_tinyml_memory_estimation():
    """Test memory estimation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_size_mb": 2.0,
    }

    result = agent.generate(spec)
    memory = result["memory_estimate"]

    assert "original_model" in memory
    assert "quantized_model" in memory
    assert "tensor_arena" in memory
    assert "total_estimated" in memory


def test_tinyml_performance_estimation():
    """Test performance estimation."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "inference",
        "platform": "esp32",
    }

    result = agent.generate(spec)
    performance = result["performance_estimate"]

    assert "inference_time" in performance
    assert "power" in performance


def test_tinyml_unknown_task_type():
    """Test handling of unknown task types."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    spec = {
        "task_type": "unknown_task",
        "platform": "arduino",
    }

    result = agent.generate(spec)

    assert result["status"] == "error"
    assert "Unknown task type" in result["message"]


def test_tinyml_orchestrator_integration():
    """Test TinyML agent integration with orchestrator."""
    from accelerapp.agents.orchestrator import AgentOrchestrator
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    orchestrator = AgentOrchestrator()
    agent = TinyMLAgent()
    orchestrator.register_agent(agent)

    found_agent = orchestrator.find_agent("tinyml")
    assert found_agent is not None
    assert found_agent.name == "TinyML Agent"


@pytest.mark.integration
def test_tinyml_full_workflow():
    """Test complete TinyML workflow."""
    from accelerapp.agents.tinyml_agent import TinyMLAgent

    agent = TinyMLAgent()

    # Step 1: Convert model
    conversion_spec = {
        "task_type": "model_conversion",
        "platform": "arduino",
        "model_path": "/path/to/model.h5",
    }

    conversion_result = agent.generate(conversion_spec)
    assert conversion_result["status"] == "success"

    # Step 2: Generate inference code
    inference_spec = {
        "task_type": "inference",
        "platform": "arduino",
        "model_type": "classification",
    }

    inference_result = agent.generate(inference_spec)
    assert inference_result["status"] == "success"

    # Step 3: Generate adaptive behavior
    adaptive_spec = {
        "task_type": "adaptive_behavior",
        "platform": "arduino",
    }

    adaptive_result = agent.generate(adaptive_spec)
    assert adaptive_result["status"] == "success"
