"""
Main LLM service interface for local model integration.
Provides unified interface for multiple LLM backends.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum


class LLMBackend(Enum):
    """Supported local LLM backends."""
    OLLAMA = "ollama"
    LOCALAI = "localai"
    LLAMACPP = "llamacpp"


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        model: str, 
        **kwargs
    ) -> str:
        """
        Generate text from prompt using local LLM.
        
        Args:
            prompt: Input prompt for generation
            model: Model name/identifier
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available.
        
        Returns:
            True if provider is ready, False otherwise
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models.
        
        Returns:
            List of model identifiers
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the provider.
        
        Returns:
            Dictionary with health status information
        """
        pass


class LocalLLMService:
    """
    Main service for managing local LLM interactions.
    Supports multiple backends with automatic fallback.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM service.
        
        Args:
            config: Configuration dictionary with LLM settings
        """
        self.config = config or {}
        self.providers: Dict[str, LLMProvider] = {}
        self.active_backend: Optional[str] = None
        self.fallback_order: List[str] = []
        
    def register_provider(
        self, 
        backend: LLMBackend, 
        provider: LLMProvider
    ) -> None:
        """
        Register a new LLM provider.
        
        Args:
            backend: Backend type
            provider: Provider instance
        """
        self.providers[backend.value] = provider
        
        # Set as active if first provider or explicitly configured
        if not self.active_backend:
            self.active_backend = backend.value
    
    def set_active_backend(self, backend: LLMBackend) -> None:
        """
        Set the active LLM backend.
        
        Args:
            backend: Backend to activate
        """
        if backend.value in self.providers:
            self.active_backend = backend.value
        else:
            raise ValueError(f"Backend {backend.value} not registered")
    
    def set_fallback_order(self, backends: List[LLMBackend]) -> None:
        """
        Set the order of backends to try on failure.
        
        Args:
            backends: List of backends in order of preference
        """
        self.fallback_order = [b.value for b in backends]
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        backend: Optional[LLMBackend] = None,
        **kwargs
    ) -> str:
        """
        Generate text using configured LLM backend.
        
        Args:
            prompt: Input prompt
            model: Optional model override
            backend: Optional backend override
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If no providers are available
        """
        # Determine which backend to use
        target_backend = (
            backend.value if backend 
            else self.active_backend
        )
        
        if not target_backend or target_backend not in self.providers:
            raise RuntimeError("No LLM backend available")
        
        # Try primary backend
        try:
            provider = self.providers[target_backend]
            if not provider.is_available():
                raise RuntimeError(f"Provider {target_backend} not available")
            
            # Use configured model or default
            model_name = model or self.config.get('default_model', 'codellama:7b')
            
            return provider.generate(prompt, model_name, **kwargs)
            
        except Exception as e:
            # Try fallback providers
            if self.fallback_order:
                for fallback_backend in self.fallback_order:
                    if fallback_backend == target_backend:
                        continue
                    
                    if fallback_backend in self.providers:
                        try:
                            provider = self.providers[fallback_backend]
                            if provider.is_available():
                                model_name = model or self.config.get('default_model', 'codellama:7b')
                                return provider.generate(prompt, model_name, **kwargs)
                        except Exception:
                            continue
            
            # All providers failed
            raise RuntimeError(f"LLM generation failed: {str(e)}")
    
    def get_available_models(
        self, 
        backend: Optional[LLMBackend] = None
    ) -> List[str]:
        """
        Get list of available models for a backend.
        
        Args:
            backend: Backend to query (defaults to active)
            
        Returns:
            List of available model identifiers
        """
        target_backend = (
            backend.value if backend 
            else self.active_backend
        )
        
        if target_backend and target_backend in self.providers:
            return self.providers[target_backend].list_models()
        
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all registered providers.
        
        Returns:
            Dictionary with health status of each provider
        """
        status = {
            'active_backend': self.active_backend,
            'providers': {}
        }
        
        for backend_name, provider in self.providers.items():
            try:
                status['providers'][backend_name] = provider.health_check()
            except Exception as e:
                status['providers'][backend_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return status
