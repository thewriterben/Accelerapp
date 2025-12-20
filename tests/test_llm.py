"""
Tests for LLM integration module.
"""

import pytest
from pathlib import Path
import tempfile
import json


def test_llm_service_import():
    """Test LLM service import."""
    from accelerapp.llm import LocalLLMService
    assert LocalLLMService is not None


def test_ollama_provider_import():
    """Test Ollama provider import."""
    from accelerapp.llm import OllamaProvider
    assert OllamaProvider is not None


def test_model_manager_import():
    """Test model manager import."""
    from accelerapp.llm import ModelManager
    assert ModelManager is not None


def test_prompt_templates_import():
    """Test prompt templates import."""
    from accelerapp.llm import PromptTemplates
    assert PromptTemplates is not None


def test_llm_service_initialization():
    """Test LLM service initialization."""
    from accelerapp.llm import LocalLLMService
    
    service = LocalLLMService()
    assert service is not None
    assert service.providers == {}
    assert service.active_backend is None


def test_llm_service_provider_registration():
    """Test provider registration."""
    from accelerapp.llm import LocalLLMService, OllamaProvider, LLMBackend
    
    service = LocalLLMService()
    provider = OllamaProvider()
    
    service.register_provider(LLMBackend.OLLAMA, provider)
    assert len(service.providers) == 1
    assert service.active_backend == LLMBackend.OLLAMA.value


def test_ollama_provider_initialization():
    """Test Ollama provider initialization."""
    from accelerapp.llm import OllamaProvider
    
    provider = OllamaProvider()
    assert provider.base_url == "http://localhost:11434"
    assert provider.timeout == 300


def test_ollama_provider_custom_url():
    """Test Ollama provider with custom URL."""
    from accelerapp.llm import OllamaProvider
    
    provider = OllamaProvider(base_url="http://custom:8080")
    assert provider.base_url == "http://custom:8080"


def test_model_manager_initialization():
    """Test model manager initialization."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        manager = ModelManager(cache_dir=cache_dir)
        
        assert manager.cache_dir == cache_dir
        assert cache_dir.exists()
        assert manager.models == {}


def test_model_manager_register_model():
    """Test model registration."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        manager = ModelManager(cache_dir=cache_dir)
        
        model_info = manager.register_model(
            name="codellama:7b",
            backend="ollama",
            size=3800000000,
            version="1.0"
        )
        
        assert model_info.name == "codellama:7b"
        assert model_info.backend == "ollama"
        assert model_info.size == 3800000000
        assert "codellama:7b" in manager.models


def test_model_manager_list_models():
    """Test model listing."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        manager = ModelManager(cache_dir=cache_dir)
        
        manager.register_model("model1", "ollama")
        manager.register_model("model2", "localai")
        manager.register_model("model3", "ollama")
        
        all_models = manager.list_models()
        assert len(all_models) == 3
        
        ollama_models = manager.list_models(backend="ollama")
        assert len(ollama_models) == 2


def test_model_manager_remove_model():
    """Test model removal."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        manager = ModelManager(cache_dir=cache_dir)
        
        manager.register_model("test_model", "ollama")
        assert "test_model" in manager.models
        
        result = manager.remove_model("test_model")
        assert result is True
        assert "test_model" not in manager.models
        
        result = manager.remove_model("nonexistent")
        assert result is False


def test_model_manager_get_recommended_models():
    """Test getting recommended models."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ModelManager(cache_dir=Path(tmpdir))
        
        code_models = manager.get_recommended_models("code_generation")
        assert len(code_models) > 0
        assert any("codellama" in m['name'] for m in code_models)
        
        firmware_models = manager.get_recommended_models("firmware")
        assert len(firmware_models) > 0


def test_model_manager_stats():
    """Test model statistics."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        manager = ModelManager(cache_dir=cache_dir)
        
        manager.register_model("model1", "ollama", size=1000000)
        manager.register_model("model2", "ollama", size=2000000)
        manager.register_model("model3", "localai", size=3000000)
        
        stats = manager.get_model_stats()
        assert stats['total_models'] == 3
        assert stats['backends']['ollama'] == 2
        assert stats['backends']['localai'] == 1
        assert stats['total_size_bytes'] == 6000000


def test_model_manager_persistence():
    """Test model metadata persistence."""
    from accelerapp.llm import ModelManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "models"
        
        # Create manager and register model
        manager1 = ModelManager(cache_dir=cache_dir)
        manager1.register_model("persistent_model", "ollama")
        
        # Create new manager instance with same cache dir
        manager2 = ModelManager(cache_dir=cache_dir)
        
        # Model should be loaded from metadata
        assert "persistent_model" in manager2.models


