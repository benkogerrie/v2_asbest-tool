"""
Queue connection and configuration for Redis and RQ.
"""
import redis
from rq import Queue
from app.config import settings


def redis_conn():
    """Get Redis connection."""
    try:
        conn = redis.from_url(settings.redis_url)
        # Test connection
        conn.ping()
        return conn
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to connect to Redis at {settings.redis_url}: {e}")
        raise


def reports_queue():
    """Get the reports processing queue."""
    return Queue(
        "reports", 
        connection=redis_conn(), 
        default_timeout=settings.job_timeout_seconds
    )
