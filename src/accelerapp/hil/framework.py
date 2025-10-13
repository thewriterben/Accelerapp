"""
HIL testing framework core.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """
    Represents the result of a test execution.
    """
    test_id: str
    test_name: str
    status: TestStatus
    message: str = ""
    duration: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'status': self.status.value,
            'message': self.message,
            'duration': self.duration,
            'data': self.data,
            'timestamp': self.timestamp,
        }


class TestCase:
    """
    Base class for HIL test cases.
    """
    
    def __init__(
        self,
        test_id: str,
        name: str,
        description: str = ""
    ):
        """
        Initialize test case.
        
        Args:
            test_id: Unique test identifier
            name: Test name
            description: Test description
        """
        self.test_id = test_id
        self.name = name
        self.description = description
        self.hardware_interface = None
    
    def setup(self):
        """Setup method called before test execution."""
        pass
    
    def teardown(self):
        """Teardown method called after test execution."""
        pass
    
    def run(self) -> TestResult:
        """
        Execute the test.
        
        Returns:
            TestResult object
        """
        start_time = datetime.utcnow()
        
        try:
            self.setup()
            self.execute()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_id=self.test_id,
                test_name=self.name,
                status=TestStatus.PASSED,
                message="Test passed",
                duration=duration,
                timestamp=end_time.isoformat()
            )
        
        except AssertionError as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_id=self.test_id,
                test_name=self.name,
                status=TestStatus.FAILED,
                message=str(e),
                duration=duration,
                timestamp=end_time.isoformat()
            )
        
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_id=self.test_id,
                test_name=self.name,
                status=TestStatus.ERROR,
                message=f"Error: {str(e)}",
                duration=duration,
                timestamp=end_time.isoformat()
            )
        
        finally:
            try:
                self.teardown()
            except:
                pass
    
    def execute(self):
        """
        Main test execution method.
        Override this in subclasses.
        """
        raise NotImplementedError("Test must implement execute method")
    
    def assert_equal(self, actual, expected, message: str = ""):
        """Assert that two values are equal."""
        if actual != expected:
            msg = message or f"Expected {expected}, got {actual}"
            raise AssertionError(msg)
    
    def assert_true(self, condition: bool, message: str = ""):
        """Assert that condition is true."""
        if not condition:
            msg = message or "Condition is not true"
            raise AssertionError(msg)
    
    def assert_false(self, condition: bool, message: str = ""):
        """Assert that condition is false."""
        if condition:
            msg = message or "Condition is not false"
            raise AssertionError(msg)


class HILTestFramework:
    """
    Main HIL testing framework.
    Manages test suites and hardware interfaces.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize HIL test framework.
        
        Args:
            config: Framework configuration
        """
        self.config = config or {}
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: List[TestResult] = []
    
    def register_test(self, test_case: TestCase):
        """
        Register a test case.
        
        Args:
            test_case: TestCase instance
        """
        self.test_cases[test_case.test_id] = test_case
    
    def run_test(self, test_id: str) -> TestResult:
        """
        Run a specific test.
        
        Args:
            test_id: Test identifier
            
        Returns:
            TestResult object
        """
        if test_id not in self.test_cases:
            return TestResult(
                test_id=test_id,
                test_name="Unknown",
                status=TestStatus.ERROR,
                message="Test not found",
                timestamp=datetime.utcnow().isoformat()
            )
        
        test_case = self.test_cases[test_id]
        result = test_case.run()
        self.test_results.append(result)
        
        return result
    
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all registered tests.
        
        Returns:
            List of test results
        """
        results = []
        
        for test_id in self.test_cases:
            result = self.run_test(test_id)
            results.append(result)
        
        return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """
        Get summary of test results.
        
        Returns:
            Summary dictionary
        """
        if not self.test_results:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'error': 0,
                'skipped': 0,
            }
        
        summary = {
            'total': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r.status == TestStatus.PASSED),
            'failed': sum(1 for r in self.test_results if r.status == TestStatus.FAILED),
            'error': sum(1 for r in self.test_results if r.status == TestStatus.ERROR),
            'skipped': sum(1 for r in self.test_results if r.status == TestStatus.SKIPPED),
        }
        
        summary['pass_rate'] = (
            summary['passed'] / summary['total'] * 100
            if summary['total'] > 0 else 0
        )
        
        return summary
    
    def clear_results(self):
        """Clear all test results."""
        self.test_results.clear()
