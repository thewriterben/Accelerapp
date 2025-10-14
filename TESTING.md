# Testing Infrastructure Guide

**Last Updated**: 2025-10-14 | **Version**: 1.0.0 | **Coverage**: 71%

This document describes the comprehensive testing infrastructure and code quality standards for the Accelerapp project.

## Overview

Accelerapp uses a modern Python testing infrastructure with:
- **pytest** for test execution (200+ tests passing)
- **Coverage.py** for code coverage tracking (currently at 71%)
- **Black** for code formatting (line length: 100)
- **isort** for import sorting (profile: black)
- **flake8** for linting (PEP 8 compliance)
- **mypy** for type checking (static type analysis)
- **Bandit** for security scanning (vulnerability detection)
- **pre-commit** for automated quality checks (15+ hooks)
- **tox** for multi-environment testing (Python 3.8-3.12)
- **GitHub Actions** for CI/CD automation (continuous testing)

## Quick Start

### Installing Dependencies

```bash
# Install all development dependencies
pip install -r requirements.txt

# Or install just the testing dependencies
pip install pytest pytest-cov pytest-asyncio pytest-xdist
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=accelerapp --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run tests in parallel
pytest tests/ -n auto
```

## Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py                 # Test package marker
├── conftest.py                 # Shared fixtures and configuration
├── test_agents.py              # Agent system tests
├── test_api.py                 # API tests
├── test_cloud.py               # Cloud service tests
├── test_communication.py       # Communication system tests
├── test_core.py                # Core functionality tests
├── test_generators.py          # Generator tests
├── test_hardware.py            # Hardware abstraction tests
├── test_hil.py                 # Hardware-in-the-loop tests
├── test_knowledge.py           # Knowledge base tests
├── test_llm.py                 # LLM integration tests
├── test_marketplace.py         # Marketplace tests
├── test_new_agents.py          # New agent tests
├── test_optimization_agents.py # Optimization agent tests
├── test_platforms.py           # Platform support tests
├── test_protocols.py           # Protocol tests
├── test_templates.py           # Template tests
└── test_visual.py              # Visual component tests
```

## Code Quality Tools

### Black (Code Formatting)

```bash
# Check if code needs formatting
black --check --line-length=100 src/

# Format code
black --line-length=100 src/
```

### isort (Import Sorting)

```bash
# Check import order
isort --check-only --profile black --line-length=100 src/

# Sort imports
isort --profile black --line-length=100 src/
```

### flake8 (Linting)

```bash
# Run linter
flake8 src/ --max-line-length=100 --extend-ignore=E203,E266,E501,W503
```

### mypy (Type Checking)

```bash
# Run type checker
mypy src/ --ignore-missing-imports --check-untyped-defs
```

### Bandit (Security Scanning)

```bash
# Run security scan
bandit -r src/ -ll

# Generate JSON report
bandit -r src/ -f json -o bandit-report.json
```

## Pre-commit Hooks

Pre-commit hooks automatically check code quality before commits.

### Installation

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Configured Hooks

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-json**: Validate JSON files
- **check-toml**: Validate TOML files
- **detect-private-key**: Detect private keys in code
- **black**: Format Python code
- **isort**: Sort imports
- **flake8**: Lint Python code
- **bandit**: Security scanning
- **mypy**: Type checking
- **interrogate**: Check docstring coverage
- **safety**: Check for known security vulnerabilities

## Multi-Environment Testing with Tox

Tox allows testing across multiple Python versions and environments.

### Usage

```bash
# Install tox
pip install tox

# Run tests on all Python versions
tox

# Run specific environment
tox -e py311

# Run linting
tox -e lint

# Run security scans
tox -e security-scan

# Format code
tox -e format

