"""Error handling utilities for the Rotterdam Time Machine project.

This module provides utilities for consistent error handling and logging across
the application. It includes decorators for handling API errors and functions
for standardized error logging.

Example:
    >>> @handle_api_errors(default_return=None)
    ... def api_call():
    ...     # API call that might fail
    ...     pass
"""
import functools
import logging
from typing import Callable, TypeVar, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')

def handle_api_errors(default_return: Optional[T] = None) -> Callable:
    """Decorator for handling API errors in service methods.
    
    This decorator wraps service methods that make API calls, providing consistent
    error handling and logging. If an error occurs, it logs the error and returns
    a default value.
    
    Args:
        default_return: Value to return if an error occurs. Defaults to None.
        
    Returns:
        A decorator function that wraps the API call.
        
    Example:
        >>> @handle_api_errors(default_return=[])
        ... def get_data():
        ...     # API call that might fail
        ...     pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator

def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context.
    
    This function provides a standardized way to log errors with additional
    context information.
    
    Args:
        error: The exception that occurred.
        context: Additional context about where the error occurred.
            Defaults to an empty string.
            
    Example:
        >>> try:
        ...     # Some operation that might fail
        ...     pass
        ... except Exception as e:
        ...     log_error(e, "Database connection")
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg) 