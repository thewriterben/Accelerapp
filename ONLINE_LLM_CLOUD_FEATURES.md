# Online LLM and Cloud Support Features

**Version**: 1.1.0  
**Date**: 2025-12-20  
**Status**: Production Ready

This document describes the online LLM integration and cloud support features added to Accelerapp, enabling cloud-based code generation and artifact management.

## Overview

Accelerapp now supports both local (air-gapped) and online (cloud-based) LLM providers for code generation, as well as comprehensive cloud storage and synchronization capabilities for managing generated artifacts.

## Features

### Online LLM Providers

In addition to local LLM backends (Ollama, LocalAI, llama.cpp), Accelerapp now supports:

- **OpenAI**: GPT-4o, GPT-4-turbo, GPT-3.5-turbo and other OpenAI models
- **Anthropic**: Claude Sonnet 4, Claude Opus 4, Claude 3.5 and other Claude models

### Cloud Storage

Comprehensive cloud storage service for managing generated code artifacts:

- **Multi-provider support**: AWS S3, Azure Blob, Google Cloud Storage
- **Local backend**: For testing and air-gapped environments
- **Artifact management**: Upload, download, list, and delete code artifacts
- **Metadata tracking**: Custom metadata for each artifact
- **Sync capabilities**: Bidirectional sync between local and cloud storage

### Cloud Synchronization

Real-time synchronization service for configurations and deployments:

- **Configuration sync**: Sync device configurations to/from cloud
- **Deployment state sync**: Track deployment status across environments
- **Conflict resolution**: Automatic and custom conflict resolution
- **Background sync**: Optional auto-sync with configurable intervals

## Quick Start

### Using Online LLM Providers

```python
from accelerapp.llm import (
    LocalLLMService,
    OpenAIProvider,
    AnthropicProvider,
    LLMBackend,
)

# Initialize service
service = LocalLLMService()

# Register OpenAI provider
openai = OpenAIProvider(api_key="your-openai-api-key")
service.register_provider(LLMBackend.OPENAI, openai)

# Register Anthropic provider
anthropic = AnthropicProvider(api_key="your-anthropic-api-key")
service.register_provider(LLMBackend.ANTHROPIC, anthropic)

# Generate code using OpenAI
code = service.generate(
    prompt="Generate Arduino firmware for an LED blinker on pin 13",
    model="gpt-4o",
    backend=LLMBackend.OPENAI,
    system_prompt="You are an expert embedded systems programmer."
)
```

### Environment Variables

You can configure API keys via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Using Cloud Storage

```python
from accelerapp.cloud import (
    CloudStorageService,
    CloudStorageProvider,
    LocalStorageBackend,
)

# Initialize with local backend (for testing)
service = CloudStorageService({"bucket_name": "my-artifacts"})
backend = LocalStorageBackend("/path/to/storage")
service.register_backend(CloudStorageProvider.LOCAL, backend)

# Upload generated code
result = service.upload_artifact(
    artifact_id="firmware-001",
    data=firmware_bytes,
    artifact_type="firmware",
    metadata={"version": "1.0.0", "platform": "esp32"}
)

# Download artifact
data = service.download_artifact("firmware-001", "firmware")

# List artifacts
artifacts = service.list_artifacts(artifact_type="firmware")
```

### Using Cloud Sync

```python
from accelerapp.cloud import (
    CloudSyncService,
    SyncDirection,
    SyncStatus,
)

# Initialize sync service
sync = CloudSyncService({"sync_interval": 60})

# Register sync handler
def config_sync_handler(resource_id, direction):
    # Implement your sync logic
    return {"success": True}

sync.register_sync_handler("configuration", config_sync_handler)

# Sync configuration
record = sync.sync_configuration(
    config_id="device-config",
    config_data={"device_name": "Smart Sensor"},
    direction=SyncDirection.UPLOAD
)

# Check sync status
status = sync.get_sync_status(record.record_id)
print(f"Sync status: {status.status.value}")

# Enable auto-sync
sync.enable_auto_sync(interval=120)  # Every 2 minutes
```

## API Reference

### LLM Providers

#### OpenAIProvider

```python
class OpenAIProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,     # Or set OPENAI_API_KEY env var
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 120,
        organization: Optional[str] = None,
    ): ...
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = None,
        stop: List[str] = None,
        system_prompt: str = None,
    ) -> str: ...
    
    def is_available(self) -> bool: ...
    def list_models(self) -> List[str]: ...
    def health_check(self) -> Dict[str, Any]: ...
```

**Supported Models**:
- `gpt-4o` (default)
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

#### AnthropicProvider

```python
class AnthropicProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,     # Or set ANTHROPIC_API_KEY env var
        base_url: str = "https://api.anthropic.com",
        timeout: int = 120,
    ): ...
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = None,
        stop_sequences: List[str] = None,
        system_prompt: str = None,
    ) -> str: ...
    
    def is_available(self) -> bool: ...
    def list_models(self) -> List[str]: ...
    def health_check(self) -> Dict[str, Any]: ...
    def count_tokens(self, text: str) -> int: ...
```

