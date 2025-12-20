"""
Anthropic provider implementation for online LLM integration.
Supports cloud-based code generation using Anthropic's Claude models.
"""

from typing import Dict, Any, List, Optional
import json
import urllib.request
import urllib.error
import os
from .local_llm_service import LLMProvider


class AnthropicProvider(LLMProvider):
    """
    Anthropic LLM provider for cloud-based code generation.
    Communicates with Anthropic API via HTTPS.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    SUPPORTED_MODELS = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    API_VERSION = "2023-06-01"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.anthropic.com",
        timeout: int = 120,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            base_url: Base URL for Anthropic API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._available = None

    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """
        Generate text using Anthropic Claude model.

        Args:
            prompt: Input prompt for generation
            model: Model name (e.g., 'claude-sonnet-4-20250514', 'claude-3-opus-20240229')
            **kwargs: Additional generation parameters
                - temperature (float): Sampling temperature (default: 0.7)
                - max_tokens (int): Maximum tokens to generate (default: 4096)
                - top_p (float): Nucleus sampling parameter
                - stop_sequences (List[str]): Stop sequences
                - system_prompt (str): System prompt for context

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails or API key is not configured
        """
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured")

        url = f"{self.base_url}/v1/messages"

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Prepare request data
        data: Dict[str, Any] = {
            "model": model or self.DEFAULT_MODEL,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        # Add system prompt if provided
        system_prompt = kwargs.get("system_prompt")
        if system_prompt:
            data["system"] = system_prompt

        # Add optional parameters
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        else:
            data["temperature"] = 0.7

        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]

        if "stop_sequences" in kwargs:
            data["stop_sequences"] = kwargs["stop_sequences"]
        elif "stop" in kwargs:
            data["stop_sequences"] = kwargs["stop"]

        try:
            # Build headers
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": self.API_VERSION,
            }

            # Make request to Anthropic API
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

                # Extract text from response
                if "content" in result and len(result["content"]) > 0:
                    # Anthropic returns content as array of content blocks
                    text_blocks = [
                        block.get("text", "")
                        for block in result["content"]
                        if block.get("type") == "text"
                    ]
                    return "".join(text_blocks)
                return ""

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"Anthropic API error ({e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Anthropic: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from Anthropic: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Anthropic generation failed: {str(e)}")

    def is_available(self) -> bool:
        """
        Check if Anthropic service is available.

        Returns:
            True if API key is configured and service is accessible
        """
        if self._available is not None:
            return self._available

        if not self.api_key:
            self._available = False
            return False

        try:
            # Test API availability with a minimal request
            # Anthropic doesn't have a simple health endpoint, so we check if we can reach the API
            url = f"{self.base_url}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": self.API_VERSION,
            }

            # Send minimal request to verify connectivity
            data = {
                "model": self.DEFAULT_MODEL,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                self._available = response.status == 200
                return self._available

        except urllib.error.HTTPError as e:
            # 401 means API key is invalid, but service is reachable
            # Other 4xx errors might indicate valid API key but other issues
            if e.code == 401:
                self._available = False
            else:
                # Service is reachable but returned an error (could be rate limit, etc.)
                self._available = True
            return self._available
        except Exception:
            self._available = False
            return False

    def list_models(self) -> List[str]:
        """
        List available Anthropic models.

        Returns:
            List of supported model identifiers
        """
        # Anthropic doesn't have a models list endpoint,
        # so we return the known supported models
        return self.SUPPORTED_MODELS

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Anthropic service.

        Returns:
            Dictionary with health status
        """
        status: Dict[str, Any] = {
            "available": False,
            "provider": "anthropic",
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
            "models_count": len(self.SUPPORTED_MODELS),
            "models": self.SUPPORTED_MODELS,
        }

        try:
            if self.is_available():
                status["available"] = True
                status["status"] = "healthy"
            else:
                status["status"] = "unavailable"
                if not self.api_key:
                    status["error"] = "API key not configured"
                else:
                    status["error"] = "Cannot connect to Anthropic service"

        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)

        return status

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count (approximation)
        """
        # Simple approximation: ~4 characters per token for English text
        # For more accurate counting, use the anthropic package
        return len(text) // 4
