""
Retry utilities with exponential backoff and jitter.
"""
import random
import time
from functools import wraps
from typing import Callable, Type, TypeVar, Any, Optional, Union, List, Tuple, Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState,
    Retrying,
    retry_any,
    retry_if_exception
)
from tenacity.stop import stop_base
from tenacity.wait import wait_base
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
P = TypeVar('P')
R = TypeVar('R')

def retry_with_backoff(
    retries: int = 3,
    min_wait: float = 1,
    max_wait: float = 60,
    exponential_base: float = 2,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_retries: bool = True,
):
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        retries: Maximum number of retries
        min_wait: Minimum seconds to wait between retries
        max_wait: Maximum seconds to wait between retries
        exponential_base: Base for exponential backoff
        jitter: Whether to add jitter to wait times
        exceptions: Exception(s) to catch and retry on
        log_retries: Whether to log retry attempts
        
    Returns:
        Decorator that applies retry logic to the decorated function
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        break
                        
                    # Calculate wait time with exponential backoff
                    wait = min(
                        max_wait,
                        min_wait * (exponential_base ** attempt)
                    )
                    
                    # Add jitter
                    if jitter:
                        wait = random.uniform(0, wait)
                    
                    if log_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {wait:.2f} seconds..."
                        )
                    
                    time.sleep(wait)
            
            # If we get here, all retries failed
            raise last_exception if last_exception else Exception("Unknown error in retry")
        return wrapper
    return decorator

def async_retry_with_backoff(
    retries: int = 3,
    min_wait: float = 1,
    max_wait: float = 60,
    exponential_base: float = 2,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_retries: bool = True,
):
    """
    Async version of retry_with_backoff for async functions.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None
            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        break
                        
                    # Calculate wait time with exponential backoff
                    wait = min(
                        max_wait,
                        min_wait * (exponential_base ** attempt)
                    )
                    
                    # Add jitter
                    if jitter:
                        wait = random.uniform(0, wait)
                    
                    if log_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {wait:.2f} seconds..."
                        )
                    
                    import asyncio
                    await asyncio.sleep(wait)
            
            # If we get here, all retries failed
            raise last_exception if last_exception else Exception("Unknown error in retry")
        return wrapper
    return decorator

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        retries: int = 3,
        min_wait: float = 1,
        max_wait: float = 60,
        exponential_base: float = 2,
        jitter: bool = True,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        log_retries: bool = True,
    ):
        self.retries = retries
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions
        self.log_retries = log_retries
    
    def get_retry_decorator(self, is_async: bool = False):
        """Get the appropriate retry decorator based on sync/async context."""
        if is_async:
            return async_retry_with_backoff(
                retries=self.retries,
                min_wait=self.min_wait,
                max_wait=self.max_wait,
                exponential_base=self.exponential_base,
                jitter=self.jitter,
                exceptions=self.exceptions,
                log_retries=self.log_retries,
            )
        return retry_with_backoff(
            retries=self.retries,
            min_wait=self.min_wait,
            max_wait=self.max_wait,
            exponential_base=self.exponential_base,
            jitter=self.jitter,
            exceptions=self.exceptions,
            log_retries=self.log_retries,
        )

# Common retry configurations
DATABASE_RETRY_CONFIG = RetryConfig(
    retries=5,
    min_wait=0.1,
    max_wait=10,
    exceptions=(sqlite3.OperationalError, sqlite3.InterfaceError)
)

HTTP_RETRY_CONFIG = RetryConfig(
    retries=3,
    min_wait=1,
    max_wait=10,
    exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
)

REGULATORY_FETCH_RETRY_CONFIG = RetryConfig(
    retries=5,
    min_wait=2,
    max_wait=30,
    exceptions=(Exception,),  # Broad exception handling for network issues
    log_retries=True
)
