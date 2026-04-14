import time
from fastapi import HTTPException, status, Request
from redis import Redis
from app.core.config import settings
from app.core.logger import logger

class RateLimiter:
    """
    Redis-based rate limiter.
    """
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=1,  # Use a different DB for rate limiting
            decode_responses=True
        )

    def is_rate_limited(self, key: str, limit: int = 10, window: int = 60) -> bool:
        """
        Check if a key (IP or User ID) has exceeded the rate limit.
        limit: Max requests
        window: Time window in seconds
        """
        try:
            current_time = int(time.time())
            pipe = self.redis.pipeline()
            
            # Use a sorted set to store timestamps of requests
            redis_key = f"rate_limit:{key}"
            
            # Remove timestamps older than the window
            pipe.zremrangebyscore(redis_key, 0, current_time - window)
            # Add current timestamp
            pipe.zadd(redis_key, {str(current_time): current_time})
            # Count elements in the window
            pipe.zcard(redis_key)
            # Set expiry on the key to clean up
            pipe.expire(redis_key, window)
            
            results = pipe.execute()
            request_count = results[2]
            
            return request_count > limit
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            return False  # Fail open in case of Redis issues

rate_limiter = RateLimiter()

def rate_limit(limit: int = 10, window: int = 60):
    """
    Dependency for rate limiting.
    """
    async def dependency(request: Request):
        # Use IP address as default identifier
        client_ip = request.client.host
        if rate_limiter.is_rate_limited(client_ip, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
    return dependency
