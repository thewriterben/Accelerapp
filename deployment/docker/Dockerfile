# Accelerapp Air-Gapped Deployment Dockerfile
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY MANIFEST.in .
COPY README.md .

# Install application
RUN pip install --no-cache-dir -e .

# Create directories for models and cache
RUN mkdir -p /app/models /app/cache /app/output

# Expose port for monitoring
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import accelerapp; print('healthy')" || exit 1

# Default command
CMD ["accelerapp", "info"]


# Development stage with additional tools
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy tests
COPY tests/ ./tests/

CMD ["bash"]


# Production stage - minimal image
FROM base as production

# Remove unnecessary files
RUN find /usr/local/lib/python3.11/site-packages -type d -name "tests" -exec rm -rf {} + || true
RUN find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + || true

# Run as non-root user
RUN useradd -m -u 1000 accelerapp && \
    chown -R accelerapp:accelerapp /app
USER accelerapp

CMD ["accelerapp", "info"]
