"""
Recovery strategies for handling failures.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RecoveryStrategy(ABC):
    """Abstract base class for recovery strategies."""
    
    @abstractmethod
    async def recover(self, context: Dict[str, Any]) -> bool:
        """
        Attempt to recover from a failure.
        
        Args:
            context: Recovery context with failure information
            
        Returns:
            True if recovery succeeded
        """
        pass


class RestartStrategy(RecoveryStrategy):
    """Strategy that attempts to restart a failed service."""
    
    async def recover(self, context: Dict[str, Any]) -> bool:
        """Restart the failed service."""
        service = context.get("service")
        if not service:
            return False
        
        try:
            # Stop service
            if hasattr(service, "stop"):
                await service.stop()
            
            # Start service
            if hasattr(service, "start"):
                await service.start()
            
            logger.info(f"Successfully restarted service: {context.get('service_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart service: {e}")
            return False


class FallbackStrategy(RecoveryStrategy):
    """Strategy that uses a fallback mechanism."""
    
    def __init__(self, fallback_func: Callable):
        """
        Initialize fallback strategy.
        
        Args:
            fallback_func: Fallback function to call
        """
        self.fallback_func = fallback_func
    
    async def recover(self, context: Dict[str, Any]) -> bool:
        """Use fallback mechanism."""
        try:
            result = self.fallback_func(context)
            context["result"] = result
            logger.info("Fallback mechanism succeeded")
            return True
        except Exception as e:
            logger.error(f"Fallback mechanism failed: {e}")
            return False


class RetryStrategy(RecoveryStrategy):
    """Strategy that retries the failed operation."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        """
        Initialize retry strategy.
        
        Args:
            max_retries: Maximum number of retries
            delay: Delay between retries
        """
        self.max_retries = max_retries
        self.delay = delay
    
    async def recover(self, context: Dict[str, Any]) -> bool:
        """Retry the failed operation."""
        import asyncio
        
        operation = context.get("operation")
        if not operation:
            return False
        
        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.delay * (attempt + 1))
                result = await operation()
                context["result"] = result
                logger.info(f"Retry succeeded on attempt {attempt + 1}")
                return True
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
        
        return False


class RecoveryManager:
    """
    Manages recovery strategies for different failure types.
    
    Features:
    - Strategy registration
    - Automatic strategy selection
    - Recovery attempt tracking
    """
    
    def __init__(self):
        """Initialize recovery manager."""
        self._strategies: Dict[str, List[RecoveryStrategy]] = {}
        self._recovery_attempts: Dict[str, int] = {}
    
    def register_strategy(
        self,
        failure_type: str,
        strategy: RecoveryStrategy
    ) -> None:
        """
        Register a recovery strategy for a failure type.
        
        Args:
            failure_type: Type of failure
            strategy: Recovery strategy
        """
        if failure_type not in self._strategies:
            self._strategies[failure_type] = []
        
        self._strategies[failure_type].append(strategy)
        logger.info(f"Registered recovery strategy for {failure_type}")
    
    async def attempt_recovery(
        self,
        failure_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Attempt recovery for a failure.
        
        Args:
            failure_type: Type of failure
            context: Recovery context
            
        Returns:
            True if any strategy succeeded
        """
        if failure_type not in self._strategies:
            logger.warning(f"No recovery strategies registered for {failure_type}")
            return False
        
        # Track recovery attempts
        self._recovery_attempts[failure_type] = (
            self._recovery_attempts.get(failure_type, 0) + 1
        )
        
        # Try each strategy
        for strategy in self._strategies[failure_type]:
            try:
                if await strategy.recover(context):
                    logger.info(
                        f"Recovery succeeded for {failure_type} "
                        f"using {strategy.__class__.__name__}"
                    )
                    return True
            except Exception as e:
                logger.error(
                    f"Recovery strategy {strategy.__class__.__name__} "
                    f"failed for {failure_type}: {e}"
                )
        
        logger.error(f"All recovery strategies failed for {failure_type}")
        return False
    
    def get_recovery_stats(self) -> Dict[str, int]:
        """
        Get recovery attempt statistics.
        
        Returns:
            Dictionary of failure types and attempt counts
        """
        return self._recovery_attempts.copy()
    
    def reset_stats(self) -> None:
        """Reset recovery statistics."""
        self._recovery_attempts.clear()
