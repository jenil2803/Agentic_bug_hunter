"""
Rate limiter utility to manage API calls
"""
import time
from functools import wraps
from common.config import MAX_REQUESTS_PER_MINUTE
from common.logger import get_logger

logger = get_logger("rate_limiter")

class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_MINUTE, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_proceed(self) -> bool:
        """Check if a request can proceed"""
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        while not self.can_proceed():
            sleep_time = 1
            time.sleep(sleep_time)


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limited(func):
    """Decorator to rate limit function calls"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        rate_limiter.wait_if_needed()
        return await func(*args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        rate_limiter.wait_if_needed()
        return func(*args, **kwargs)
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
