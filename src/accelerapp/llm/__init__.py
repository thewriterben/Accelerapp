"""
LLM integration module for code generation.
Provides support for multiple LLM backends:
- Local/Air-gapped: Ollama, LocalAI, llama.cpp
- Online/Cloud: OpenAI, Anthropic
"""

from .anthropic_provider import AnthropicProvider
from .local_llm_service import LLMBackend, LLMProvider, LocalLLMService
from .model_manager import ModelInfo, ModelManager
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
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
