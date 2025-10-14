"""
Saga pattern implementation for distributed transactions.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import asyncio
import logging

from .bus import Event, EventBus

logger = logging.getLogger(__name__)


class SagaState(Enum):
    """Saga execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep:
    """Represents a single step in a saga."""
    
    def __init__(
        self,
        name: str,
        action: Callable,
        compensation: Optional[Callable] = None,
    ):
        """
        Initialize saga step.
        
        Args:
            name: Step name
            action: Action to execute
            compensation: Compensation action for rollback
        """
        self.name = name
        self.action = action
        self.compensation = compensation
        self.completed = False


class Saga(ABC):
    """
    Base class for implementing sagas.
    
    A saga is a sequence of local transactions with compensating actions
    for failure recovery.
    """
    
    def __init__(self, saga_id: str):
        """
        Initialize saga.
        
        Args:
            saga_id: Unique saga identifier
        """
        self.saga_id = saga_id
        self.state = SagaState.PENDING
        self._steps: List[SagaStep] = []
        self._completed_steps: List[SagaStep] = []
        self._context: Dict[str, Any] = {}
    
    def add_step(
        self,
        name: str,
        action: Callable,
        compensation: Optional[Callable] = None,
    ) -> None:
        """
        Add a step to the saga.
        
        Args:
            name: Step name
            action: Action to execute
            compensation: Compensation action
        """
        step = SagaStep(name, action, compensation)
        self._steps.append(step)
    
    async def execute(self) -> bool:
        """
        Execute the saga.
        
        Returns:
            True if saga completed successfully
        """
        self.state = SagaState.RUNNING
        logger.info(f"Starting saga: {self.saga_id}")
        
        try:
            for step in self._steps:
                logger.info(f"Executing saga step: {step.name}")
                
                # Execute step action
                if asyncio.iscoroutinefunction(step.action):
                    result = await step.action(self._context)
                else:
                    result = step.action(self._context)
                
                # Store result in context
                self._context[step.name] = result
                
                # Mark step as completed
                step.completed = True
                self._completed_steps.append(step)
                
                logger.info(f"Completed saga step: {step.name}")
            
            self.state = SagaState.COMPLETED
            logger.info(f"Saga completed successfully: {self.saga_id}")
            return True
            
        except Exception as e:
            logger.error(f"Saga failed: {self.saga_id}, error: {e}")
            self.state = SagaState.FAILED
            
            # Compensate completed steps
            await self._compensate()
            
            return False
    
    async def _compensate(self) -> None:
        """Execute compensation actions for completed steps."""
        self.state = SagaState.COMPENSATING
        logger.info(f"Starting compensation for saga: {self.saga_id}")
        
        # Compensate in reverse order
        for step in reversed(self._completed_steps):
            if step.compensation:
                try:
                    logger.info(f"Compensating saga step: {step.name}")
                    
                    if asyncio.iscoroutinefunction(step.compensation):
                        await step.compensation(self._context)
                    else:
                        step.compensation(self._context)
                    
                    logger.info(f"Compensated saga step: {step.name}")
                    
                except Exception as e:
                    logger.error(
                        f"Compensation failed for step {step.name}: {e}"
                    )
        
        self.state = SagaState.COMPENSATED
        logger.info(f"Saga compensation completed: {self.saga_id}")
    
    def get_context(self) -> Dict[str, Any]:
        """Get saga execution context."""
        return self._context.copy()


class SagaOrchestrator:
    """
    Orchestrates saga execution and tracks saga state.
    
    Features:
    - Saga lifecycle management
    - Saga state tracking
    - Event-driven saga coordination
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize saga orchestrator.
        
        Args:
            event_bus: Optional event bus for event-driven coordination
        """
        self._sagas: Dict[str, Saga] = {}
        self._event_bus = event_bus
        
        if self._event_bus:
            self._register_event_handlers()
    
    def register_saga(self, saga: Saga) -> None:
        """
        Register a saga for orchestration.
        
        Args:
            saga: Saga instance
        """
        self._sagas[saga.saga_id] = saga
        logger.info(f"Registered saga: {saga.saga_id}")
    
    async def execute_saga(self, saga_id: str) -> bool:
        """
        Execute a registered saga.
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            True if saga completed successfully
        """
        if saga_id not in self._sagas:
            raise ValueError(f"Saga not found: {saga_id}")
        
        saga = self._sagas[saga_id]
        
        # Publish saga started event
        if self._event_bus:
            await self._event_bus.publish(Event(
                event_type="saga.started",
                data={"saga_id": saga_id},
                source="saga_orchestrator",
            ))
        
        # Execute saga
        result = await saga.execute()
        
        # Publish saga completed/failed event
        if self._event_bus:
            event_type = "saga.completed" if result else "saga.failed"
            await self._event_bus.publish(Event(
                event_type=event_type,
                data={
                    "saga_id": saga_id,
                    "state": saga.state.value,
                },
                source="saga_orchestrator",
            ))
        
        return result
    
    def get_saga(self, saga_id: str) -> Optional[Saga]:
        """
        Get a saga by ID.
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            Saga instance or None
        """
        return self._sagas.get(saga_id)
    
    def get_saga_state(self, saga_id: str) -> Optional[SagaState]:
        """
        Get the state of a saga.
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            Saga state or None
        """
        saga = self._sagas.get(saga_id)
        return saga.state if saga else None
    
    def get_all_sagas(self) -> Dict[str, str]:
        """
        Get all registered sagas and their states.
        
        Returns:
            Dictionary mapping saga IDs to their states
        """
        return {
            saga_id: saga.state.value
            for saga_id, saga in self._sagas.items()
        }
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for saga coordination."""
        if not self._event_bus:
            return
        
        # Handler for saga trigger events
        async def handle_saga_trigger(event: Event):
            saga_id = event.data.get("saga_id")
            if saga_id and saga_id in self._sagas:
                await self.execute_saga(saga_id)
        
        self._event_bus.subscribe("saga.trigger", handle_saga_trigger)
