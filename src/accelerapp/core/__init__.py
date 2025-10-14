"""
Core architecture module for Accelerapp.
Provides fundamental interfaces, dependency injection, and configuration management.
"""

from .interfaces import IService, IAgent, IPlugin, IRepository, BaseService
from .exceptions import (
    AccelerappException,
    ConfigurationError,
    ServiceError,
    ValidationError,
    ResourceError,
)
from .config import ConfigurationManager
from .dependency_injection import ServiceContainer

# Import AccelerappCore from the legacy core.py for backward compatibility
import sys
from pathlib import Path

# Get parent directory and import from core.py
parent_dir = Path(__file__).parent.parent
core_module_path = parent_dir / "core.py"
if core_module_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("accelerapp_core_legacy", core_module_path)
    if spec and spec.loader:
        core_legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core_legacy)
        AccelerappCore = core_legacy.AccelerappCore
    else:
        AccelerappCore = None
else:
    AccelerappCore = None

__all__ = [
    "IService",
    "IAgent",
    "IPlugin",
    "IRepository",
    "BaseService",
    "AccelerappException",
    "ConfigurationError",
    "ServiceError",
    "ValidationError",
    "ResourceError",
    "ConfigurationManager",
    "ServiceContainer",
]

if AccelerappCore:
    __all__.append("AccelerappCore")
