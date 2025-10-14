"""
Tests for enhanced exception handling system.
"""

import pytest
import asyncio
import time

from src.accelerapp.core.exceptions import (
    AccelerappException,
    ErrorCode,
    ExceptionHandler,
    GlobalExceptionHandler,
    RetryPolicy,
    retry_with_backoff,
    CircuitBreaker,
    CircuitState,
    circuit_breaker,
    RecoveryStrategy,
    RecoveryManager,
    RestartStrategy,
    RetryExhaustedError,
    CircuitBreakerError,
)


class TestExceptionHierarchy:
    """Test exception hierarchy with error codes."""
    
    def test_base_exception(self):
        """Test base exception creation."""
        exc = AccelerappException(
            "Test error",
            details={"key": "value"},
            error_code=ErrorCode.SERVICE_UNAVAILABLE
        )
        
        assert exc.message == "Test error"
        assert exc.details == {"key": "value"}
        assert exc.error_code == ErrorCode.SERVICE_UNAVAILABLE
    
    def test_exception_string_representation(self):
        """Test exception string formatting."""
        exc = AccelerappException(
            "Test error",
            error_code=ErrorCode.CONFIG_INVALID
        )
        
        str_repr = str(exc)
        assert "Test error" in str_repr
        assert str(ErrorCode.CONFIG_INVALID.value) in str_repr
    
    def test_exception_to_dict(self):
        """Test converting exception to dictionary."""
        exc = AccelerappException(
            "Test error",
            details={"info": "data"},
            error_code=ErrorCode.VALIDATION_FAILED
        )
        
        exc_dict = exc.to_dict()
        assert exc_dict["message"] == "Test error"
        assert exc_dict["error_code"] == ErrorCode.VALIDATION_FAILED.value
        assert exc_dict["details"] == {"info": "data"}


class TestExceptionHandler:
    """Test exception handler functionality."""
    
    def test_register_handler(self):
        """Test registering exception handlers."""
        handler = ExceptionHandler()
        
        handled = [False]
        
        def handle_value_error(exc, context):
            handled[0] = True
        
        handler.register(ValueError, handle_value_error)
        
        exc = ValueError("Test error")
        handler.handle(exc)
        
        assert handled[0]
    
    def test_fallback_handler(self):
        """Test fallback handler for unregistered exceptions."""
        handler = ExceptionHandler()
        
        fallback_called = [False]
        
        def fallback(exc, context):
            fallback_called[0] = True
        
        handler.set_fallback(fallback)
        
        exc = RuntimeError("Test error")
        try:
            handler.handle(exc)
        except RuntimeError:
            pass
        
        assert fallback_called[0]


class TestRetryPolicy:
    """Test retry policy and mechanisms."""
    
    def test_retry_policy_creation(self):
        """Test creating retry policy."""
        policy = RetryPolicy(max_attempts=5, base_delay=2.0)
        
        assert policy.max_attempts == 5
        assert policy.base_delay == 2.0
    
    def test_should_retry(self):
        """Test retry decision logic."""
        policy = RetryPolicy(max_attempts=3, retry_on=(ValueError,))
        
        # Should retry on ValueError
        assert policy.should_retry(ValueError(), 1)
        
        # Should not retry on different exception
        assert not policy.should_retry(TypeError(), 1)
        
        # Should not retry after max attempts
        assert not policy.should_retry(ValueError(), 3)
    
    def test_get_delay_exponential(self):
        """Test exponential backoff delay calculation."""
        policy = RetryPolicy(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )
        
        delay1 = policy.get_delay(0)
        delay2 = policy.get_delay(1)
        delay3 = policy.get_delay(2)
        
        assert delay1 == 1.0
        assert delay2 == 2.0
        assert delay3 == 4.0
    
    def test_retry_decorator_success(self):
        """Test retry decorator on successful function."""
        attempts = [0]
        
        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def func():
            attempts[0] += 1
            return "success"
        
        result = func()
        assert result == "success"
        assert attempts[0] == 1
    
    def test_retry_decorator_failure_then_success(self):
        """Test retry decorator with initial failures."""
        attempts = [0]
        
        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def func():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = func()
        assert result == "success"
        assert attempts[0] == 3
    
    def test_retry_decorator_exhausted(self):
        """Test retry decorator when all attempts fail."""
        @retry_with_backoff(max_attempts=2, base_delay=0.1)
        def func():
            raise ValueError("Permanent error")
        
        with pytest.raises(RetryExhaustedError):
            func()


