"""
LLM integration module for code generation.
Provides support for multiple LLM backends:
- Local/Air-gapped: Ollama, LocalAI, llama.cpp
- Online/Cloud: OpenAI, Anthropic
"""

from .local_llm_service import LocalLLMService, LLMBackend, LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .model_manager import ModelManager, ModelInfo
from .prompt_templates import PromptTemplates

__all__ = [
    "LocalLLMService",
    "LLMBackend",
    "LLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "ModelManager",
    "ModelInfo",
    "PromptTemplates",
]