# Clean build artifacts
tox -e clean
```

### Available Environments

- `py38`, `py39`, `py310`, `py311`, `py312`: Run tests on specific Python version
- `integration`: Run integration tests
- `performance`: Run performance tests
- `security`: Run security tests
- `all`: Run all tests
- `lint`: Run code quality checks
- `format`: Format code with black and isort
- `security-scan`: Run security scans
- `docs`: Build documentation
- `clean`: Clean up build artifacts

## CI/CD Pipeline

GitHub Actions workflows are configured for automated testing and deployment.

### Workflows

#### CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:
- **Test Job**: Runs tests on Python 3.8-3.12
- **Lint Job**: Checks code quality (black, isort, flake8, mypy)
- **Security Job**: Security scanning (bandit, safety)
- **Performance Job**: Performance tests
- **Build Job**: Builds package and validates

#### Security Scanning (`.github/workflows/security.yml`)

Runs daily and on main branch:
- Bandit security scan
- Safety dependency check
- CodeQL analysis
- Dependency review

#### Release (`.github/workflows/release.yml`)

Triggered on releases:
- Build package
- Publish to PyPI
- Create GitHub release assets
- Build and deploy documentation

## Coverage Reports

Code coverage is tracked using Coverage.py:

```bash
# Generate coverage report
pytest tests/ --cov=accelerapp --cov-report=html

# View HTML report
open htmlcov/index.html

# Generate XML report (for CI)
pytest tests/ --cov=accelerapp --cov-report=xml
```

### Current Coverage: 71.01%

Coverage goals:
- **Target**: 80%+
- **Critical paths**: 90%+
- **New features**: Must include tests

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_config`: Sample configuration dictionary
- `sample_yaml_config`: Sample YAML configuration file
- `sample_code`: Sample C/Arduino code
- `sample_python_code`: Sample Python code
- `mock_agent`: Mock agent for testing
- `reset_environment`: Reset environment variables
- `performance_threshold`: Performance test thresholds

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Example Test

```python
import pytest
from accelerapp.core import AccelerappCore

@pytest.mark.unit
def test_core_initialization():
    """Test core initialization."""
    core = AccelerappCore()
    assert core is not None

@pytest.mark.integration
def test_full_workflow(sample_config, temp_dir):
    """Test complete workflow."""
    core = AccelerappCore()
    result = core.generate(sample_config, temp_dir)
    assert result is not None
```

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.security`: Security tests
- `@pytest.mark.slow`: Slow running tests

## Configuration Files

### pyproject.toml

Modern Python project configuration with:
- Package metadata
- Build system configuration
- Tool configurations (pytest, black, isort, mypy, coverage)

### .pre-commit-config.yaml

Pre-commit hook configuration for automated checks

### tox.ini

Multi-environment testing configuration

## Best Practices

1. **Write tests first**: TDD approach when possible
2. **Keep tests isolated**: Each test should be independent
3. **Use fixtures**: Share common setup code
4. **Test edge cases**: Not just happy paths
5. **Mock external dependencies**: Avoid network calls in unit tests
6. **Meaningful assertions**: Clear and specific
7. **Documentation**: Document complex test scenarios
8. **Coverage**: Aim for 80%+ coverage
9. **Performance**: Keep tests fast
10. **Security**: Include security tests for sensitive code

## Troubleshooting

### Tests Fail Locally

```bash
# Clean up cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run tests with verbose output
pytest tests/ -vv
```

### Coverage Not Generated

```bash
# Install pytest-cov
pip install pytest-cov

# Run with coverage explicitly
pytest tests/ --cov=accelerapp --cov-report=html
```

### Pre-commit Hooks Fail

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files

# Skip hooks temporarily
git commit --no-verify
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Black documentation](https://black.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Bandit documentation](https://bandit.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)
- [tox documentation](https://tox.wiki/)

## Contributing

When contributing code:

1. Write tests for new features
2. Ensure all tests pass
3. Maintain or improve coverage
4. Follow code style guidelines
5. Run pre-commit hooks
6. Update documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
