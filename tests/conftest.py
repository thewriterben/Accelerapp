"""Shared pytest fixtures and configuration for all tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> dict:
    """Provide a sample configuration for testing."""
    return {
        'name': 'test_device',
        'platform': 'esp32',
        'peripherals': [
            {
                'type': 'sensor',
                'name': 'temperature',
                'pin': 34
            }
        ]
    }


@pytest.fixture
def sample_yaml_config(temp_dir: Path, sample_config: dict) -> Path:
    """Create a sample YAML config file for testing."""
    import yaml
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    return config_file


@pytest.fixture
def sample_code() -> str:
    """Provide sample code for testing code analysis."""
    return """
void setup() {
    Serial.begin(9600);
    pinMode(13, OUTPUT);
}

void loop() {
    digitalWrite(13, HIGH);
    delay(1000);
    digitalWrite(13, LOW);
    delay(1000);
}
"""


@pytest.fixture
def sample_python_code() -> str:
    """Provide sample Python code for testing."""
    return """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 10)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    from accelerapp.agents.base_agent import BaseAgent
    
    class MockAgent(BaseAgent):
        def __init__(self):
            super().__init__()
            self.name = "Mock Agent"
            self.capabilities = ["test_capability"]
        
        def can_handle(self, task: str) -> bool:
            return "test" in task.lower()
        
        def generate(self, spec: dict, context: dict = None) -> dict:
            return {
                'status': 'success',
                'result': 'mock_result'
            }
        
        def get_info(self) -> dict:
            return {
                'name': self.name,
                'capabilities': self.capabilities
            }
    
    return MockAgent()


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def performance_threshold() -> dict:
    """Define performance thresholds for performance tests."""
    return {
        'max_execution_time': 5.0,  # seconds
        'max_memory_usage': 100 * 1024 * 1024,  # 100 MB
        'max_cpu_percent': 80.0,  # percent
    }


# Markers for organizing tests
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
