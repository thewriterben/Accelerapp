"""
Local LLM integration module for air-gapped code generation.
Provides support for multiple local LLM backends (Ollama, LocalAI, llama.cpp).
"""

from .local_llm_service import LocalLLMService, LLMBackend, LLMProvider
from .ollama_provider import OllamaProvider
from .model_manager import ModelManager, ModelInfo
from .prompt_templates import PromptTemplates

__all__ = [
    "LocalLLMService",
    "LLMBackend",
    "LLMProvider",
    "OllamaProvider",
    "ModelManager",
    "ModelInfo",
    "PromptTemplates",
]
