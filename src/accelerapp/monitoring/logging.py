"""
Structured logging for Accelerapp.
Provides JSON-based logging with correlation IDs.
"""

import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """Formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class CorrelationAdapter(logging.LoggerAdapter):
    """Logger adapter that adds correlation IDs to log records."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add correlation ID.

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Processed message and kwargs
        """
        extra = kwargs.get("extra", {})

        # Add correlation ID if not present
        if "correlation_id" not in extra:
            extra["correlation_id"] = self.extra.get("correlation_id")

        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    level: str = "INFO",
    structured: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Setup application logging.

    Args:
        level: Logging level
        structured: Use structured JSON logging
        log_file: Optional log file path
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(
    name: str,
    correlation_id: Optional[str] = None,
    **extra_fields,
) -> logging.Logger:
    """
    Get a logger with optional correlation ID.

    Args:
        name: Logger name
        correlation_id: Correlation ID for tracking requests
        **extra_fields: Additional fields to include in all log messages

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    if correlation_id or extra_fields:
        extra = {"correlation_id": correlation_id or str(uuid.uuid4())}
        if extra_fields:
            extra["extra_fields"] = extra_fields
        return CorrelationAdapter(logger, extra)

    return logger


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID.

    Returns:
        Correlation ID string
    """
    return str(uuid.uuid4())