def test_prompt_templates_firmware():
    """Test firmware prompt formatting."""
    from accelerapp.llm import PromptTemplates
    
    prompt = PromptTemplates.format_firmware_prompt(
        platform="arduino",
        mcu="ATmega328P",
        clock_speed="16MHz",
        peripherals="LED on pin 13"
    )
    
    assert "arduino" in prompt
    assert "ATmega328P" in prompt
    assert "16MHz" in prompt
    assert "LED on pin 13" in prompt


def test_prompt_templates_sdk():
    """Test SDK prompt formatting."""
    from accelerapp.llm import PromptTemplates
    
    prompt = PromptTemplates.format_sdk_prompt(
        language="python",
        device_spec="LED controller",
        protocol="serial"
    )
    
    assert "python" in prompt
    assert "LED controller" in prompt
    assert "serial" in prompt


def test_prompt_templates_ui():
    """Test UI prompt formatting."""
    from accelerapp.llm import PromptTemplates
    
    prompt = PromptTemplates.format_ui_prompt(
        framework="react",
        device_name="Sensor Array",
        features="Real-time monitoring"
    )
    
    assert "react" in prompt
    assert "Sensor Array" in prompt
    assert "Real-time monitoring" in prompt


def test_prompt_templates_system_prompts():
    """Test system prompt generation."""
    from accelerapp.llm import PromptTemplates
    
    firmware_prompt = PromptTemplates.get_system_prompt("firmware")
    assert "embedded systems" in firmware_prompt
    
    software_prompt = PromptTemplates.get_system_prompt("software")
    assert "SDK" in software_prompt or "software" in software_prompt
    
    ui_prompt = PromptTemplates.get_system_prompt("ui")
    assert "frontend" in ui_prompt or "UI" in ui_prompt


def test_prompt_templates_add_context():
    """Test adding context to prompts."""
    from accelerapp.llm import PromptTemplates
    
    base_prompt = "Generate code for device."
    context = {
        "version": "1.0",
        "author": "test"
    }
    
    enhanced = PromptTemplates.add_context(base_prompt, context)
    assert "Generate code for device." in enhanced
    assert "version" in enhanced
    assert "author" in enhanced


# ============================================================
# Tests for Online LLM Providers (OpenAI, Anthropic)
# ============================================================


def test_openai_provider_import():
    """Test OpenAI provider import."""
    from accelerapp.llm import OpenAIProvider
    assert OpenAIProvider is not None


def test_anthropic_provider_import():
    """Test Anthropic provider import."""
    from accelerapp.llm import AnthropicProvider
    assert AnthropicProvider is not None


def test_llm_backend_online_values():
    """Test LLMBackend includes online providers."""
    from accelerapp.llm import LLMBackend
    
    assert LLMBackend.OPENAI is not None
    assert LLMBackend.ANTHROPIC is not None
    assert LLMBackend.OPENAI.value == "openai"
    assert LLMBackend.ANTHROPIC.value == "anthropic"


def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    from accelerapp.llm import OpenAIProvider
    
    provider = OpenAIProvider()
    assert provider.base_url == "https://api.openai.com/v1"
    assert provider.timeout == 120


def test_openai_provider_custom_config():
    """Test OpenAI provider with custom configuration."""
    from accelerapp.llm import OpenAIProvider
    
    provider = OpenAIProvider(
        api_key="test-key",
        base_url="https://custom.api.com",
        timeout=60,
        organization="test-org"
    )
    assert provider.api_key == "test-key"
    assert provider.base_url == "https://custom.api.com"
    assert provider.timeout == 60
    assert provider.organization == "test-org"


def test_openai_provider_health_check_no_key():
    """Test OpenAI health check without API key."""
    from accelerapp.llm import OpenAIProvider
    
    provider = OpenAIProvider(api_key=None)
    health = provider.health_check()
    
    assert health["provider"] == "openai"
    assert health["has_api_key"] is False
    assert health["available"] is False


def test_openai_provider_list_models_no_key():
    """Test listing models without API key returns empty list."""
    from accelerapp.llm import OpenAIProvider
    
    provider = OpenAIProvider(api_key=None)
    models = provider.list_models()
    
    assert isinstance(models, list)
    assert len(models) == 0


def test_openai_provider_generate_without_key_raises():
    """Test that generate raises error without API key."""
    from accelerapp.llm import OpenAIProvider
    import pytest
    
    provider = OpenAIProvider(api_key=None)
    
    with pytest.raises(RuntimeError) as exc_info:
        provider.generate("test prompt", "gpt-4o")
    
    assert "API key not configured" in str(exc_info.value)


