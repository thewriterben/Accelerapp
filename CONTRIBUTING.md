# Contributing to Accelerapp

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

- Follow PEP 8 style guidelines for Python code
- Add docstrings to all classes and functions
- Include type hints where appropriate
- Write unit tests for new functionality
- Keep changes focused and atomic

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=accelerapp tests/
```

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
