import os
import time
from collections import defaultdict
from fastapi import HTTPException, Request, status

# In-memory request timestamp tracker per client IP
_client_requests: dict[str, list[float]] = defaultdict(list)

def get_rate_limit_config() -> tuple[int, int]:
    """Fetch rate limit settings from environment variables."""
    max_requests = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", "5"))
    window_seconds = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))
    return max_requests, window_seconds

def reset_rate_limits() -> None:
    """Reset in-memory rate limit store (used in testing)."""
    _client_requests.clear()

async def check_rate_limit(request: Request) -> None:
    """FastAPI dependency enforcing rate limiting per client IP."""
    max_requests, window_seconds = get_rate_limit_config()
    client_ip = request.client.host if request.client else '127.0.0.1'
    now = time.time()
    timestamps = _client_requests[client_ip]

    # Remove timestamps older than current window
    _client_requests[client_ip] = [t for t in timestamps if now - t < window_seconds]

    if len(_client_requests[client_ip]) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(window_seconds)},
        )

    _client_requests[client_ip].append(now)