def test_openai_provider_default_model():
    """Test OpenAI default model is set."""
    from accelerapp.llm import OpenAIProvider
    
    assert OpenAIProvider.DEFAULT_MODEL == "gpt-4o"
    assert "gpt-4o" in OpenAIProvider.SUPPORTED_MODELS


def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization."""
    from accelerapp.llm import AnthropicProvider
    
    provider = AnthropicProvider()
    assert provider.base_url == "https://api.anthropic.com"
    assert provider.timeout == 120


def test_anthropic_provider_custom_config():
    """Test Anthropic provider with custom configuration."""
    from accelerapp.llm import AnthropicProvider
    
    provider = AnthropicProvider(
        api_key="test-key",
        base_url="https://custom.api.com",
        timeout=60
    )
    assert provider.api_key == "test-key"
    assert provider.base_url == "https://custom.api.com"
    assert provider.timeout == 60


def test_anthropic_provider_health_check_no_key():
    """Test Anthropic health check without API key."""
    from accelerapp.llm import AnthropicProvider
    
    provider = AnthropicProvider(api_key=None)
    health = provider.health_check()
    
    assert health["provider"] == "anthropic"
    assert health["has_api_key"] is False
    assert health["available"] is False


def test_anthropic_provider_list_models():
    """Test listing Anthropic models returns supported models."""
    from accelerapp.llm import AnthropicProvider
    
    provider = AnthropicProvider()
    models = provider.list_models()
    
    assert isinstance(models, list)
    assert len(models) > 0
    assert "claude-sonnet-4-20250514" in models


def test_anthropic_provider_generate_without_key_raises():
    """Test that generate raises error without API key."""
    from accelerapp.llm import AnthropicProvider
    import pytest
    
    provider = AnthropicProvider(api_key=None)
    
    with pytest.raises(RuntimeError) as exc_info:
        provider.generate("test prompt", "claude-sonnet-4-20250514")
    
    assert "API key not configured" in str(exc_info.value)


def test_anthropic_provider_default_model():
    """Test Anthropic default model is set."""
    from accelerapp.llm import AnthropicProvider
    
    assert AnthropicProvider.DEFAULT_MODEL == "claude-sonnet-4-20250514"
    assert "claude-sonnet-4-20250514" in AnthropicProvider.SUPPORTED_MODELS


def test_anthropic_token_counter():
    """Test Anthropic token counter approximation."""
    from accelerapp.llm import AnthropicProvider
    
    provider = AnthropicProvider()
    count = provider.count_tokens("This is a test sentence.")
    
    assert isinstance(count, int)
    assert count > 0


def test_llm_service_register_online_providers():
    """Test registering online providers with LLM service."""
    from accelerapp.llm import (
        LocalLLMService,
        OpenAIProvider,
        AnthropicProvider,
        LLMBackend,
    )
    
    service = LocalLLMService()
    
    openai_provider = OpenAIProvider(api_key="test")
    anthropic_provider = AnthropicProvider(api_key="test")
    
    service.register_provider(LLMBackend.OPENAI, openai_provider)
    service.register_provider(LLMBackend.ANTHROPIC, anthropic_provider)
    
    assert LLMBackend.OPENAI.value in service.providers
    assert LLMBackend.ANTHROPIC.value in service.providers


def test_llm_service_set_online_backend():
    """Test setting online backend as active."""
    from accelerapp.llm import (
        LocalLLMService,
        OpenAIProvider,
        AnthropicProvider,
        LLMBackend,
    )
    
    service = LocalLLMService()
    service.register_provider(LLMBackend.OPENAI, OpenAIProvider(api_key="test"))
    service.register_provider(LLMBackend.ANTHROPIC, AnthropicProvider(api_key="test"))
    
    # First registered becomes active by default
    assert service.active_backend == LLMBackend.OPENAI.value
    
    # Switch to Anthropic
    service.set_active_backend(LLMBackend.ANTHROPIC)
    assert service.active_backend == LLMBackend.ANTHROPIC.value


def test_llm_service_health_check_with_online_providers():
    """Test health check includes online provider status."""
    from accelerapp.llm import (
        LocalLLMService,
        OpenAIProvider,
        LLMBackend,
    )
    
    service = LocalLLMService()
    service.register_provider(LLMBackend.OPENAI, OpenAIProvider(api_key=None))
    
    health = service.health_check()
    
    assert "providers" in health
    assert LLMBackend.OPENAI.value in health["providers"]