@pytest.mark.asyncio
class TestRetryAsync:
    """Test async retry functionality."""
    
    async def test_async_retry_success(self):
        """Test async retry with success."""
        attempts = [0]
        
        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        async def async_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = await async_func()
        assert result == "success"
        assert attempts[0] == 2


class TestCircuitBreaker:
    """Test circuit breaker pattern."""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        def func():
            return "success"
        
        result = breaker.call(func)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after failures."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        def failing_func():
            raise ValueError("Error")
        
        # Trigger failures
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        # Circuit should be open now
        assert breaker.state == CircuitState.OPEN
        
        # Next call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            breaker.call(failing_func)
    
    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            success_threshold=2
        )
        
        def failing_func():
            raise ValueError("Error")
        
        def success_func():
            return "success"
        
        # Open the circuit
        for _ in range(2):
            try:
                breaker.call(failing_func)
            except ValueError:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Should transition to half-open and succeed
        result = breaker.call(success_func)
        assert result == "success"
        
        # After success_threshold successes, should close
        breaker.call(success_func)
        assert breaker.state == CircuitState.CLOSED
    
    def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator."""
        @circuit_breaker(failure_threshold=2)
        def func(should_fail=False):
            if should_fail:
                raise ValueError("Error")
            return "success"
        
        # Successful calls
        assert func() == "success"
        
        # Fail to open circuit
        for _ in range(2):
            try:
                func(should_fail=True)
            except ValueError:
                pass
        
        # Should be open
        with pytest.raises(CircuitBreakerError):
            func()
    
    def test_circuit_breaker_reset(self):
        """Test manually resetting circuit breaker."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        def failing_func():
            raise ValueError("Error")
        
        # Open circuit
        try:
            breaker.call(failing_func)
        except ValueError:
            pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Reset
        breaker.reset()
        assert breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
class TestRecoveryStrategies:
    """Test recovery strategies."""
    
    async def test_restart_strategy(self):
        """Test restart recovery strategy."""
        class MockService:
            def __init__(self):
                self.stopped = False
                self.started = False
            
            async def stop(self):
                self.stopped = True
            
            async def start(self):
                self.started = True
        
        service = MockService()
        strategy = RestartStrategy()
        
        context = {
            "service": service,
            "service_name": "test_service"
        }
        
        result = await strategy.recover(context)
        
        assert result is True
        assert service.stopped
        assert service.started
    
    async def test_recovery_manager(self):
        """Test recovery manager."""
        manager = RecoveryManager()
        
        recovered = [False]
        
        class TestStrategy(RecoveryStrategy):
            async def recover(self, context):
                recovered[0] = True
                return True
        
        strategy = TestStrategy()
        manager.register_strategy("test_failure", strategy)
        
        result = await manager.attempt_recovery("test_failure", {})
        
        assert result is True
        assert recovered[0]
    
    async def test_recovery_manager_multiple_strategies(self):
        """Test recovery manager with multiple strategies."""
        manager = RecoveryManager()
        
        attempts = []
        
        class FailingStrategy(RecoveryStrategy):
            async def recover(self, context):
                attempts.append("failing")
                return False
        
        class SuccessStrategy(RecoveryStrategy):
            async def recover(self, context):
                attempts.append("success")
                return True
        
        manager.register_strategy("test_failure", FailingStrategy())
        manager.register_strategy("test_failure", SuccessStrategy())
        
        result = await manager.attempt_recovery("test_failure", {})
        
        assert result is True
        assert "failing" in attempts
        assert "success" in attempts