**Supported Models**:
- `claude-sonnet-4-20250514` (default)
- `claude-opus-4-20250514`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

### Cloud Storage

#### CloudStorageService

```python
class CloudStorageService:
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...
    
    def register_backend(
        self,
        provider: CloudStorageProvider,
        backend: CloudStorageBackend
    ) -> None: ...
    
    def upload_artifact(
        self,
        artifact_id: str,
        data: bytes,
        artifact_type: str = "generated_code",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]: ...
    
    def download_artifact(
        self,
        artifact_id: str,
        artifact_type: str = "generated_code"
    ) -> Optional[bytes]: ...
    
    def delete_artifact(
        self,
        artifact_id: str,
        artifact_type: str = "generated_code"
    ) -> bool: ...
    
    def list_artifacts(
        self,
        artifact_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]: ...
    
    def sync_artifacts(
        self,
        local_path: str,
        artifact_type: str = "generated_code",
        direction: str = "upload",
    ) -> Dict[str, Any]: ...
```

#### CloudStorageProvider (Enum)

- `AWS_S3`: Amazon S3
- `AZURE_BLOB`: Azure Blob Storage
- `GOOGLE_CLOUD`: Google Cloud Storage
- `LOCAL`: Local filesystem (for testing)

### Cloud Sync

#### CloudSyncService

```python
class CloudSyncService:
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...
    
    def register_sync_handler(
        self,
        resource_type: str,
        handler: Callable[[str, SyncDirection], Dict[str, Any]]
    ) -> None: ...
    
    def sync_resource(
        self,
        resource_type: str,
        resource_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        data: Optional[Any] = None,
    ) -> SyncRecord: ...
    
    def sync_configuration(
        self,
        config_id: str,
        config_data: Dict[str, Any],
        direction: SyncDirection = SyncDirection.UPLOAD,
    ) -> SyncRecord: ...
    
    def sync_deployment(
        self,
        deployment_id: str,
        deployment_data: Dict[str, Any],
        direction: SyncDirection = SyncDirection.UPLOAD,
    ) -> SyncRecord: ...
    
    def enable_auto_sync(self, interval: Optional[int] = None) -> None: ...
    def disable_auto_sync(self) -> None: ...
    def get_service_status(self) -> Dict[str, Any]: ...
```

#### SyncDirection (Enum)

- `UPLOAD`: Upload to cloud
- `DOWNLOAD`: Download from cloud
- `BIDIRECTIONAL`: Two-way sync

#### SyncStatus (Enum)

- `PENDING`: Sync not started
- `IN_PROGRESS`: Sync in progress
- `COMPLETED`: Sync completed successfully
- `FAILED`: Sync failed
- `CONFLICT`: Conflict detected

## Configuration Examples

### Using OpenAI for Code Generation

```yaml
# config.yaml
llm:
  provider: openai
  model: gpt-4o
  temperature: 0.7
  max_tokens: 4096

cloud:
  storage:
    provider: local
    path: ./artifacts
```

### Using Anthropic with Cloud Storage

```yaml
# config.yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  temperature: 0.7
  max_tokens: 4096

cloud:
  storage:
    provider: aws_s3
    bucket: my-accelerapp-artifacts
    region: us-east-1
  
  sync:
    enabled: true
    interval: 60
```

## Hybrid Mode (Local + Cloud)

Accelerapp supports hybrid operation where local LLMs serve as fallback:

```python
from accelerapp.llm import (
    LocalLLMService,
    OllamaProvider,
    OpenAIProvider,
    LLMBackend,
)

service = LocalLLMService()

# Register both local and cloud providers
service.register_provider(LLMBackend.OPENAI, OpenAIProvider())
service.register_provider(LLMBackend.OLLAMA, OllamaProvider())

# Set fallback order (try OpenAI first, then Ollama)
service.set_fallback_order([LLMBackend.OPENAI, LLMBackend.OLLAMA])

# Generate code - will fallback to Ollama if OpenAI fails
code = service.generate(prompt, model="gpt-4o")
```

## Security Considerations

### API Key Management

- Never commit API keys to source control
- Use environment variables or secure secret management
- Rotate API keys regularly
- Use organization-level keys where possible

### Data Privacy

- Code generated via cloud LLMs may be processed by third-party services
- For sensitive code, use local LLMs (air-gapped mode)
- Review provider data handling policies

### Network Security

- All cloud API calls use HTTPS
- Configure timeouts appropriately
- Implement rate limiting for production use

## Backward Compatibility

All new features are:

- **Non-breaking**: Existing local-only code continues to work
- **Optional**: Cloud features can be disabled via configuration
- **Isolated**: No impact on air-gapped deployment mode

## Testing

The new features include comprehensive test coverage:

- 24 new tests for online LLM providers
- 24 new tests for cloud storage and sync services
- All 89 total tests passing

Run tests with:

```bash
pytest tests/test_llm.py tests/test_cloud.py -v
```

## Support

For questions and support:
- GitHub Issues: https://github.com/thewriterben/Accelerapp/issues
- Documentation: See README.md
- Email: thewriterben@protonmail.com

---

**License**: MIT  
**Copyright**: 2025 The Writer Ben
