"""
OpenAI provider implementation for online LLM integration.
Supports cloud-based code generation using OpenAI's GPT models.
"""

from typing import Dict, Any, List, Optional
import json
import urllib.request
import urllib.error
import os
from .local_llm_service import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider for cloud-based code generation.
    Communicates with OpenAI API via HTTPS.
    """

    DEFAULT_MODEL = "gpt-4o"
    SUPPORTED_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 120,
        organization: Optional[str] = None,
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            base_url: Base URL for OpenAI API
            timeout: Request timeout in seconds
            organization: Optional organization ID
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.organization = organization
        self._available = None

    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """
        Generate text using OpenAI model.

        Args:
            prompt: Input prompt for generation
            model: Model name (e.g., 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo')
            **kwargs: Additional generation parameters
                - temperature (float): Sampling temperature (default: 0.7)
                - max_tokens (int): Maximum tokens to generate (default: 4096)
                - top_p (float): Nucleus sampling parameter
                - stop (List[str]): Stop sequences
                - system_prompt (str): System prompt for context

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails or API key is not configured
        """
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured")

        url = f"{self.base_url}/chat/completions"

        # Build messages
        messages = []

        # Add system prompt if provided
        system_prompt = kwargs.get("system_prompt")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        # Prepare request data
        data: Dict[str, Any] = {
            "model": model or self.DEFAULT_MODEL,
            "messages": messages,
        }

        # Add optional parameters
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        else:
            data["temperature"] = 0.7

        if "max_tokens" in kwargs:
            data["max_tokens"] = kwargs["max_tokens"]
        else:
            data["max_tokens"] = 4096

        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]

        if "stop" in kwargs:
            data["stop"] = kwargs["stop"]

        try:
            # Build headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            if self.organization:
                headers["OpenAI-Organization"] = self.organization

            # Make request to OpenAI API
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Extract text from response
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return ""

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"OpenAI API error ({e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to OpenAI: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from OpenAI: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")

    def is_available(self) -> bool:
        """
        Check if OpenAI service is available.

        Returns:
            True if API key is configured and service is accessible
        """
        if self._available is not None:
            return self._available

        if not self.api_key:
            self._available = False
            return False

        try:
            # Test API availability with models endpoint
            url = f"{self.base_url}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            if self.organization:
                headers["OpenAI-Organization"] = self.organization

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                self._available = response.status == 200
                return self._available
        except Exception:
            self._available = False
            return False

    def list_models(self) -> List[str]:
        """
        List available OpenAI models.

        Returns:
            List of model identifiers suitable for code generation
        """
        if not self.api_key:
            return []

        try:
            url = f"{self.base_url}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            if self.organization:
                headers["OpenAI-Organization"] = self.organization

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                models = data.get("data", [])
                # Filter to GPT models suitable for code generation
                gpt_models = [
                    m.get("id", "")
                    for m in models
                    if m.get("id", "").startswith(("gpt-4", "gpt-3.5"))
                ]
                return sorted(gpt_models, reverse=True)

        except Exception:
            return self.SUPPORTED_MODELS

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on OpenAI service.

        Returns:
            Dictionary with health status
        """
        status: Dict[str, Any] = {
            "available": False,
            "provider": "openai",
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
            "models_count": 0,
            "models": [],
        }

        try:
            if self.is_available():
                status["available"] = True
                models = self.list_models()
                status["models"] = models
                status["models_count"] = len(models)
                status["status"] = "healthy"
            else:
                status["status"] = "unavailable"
                if not self.api_key:
                    status["error"] = "API key not configured"
                else:
                    status["error"] = "Cannot connect to OpenAI service"

        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)

        return status

    def get_usage(self) -> Dict[str, Any]:
        """
        Get API usage statistics (if available).

        Returns:
            Dictionary with usage information
        """
        # Note: OpenAI usage endpoint requires organization-level access
        return {
            "provider": "openai",
            "note": "Usage statistics available via OpenAI dashboard",
        }
