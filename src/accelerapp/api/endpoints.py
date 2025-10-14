"""
REST API endpoints for code generation and agent interaction.
Provides HTTP interface to Accelerapp functionality.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .rate_limiter import RateLimiter, APIKeyManager, RateLimitRule

# HTTP server support is optional
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    HTTPServer = None
    BaseHTTPRequestHandler = None

logger = logging.getLogger(__name__)


class CodeGenerationAPI:
    """
    REST API for code generation and agent services.
    """

    def __init__(self, accelerapp_core, host: str = "localhost", port: int = 8080):
        """
        Initialize API server.

        Args:
            accelerapp_core: AccelerappCore instance
            host: Server host
            port: Server port
        """
        if not HTTP_AVAILABLE:
            raise RuntimeError("HTTP server not available")

        self.core = accelerapp_core
        self.host = host
        self.port = port
        self.rate_limiter = RateLimiter()
        self.api_key_manager = APIKeyManager()
        self.server = None

        # Set default rate limits
        self.rate_limiter.set_rule(
            "default", RateLimitRule(max_requests=100, time_window=3600)  # 1 hour
        )

        # LLM-specific rate limits (more restrictive)
        self.rate_limiter.set_rule(
            "llm", RateLimitRule(max_requests=20, time_window=3600, burst_size=5)  # 1 hour
        )

    def start(self):
        """Start the API server."""
        handler = self._create_handler()
        self.server = HTTPServer((self.host, self.port), handler)
        logger.info(f"API server started on http://{self.host}:{self.port}")
        self.server.serve_forever()

    def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.shutdown()
            logger.info("API server stopped")

    def _create_handler(self):
        """Create request handler with access to API instance."""
        api_instance = self

        class APIHandler(BaseHTTPRequestHandler):
            """HTTP request handler for API endpoints."""

            def _set_headers(self, status=200, content_type="application/json"):
                """Set response headers."""
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

            def _send_json(self, data: Dict[str, Any], status=200):
                """Send JSON response."""
                self._set_headers(status)
                self.wfile.write(json.dumps(data).encode())

            def _send_error_json(self, message: str, status=400):
                """Send error response."""
                self._send_json({"error": message}, status)

            def _authenticate(self) -> Optional[str]:
                """Authenticate request using API key."""
                auth_header = self.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    return None

                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
                valid, client_id = api_instance.api_key_manager.validate_key(api_key)

                return client_id if valid else None

            def _check_rate_limit(self, client_id: str, limit_type: str = "default") -> bool:
                """Check rate limit for client."""
                allowed, info = api_instance.rate_limiter.check_limit(f"{limit_type}:{client_id}")

                if not allowed:
                    self._send_json(
                        {"error": "Rate limit exceeded", "retry_after": info["retry_after"]}, 429
                    )

                return allowed

            def do_GET(self):
                """Handle GET requests."""
                parsed = urlparse(self.path)
                path = parsed.path

                if path == "/health":
                    # Health check endpoint
                    self._send_json({"status": "healthy", "version": "1.0.0"})

                elif path == "/api/agents":
                    # List available agents
                    # No authentication required for listing
                    agents = []
                    if hasattr(api_instance.core, "agents"):
                        for agent in api_instance.core.agents.values():
                            agents.append(agent.get_info())

                    self._send_json({"agents": agents})

                elif path == "/api/platforms":
                    # List supported platforms
                    platforms = [
                        "arduino",
                        "esp32",
                        "stm32",
                        "raspberry_pi",
                        "raspberry_pi_pico",
                        "micropython",
                    ]
                    self._send_json({"platforms": platforms})

                else:
                    self._send_error_json("Not found", 404)

            def do_POST(self):
                """Handle POST requests."""
                # Authenticate
                client_id = self._authenticate()
                if not client_id:
                    self._send_error_json("Unauthorized", 401)
                    return

                # Parse request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body.decode())
                except json.JSONDecodeError:
                    self._send_error_json("Invalid JSON")
                    return

                parsed = urlparse(self.path)
                path = parsed.path

                if path == "/api/generate/firmware":
                    # Generate firmware code
                    if not self._check_rate_limit(client_id, "llm"):
                        return

                    self._handle_firmware_generation(data, client_id)

                elif path == "/api/generate/software":
                    # Generate software SDK
                    if not self._check_rate_limit(client_id, "llm"):
                        return

                    self._handle_software_generation(data, client_id)

                elif path == "/api/generate/ui":
                    # Generate UI code
                    if not self._check_rate_limit(client_id, "llm"):
                        return

                    self._handle_ui_generation(data, client_id)

                elif path == "/api/analyze/performance":
                    # Analyze code performance
                    if not self._check_rate_limit(client_id):
                        return

                    self._handle_performance_analysis(data, client_id)

                elif path == "/api/analyze/security":
                    # Analyze code security
                    if not self._check_rate_limit(client_id):
                        return

                    self._handle_security_analysis(data, client_id)

                elif path == "/api/optimize/memory":
                    # Optimize memory usage
                    if not self._check_rate_limit(client_id):
                        return

                    self._handle_memory_optimization(data, client_id)

                elif path == "/api/keys/generate":
                    # Generate new API key (admin only)
                    self._handle_key_generation(data, client_id)

                else:
                    self._send_error_json("Not found", 404)

            def _handle_firmware_generation(self, data: Dict[str, Any], client_id: str):
                """Handle firmware generation request."""
                try:
                    platform = data.get("platform")
                    spec = data.get("spec", {})
                    use_llm = data.get("use_llm", False)

                    if not platform:
                        self._send_error_json("Platform required")
                        return

                    # Generate firmware
                    result = api_instance.core.generate_firmware(
                        platform=platform, spec=spec, use_llm=use_llm
                    )

                    self._send_json(
                        {
                            "status": "success",
                            "platform": platform,
                            "code": result.get("code", ""),
                            "files": result.get("files", []),
                        }
                    )

                except Exception as e:
                    logger.error(f"Firmware generation error: {e}")
                    self._send_error_json(f"Generation failed: {str(e)}", 500)

            def _handle_software_generation(self, data: Dict[str, Any], client_id: str):
                """Handle software SDK generation request."""
                try:
                    language = data.get("language", "python")
                    spec = data.get("spec", {})

                    result = api_instance.core.generate_software(language=language, spec=spec)

                    self._send_json(
                        {
                            "status": "success",
                            "language": language,
                            "code": result.get("code", ""),
                            "files": result.get("files", []),
                        }
                    )

                except Exception as e:
                    logger.error(f"Software generation error: {e}")
                    self._send_error_json(f"Generation failed: {str(e)}", 500)

            def _handle_ui_generation(self, data: Dict[str, Any], client_id: str):
                """Handle UI generation request."""
                try:
                    framework = data.get("framework", "react")
                    spec = data.get("spec", {})

                    result = api_instance.core.generate_ui(framework=framework, spec=spec)

                    self._send_json(
                        {
                            "status": "success",
                            "framework": framework,
                            "code": result.get("code", ""),
                            "files": result.get("files", []),
                        }
                    )

                except Exception as e:
                    logger.error(f"UI generation error: {e}")
                    self._send_error_json(f"Generation failed: {str(e)}", 500)

            def _handle_performance_analysis(self, data: Dict[str, Any], client_id: str):
                """Handle performance analysis request."""
                try:
                    code = data.get("code", "")
                    language = data.get("language", "cpp")

                    # Use optimization agent if available
                    from ..agents.optimization_agents import PerformanceOptimizationAgent

                    agent = PerformanceOptimizationAgent()
                    result = agent.generate({"code": code, "language": language})

                    self._send_json(result)

                except Exception as e:
                    logger.error(f"Performance analysis error: {e}")
                    self._send_error_json(f"Analysis failed: {str(e)}", 500)

            def _handle_security_analysis(self, data: Dict[str, Any], client_id: str):
                """Handle security analysis request."""
                try:
                    code = data.get("code", "")
                    language = data.get("language", "cpp")

                    from ..agents.optimization_agents import SecurityAnalysisAgent

                    agent = SecurityAnalysisAgent()
                    result = agent.generate({"code": code, "language": language})

                    self._send_json(result)

                except Exception as e:
                    logger.error(f"Security analysis error: {e}")
                    self._send_error_json(f"Analysis failed: {str(e)}", 500)

            def _handle_memory_optimization(self, data: Dict[str, Any], client_id: str):
                """Handle memory optimization request."""
                try:
                    code = data.get("code", "")
                    language = data.get("language", "cpp")
                    platform = data.get("platform", "arduino")

                    from ..agents.optimization_agents import MemoryOptimizationAgent

                    agent = MemoryOptimizationAgent()
                    result = agent.generate(
                        {"code": code, "language": language, "platform": platform}
                    )

                    self._send_json(result)

                except Exception as e:
                    logger.error(f"Memory optimization error: {e}")
                    self._send_error_json(f"Optimization failed: {str(e)}", 500)

            def _handle_key_generation(self, data: Dict[str, Any], client_id: str):
                """Handle API key generation request."""
                try:
                    new_client_id = data.get("client_id")
                    permissions = data.get("permissions", ["read", "write"])

                    if not new_client_id:
                        self._send_error_json("client_id required")
                        return

                    api_key = api_instance.api_key_manager.generate_key(new_client_id, permissions)

                    self._send_json(
                        {
                            "status": "success",
                            "api_key": api_key,
                            "client_id": new_client_id,
                            "permissions": permissions,
                        }
                    )

                except Exception as e:
                    logger.error(f"Key generation error: {e}")
                    self._send_error_json(f"Generation failed: {str(e)}", 500)

        return APIHandler
