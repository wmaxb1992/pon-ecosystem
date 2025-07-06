#!/usr/bin/env python3
"""
Grok API Rate Limiter for Multi-Worker System
============================================
Manages API rate limits across multiple workers using a single key
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from collections import deque
from contextlib import asynccontextmanager

class GrokAPIRateLimiter:
    """
    Centralized rate limiter for Grok API across all workers
    """
    
    def __init__(self, requests_per_minute=100, requests_per_hour=3000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Track requests in time windows
        self.minute_requests = deque()
        self.hour_requests = deque()
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Backoff strategy
        self.backoff_time = 1.0
        self.max_backoff = 60.0
        
        self.logger = logging.getLogger(__name__)
    
    async def _cleanup_old_requests(self):
        """Remove requests outside time windows"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Clean minute window
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()
            
        # Clean hour window  
        while self.hour_requests and self.hour_requests[0] < hour_ago:
            self.hour_requests.popleft()
    
    async def _calculate_wait_time(self):
        """Calculate how long to wait before next request"""
        await self._cleanup_old_requests()
        
        now = time.time()
        wait_time = 0
        
        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            oldest_in_minute = self.minute_requests[0]
            wait_time = max(wait_time, oldest_in_minute + 60 - now)
        
        # Check hour limit
        if len(self.hour_requests) >= self.requests_per_hour:
            oldest_in_hour = self.hour_requests[0]
            wait_time = max(wait_time, oldest_in_hour + 3600 - now)
            
        return wait_time
    
    @asynccontextmanager
    async def acquire(self):
        """
        Acquire permission to make API request
        Usage:
            async with rate_limiter.acquire():
                response = await grok_api_call()
        """
        async with self._lock:
            wait_time = await self._calculate_wait_time()
            
            if wait_time > 0:
                self.logger.info(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            
            # Record this request
            now = time.time()
            self.minute_requests.append(now)
            self.hour_requests.append(now)
            
        try:
            yield
            # Reset backoff on success
            self.backoff_time = 1.0
        except Exception as e:
            # Exponential backoff on error
            if "rate limit" in str(e).lower():
                self.backoff_time = min(self.backoff_time * 2, self.max_backoff)
                self.logger.warning(f"Rate limited, backing off {self.backoff_time}s")
                await asyncio.sleep(self.backoff_time)
            raise
    
    def get_stats(self):
        """Get current rate limit stats"""
        return {
            "requests_last_minute": len(self.minute_requests),
            "requests_last_hour": len(self.hour_requests),
            "minute_limit": self.requests_per_minute,
            "hour_limit": self.requests_per_hour,
            "current_backoff": self.backoff_time
        }

# Global rate limiter instance
_global_rate_limiter = None

def get_rate_limiter():
    """Get the global rate limiter instance"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = GrokAPIRateLimiter()
    return _global_rate_limiter

# Example usage in workers:
async def safe_grok_request(prompt, **kwargs):
    """
    Make a rate-limited Grok API request
    """
    rate_limiter = get_rate_limiter()
    
    async with rate_limiter.acquire():
        # Your existing Grok API call here
        # response = await grok_client.chat(prompt, **kwargs)
        # return response
        pass

if __name__ == "__main__":
    # Test the rate limiter
    async def test_rate_limiter():
        limiter = GrokAPIRateLimiter(requests_per_minute=5)  # Lower for testing
        
        for i in range(10):
            async with limiter.acquire():
                print(f"Request {i+1} at {datetime.now()}")
                await asyncio.sleep(0.1)  # Simulate API call
            
            stats = limiter.get_stats()
            print(f"Stats: {stats}")
    
    asyncio.run(test_rate_limiter())
