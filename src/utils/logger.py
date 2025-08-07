"""Logging configuration for the application."""

import logging
import sys
from typing import Dict, Any
from config.config import config

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set log level
        log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent duplicate logs
        logger.propagate = False
    
    return logger

def log_request(logger: logging.Logger, method: str, path: str, params: Dict[str, Any] = None):
    """Log incoming request."""
    params_str = f" with params: {params}" if params else ""
    logger.info(f"Request: {method} {path}{params_str}")

def log_response(logger: logging.Logger, status_code: int, duration: float, result_count: int = None):
    """Log response details."""
    result_str = f" ({result_count} results)" if result_count is not None else ""
    logger.info(f"Response: {status_code} in {duration:.3f}s{result_str}")

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """Log error with context."""
    context_str = f" in {context}" if context else ""
    logger.error(f"Error{context_str}: {type(error).__name__}: {str(error)}")

def log_performance(logger: logging.Logger, operation: str, duration: float, details: Dict[str, Any] = None):
    """Log performance metrics."""
    details_str = f" - {details}" if details else ""
    logger.info(f"Performance - {operation}: {duration:.3f}s{details_str}")

# Configure third-party loggers
def configure_external_loggers():
    """Configure logging levels for external libraries."""
    external_loggers = {
        'splunklib': logging.WARNING,
        'openai': logging.WARNING,
        'httpx': logging.WARNING,
        'urllib3': logging.WARNING,
        'requests': logging.WARNING
    }
    
    for logger_name, level in external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

# Initialize external logger configuration
configure_external_loggers()
