"""
Ollama provider implementation for local LLM integration.
Supports offline code generation using Ollama models.
"""

from typing import Dict, Any, List, Optional
import json
import urllib.request
import urllib.error
from .local_llm_service import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider for local code generation.
    Communicates with local Ollama instance via HTTP API.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        timeout: int = 300
    ):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._available = None
    
    def generate(
        self, 
        prompt: str, 
        model: str, 
        **kwargs
    ) -> str:
        """
        Generate text using Ollama model.
        
        Args:
            prompt: Input prompt for generation
            model: Model name (e.g., 'codellama:7b', 'llama2', 'mistral')
            **kwargs: Additional generation parameters
                - temperature (float): Sampling temperature (default: 0.7)
                - max_tokens (int): Maximum tokens to generate
                - top_p (float): Nucleus sampling parameter
                - stop (List[str]): Stop sequences
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If generation fails
        """
        url = f"{self.base_url}/api/generate"
        
        # Prepare request data
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {}
        }
        
        # Add optional parameters
        if "temperature" in kwargs:
            data["options"]["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            data["options"]["num_predict"] = kwargs["max_tokens"]
        if "top_p" in kwargs:
            data["options"]["top_p"] = kwargs["top_p"]
        if "stop" in kwargs:
            data["options"]["stop"] = kwargs["stop"]
        
        try:
            # Make request to Ollama API
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
                
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Ollama: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from Ollama: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if Ollama is running and accessible
        """
        if self._available is not None:
            return self._available
        
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                self._available = response.status == 200
                return self._available
        except Exception:
            self._available = False
            return False
    
    def list_models(self) -> List[str]:
        """
        List available Ollama models.
        
        Returns:
            List of model identifiers
        """
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                models = data.get('models', [])
                return [model.get('name', '') for model in models if model.get('name')]
                
        except Exception:
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Ollama service.
        
        Returns:
            Dictionary with health status
        """
        status = {
            'available': False,
            'base_url': self.base_url,
            'models_count': 0,
            'models': []
        }
        
        try:
            if self.is_available():
                status['available'] = True
                models = self.list_models()
                status['models'] = models
                status['models_count'] = len(models)
                status['status'] = 'healthy'
            else:
                status['status'] = 'unavailable'
                status['error'] = 'Cannot connect to Ollama service'
                
        except Exception as e:
            status['status'] = 'error'
            status['error'] = str(e)
        
        return status
    
    def pull_model(self, model: str) -> Dict[str, Any]:
        """
        Pull a model from Ollama registry.
        
        Args:
            model: Model name to pull
            
        Returns:
            Dictionary with pull status
        """
        url = f"{self.base_url}/api/pull"
        data = {
            "name": model,
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=600) as response:
                result = json.loads(response.read().decode('utf-8'))
                return {
                    'status': 'success',
                    'model': model,
                    'result': result
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'model': model,
                'error': str(e)
            }
