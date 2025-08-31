"""
RQ Worker runner for processing reports.
"""
import os
import logging
import time
import sys
from rq import Worker, Queue, Connection
from app.queue.conn import redis_conn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_redis(max_retries=30, retry_delay=2):
    """Wait for Redis to become available."""
    logger.info("Waiting for Redis connection...")
    
    for attempt in range(max_retries):
        try:
            # Test Redis connection
            conn = redis_conn()
            conn.ping()
            logger.info("Redis connection established successfully!")
            return True
        except Exception as e:
            logger.warning(f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to Redis after all retries")
                return False
    
    return False


if __name__ == "__main__":
    logger.info("Starting RQ worker for report processing...")
    
    # Wait for Redis to be available
    if not wait_for_redis():
        logger.error("Cannot start worker without Redis connection")
        sys.exit(1)
    
    try:
        with Connection(redis_conn()):
            # Create worker for the reports queue
            worker = Worker([Queue("reports")])
            logger.info("Worker created, starting work...")
            worker.work(with_scheduler=True)
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)
