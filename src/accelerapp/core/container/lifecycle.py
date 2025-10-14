"""
Service lifecycle management for Accelerapp v2.0.
Provides lifecycle hooks and management for services.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """Service lifecycle states."""
    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ILifecycleAware(ABC):
    """Interface for services that need lifecycle management."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Start the service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the service."""
        pass
    
    @abstractmethod
    async def dispose(self) -> None:
        """Dispose of service resources."""
        pass


class LifecycleManager:
    """
    Manages service lifecycle operations.
    
    Features:
    - Lifecycle state tracking
    - Async lifecycle operations
    - Lifecycle hooks
    - Graceful shutdown
    """
    
    def __init__(self):
        """Initialize lifecycle manager."""
        self._services: Dict[str, Any] = {}
        self._states: Dict[str, LifecycleState] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "before_init": [],
            "after_init": [],
            "before_start": [],
            "after_start": [],
            "before_stop": [],
            "after_stop": [],
        }
    
    def register_service(self, name: str, service: Any) -> None:
        """
        Register a service for lifecycle management.
        
        Args:
            name: Service name
            service: Service instance
        """
        self._services[name] = service
        self._states[name] = LifecycleState.CREATED
        logger.info(f"Registered service '{name}' for lifecycle management")
    
    def register_hook(self, hook_type: str, callback: Callable) -> None:
        """
        Register a lifecycle hook.
        
        Args:
            hook_type: Type of hook (before_init, after_init, etc.)
            callback: Callback function
        """
        if hook_type in self._hooks:
            self._hooks[hook_type].append(callback)
    
    async def initialize_service(self, name: str) -> None:
        """
        Initialize a service.
        
        Args:
            name: Service name
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        
        service = self._services[name]
        
        try:
            self._states[name] = LifecycleState.INITIALIZING
            
            # Execute before_init hooks
            await self._execute_hooks("before_init", name, service)
            
            # Initialize service if it implements ILifecycleAware
            if isinstance(service, ILifecycleAware):
                await service.initialize()
            elif hasattr(service, "initialize"):
                result = service.initialize()
                if asyncio.iscoroutine(result):
                    await result
            
            self._states[name] = LifecycleState.INITIALIZED
            
            # Execute after_init hooks
            await self._execute_hooks("after_init", name, service)
            
            logger.info(f"Service '{name}' initialized successfully")
            
        except Exception as e:
            self._states[name] = LifecycleState.FAILED
            logger.error(f"Failed to initialize service '{name}': {e}")
            raise
    
    async def start_service(self, name: str) -> None:
        """
        Start a service.
        
        Args:
            name: Service name
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        
        service = self._services[name]
        
        try:
            self._states[name] = LifecycleState.STARTING
            
            # Execute before_start hooks
            await self._execute_hooks("before_start", name, service)
            
            # Start service if it implements ILifecycleAware
            if isinstance(service, ILifecycleAware):
                await service.start()
            elif hasattr(service, "start"):
                result = service.start()
                if asyncio.iscoroutine(result):
                    await result
            
            self._states[name] = LifecycleState.RUNNING
            
            # Execute after_start hooks
            await self._execute_hooks("after_start", name, service)
            
            logger.info(f"Service '{name}' started successfully")
            
        except Exception as e:
            self._states[name] = LifecycleState.FAILED
            logger.error(f"Failed to start service '{name}': {e}")
            raise
    
    async def stop_service(self, name: str) -> None:
        """
        Stop a service.
        
        Args:
            name: Service name
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        
        service = self._services[name]
        
        try:
            self._states[name] = LifecycleState.STOPPING
            
            # Execute before_stop hooks
            await self._execute_hooks("before_stop", name, service)
            
            # Stop service if it implements ILifecycleAware
            if isinstance(service, ILifecycleAware):
                await service.stop()
            elif hasattr(service, "stop"):
                result = service.stop()
                if asyncio.iscoroutine(result):
                    await result
            
            self._states[name] = LifecycleState.STOPPED
            
            # Execute after_stop hooks
            await self._execute_hooks("after_stop", name, service)
            
            logger.info(f"Service '{name}' stopped successfully")
            
        except Exception as e:
            self._states[name] = LifecycleState.FAILED
            logger.error(f"Failed to stop service '{name}': {e}")
            raise
    
    async def initialize_all(self) -> None:
        """Initialize all registered services."""
        for name in self._services:
            await self.initialize_service(name)
    
    async def start_all(self) -> None:
        """Start all registered services."""
        for name in self._services:
            if self._states[name] == LifecycleState.INITIALIZED:
                await self.start_service(name)
    
    async def stop_all(self) -> None:
        """Stop all registered services in reverse order."""
        for name in reversed(list(self._services.keys())):
            if self._states[name] == LifecycleState.RUNNING:
                await self.stop_service(name)
    
    async def _execute_hooks(self, hook_type: str, name: str, service: Any) -> None:
        """Execute lifecycle hooks."""
        for hook in self._hooks[hook_type]:
            try:
                result = hook(name, service)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.warning(f"Hook '{hook_type}' failed for service '{name}': {e}")
    
    def get_state(self, name: str) -> Optional[LifecycleState]:
        """
        Get the lifecycle state of a service.
        
        Args:
            name: Service name
            
        Returns:
            Service lifecycle state or None if not found
        """
        return self._states.get(name)
    
    def get_all_states(self) -> Dict[str, str]:
        """
        Get lifecycle states of all services.
        
        Returns:
            Dictionary mapping service names to their states
        """
        return {name: state.value for name, state in self._states.items()}
