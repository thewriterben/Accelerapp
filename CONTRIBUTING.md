# Contributing to Accelerapp

**Last Updated**: 2025-10-14 | **Version**: 1.0.0

Thank you for your interest in contributing to Accelerapp! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Bug Reports**: Submit detailed bug reports with reproduction steps
- **Feature Requests**: Propose new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve or expand documentation
- **Examples**: Create example projects showcasing Accelerapp

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Accelerapp.git
   cd Accelerapp
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Python Code Quality
- Follow **PEP 8** style guidelines (enforced by flake8)
- Use **Black** for code formatting (line length: 100)
- Sort imports with **isort** (profile: black)
- Add comprehensive **docstrings** to all classes and functions
- Include **type hints** throughout (checked by mypy)
- Write **unit tests** for new functionality (pytest)
- Maintain or improve **code coverage** (target: 80%+)
- Keep changes **focused and atomic**

### Security Standards
- Run **Bandit** security scanner before committing
- Never commit secrets, API keys, or credentials
- Follow secure coding practices
- Review code for CWE vulnerabilities
- Validate all user inputs

### Documentation Standards
- Update README.md for user-facing changes
- Update relevant documentation files
- Add docstrings with examples for complex functions
- Keep CHANGELOG.md up to date
- Document configuration options

## Testing

### Running Tests

Run the full test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=accelerapp --cov-report=html tests/

# Run specific test file
pytest tests/test_core.py -v

# Run tests in parallel
pytest tests/ -n auto

# Run with specific markers
pytest -m unit tests/
pytest -m integration tests/
```

### Quality Checks

Run all quality checks before committing:

```bash
# Format code
black --line-length=100 src/

# Sort imports
isort --profile black --line-length=100 src/

# Lint code
flake8 src/ --max-line-length=100

# Type check
mypy src/ --ignore-missing-imports

# Security scan
bandit -r src/ -ll

# Or use pre-commit to run all checks
pre-commit run --all-files
```

### Test Requirements
- All new features must include tests
- Tests must pass on Python 3.8-3.12
- Maintain or improve code coverage (current: 71%, target: 80%+)
- Tests should be fast (< 5 seconds per test)
- Use fixtures for common setup code

## Pull Request Process

1. Update documentation for any changed functionality
2. Add tests for new features
3. Ensure all tests pass
4. Update the README.md if needed
5. Submit your pull request with a clear description

## Code Review

All submissions require review. We use GitHub pull requests for this purpose. Expect:

- Feedback on code quality and design
- Requests for tests or documentation
- Suggestions for improvements

## Adding New Platforms

To add support for a new hardware platform:

1. Update `firmware/generator.py` with platform-specific code
2. Add platform templates if needed
3. Create example configurations
4. Update documentation
5. Add tests for the new platform

## Adding New Languages

To add a new SDK language:

1. Add language support in `software/generator.py`
2. Create appropriate templates
3. Add language-specific examples
4. Update documentation
5. Add tests

## Adding New UI Frameworks

To add UI framework support:

1. Implement generation logic in `ui/generator.py`
2. Create framework templates
3. Add example UI projects
4. Update documentation
5. Add tests

## Questions?

Feel free to open an issue for:
- Clarification on contribution process
- Discussion of major changes
- Help with development setup

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

Thank you for contributing to Accelerapp!
