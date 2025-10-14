# Testing Quick Start Guide

Quick reference for running tests and quality checks in Accelerapp.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Common Commands

### Run Tests

```bash
# All tests
pytest tests/

# With coverage report
pytest tests/ --cov=accelerapp --cov-report=html

# Specific test file
pytest tests/test_core.py -v

# Run in parallel (faster)
pytest tests/ -n auto
```

### Code Quality

```bash
# Format code (auto-fix)
black src/

# Check formatting
black --check src/

# Sort imports (auto-fix)
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

### Pre-commit Hooks

```bash
# Install hooks (once)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

### Multi-Environment Testing

```bash
# Test all Python versions
tox

# Test specific version
tox -e py311

# Run linting
tox -e lint

# Format code
tox -e format
```

## Test Organization

```
tests/
├── test_agents.py              # Agent system tests
├── test_api.py                 # API tests
├── test_core.py                # Core functionality
├── test_generators.py          # Generator tests
├── test_hardware.py            # Hardware abstraction
└── ... (18 test modules total)
```

## Coverage Goals

- **Current:** 71.01%
- **Target:** 80%+
- **Critical Paths:** 90%+

## CI/CD Status

Workflows run automatically on:
- Push to main/develop
- Pull requests
- Daily security scans
- Release events

## Quick Fixes

### Tests failing?
```bash
pytest tests/ -vv  # Verbose output
pytest tests/ --lf  # Run last failed
```

### Import errors?
```bash
pip install -e .  # Reinstall in development mode
```

### Pre-commit hooks failing?
```bash
pre-commit run --all-files  # See what needs fixing
git commit --no-verify      # Skip hooks (emergency only)
```

## Documentation

- Full Guide: [TESTING.md](../TESTING.md)
- Summary: [TESTING_INFRASTRUCTURE_SUMMARY.md](../TESTING_INFRASTRUCTURE_SUMMARY.md)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)

## Support

- Issues: https://github.com/thewriterben/Accelerapp/issues
- Discussions: https://github.com/thewriterben/Accelerapp/discussions
