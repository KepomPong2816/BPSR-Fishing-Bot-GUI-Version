import time
import functools
from typing import Callable, TypeVar, Optional

T = TypeVar('T')


class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0, exponential: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self._last_retry_count = 0

    def execute(self, func: Callable[[], T], success_check: Callable[[T], bool] = None, on_retry: Callable[[int, float], None] = None) -> Optional[T]:
        self._last_retry_count = 0
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func()
                
                if success_check is None or success_check(result):
                    return result
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    self._last_retry_count = attempt + 1
                    
                    if on_retry:
                        on_retry(attempt + 1, delay)
                    
                    time.sleep(delay)
                    
            except Exception as e:
                if attempt >= self.max_retries:
                    raise
                
                delay = self._calculate_delay(attempt)
                self._last_retry_count = attempt + 1
                
                if on_retry:
                    on_retry(attempt + 1, delay)
                
                time.sleep(delay)
        
        return None

    def _calculate_delay(self, attempt: int) -> float:
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay
        
        return min(delay, self.max_delay)

    def get_last_retry_count(self) -> int:
        return self._last_retry_count


def with_retry(max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = RetryHandler(max_retries, base_delay, max_delay)
            return handler.execute(lambda: func(*args, **kwargs))
        return wrapper
    return decorator
