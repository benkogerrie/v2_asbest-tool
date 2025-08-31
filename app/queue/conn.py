"""
Queue connection and configuration for Redis and RQ.
"""
import redis
from rq import Queue
from app.config import settings


def redis_conn():
    """Get Redis connection."""
    return redis.from_url(settings.redis_url)


def reports_queue():
    """Get the reports processing queue."""
    return Queue(
        "reports", 
        connection=redis_conn(), 
        default_timeout=settings.job_timeout_seconds
    )
