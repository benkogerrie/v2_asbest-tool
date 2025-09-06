"""
RQ Worker runner for processing reports.
"""
import os
import logging
import time
import sys

# Add the parent directory to Python path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    
    # Start health server in background
    try:
        from worker.health import start_health_server
        import threading
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        logger.info("Health server started")
    except Exception as e:
        logger.warning(f"Failed to start health server: {e}")
    
    try:
        # Test imports first
        logger.info("Testing imports...")
        from app.config import settings
        logger.info("✅ Settings import successful")
        
        from app.queue.conn import redis_conn, reports_queue
        logger.info("✅ Queue imports successful")
        
        from app.queue.jobs import process_report
        logger.info("✅ Jobs import successful")
        
        from app.database import get_db_url
        logger.info("✅ Database imports successful")
        
        # Test database connection
        try:
            db_url = get_db_url()
            logger.info(f"✅ Database URL: {db_url[:50]}...")
        except Exception as e:
            logger.error(f"❌ Database URL failed: {e}")
            exit(1)
        
        # Test S3/Storage configuration
        try:
            from app.services.storage import storage
            logger.info("✅ Storage service import successful")
        except Exception as e:
            logger.error(f"❌ Storage service import failed: {e}")
            exit(1)
        
        # Wait for Redis to become available
        if not wait_for_redis():
            logger.error("Failed to connect to Redis, exiting...")
            exit(1)
        
        logger.info("Redis connection established, starting worker...")

        with Connection(redis_conn()):
            # Create worker for the reports queue
            worker = Worker([Queue("reports")])
            logger.info("Worker created, starting work...")
            
            # Start worker with health monitoring
            try:
                worker.work(with_scheduler=True)
            except KeyboardInterrupt:
                logger.info("Worker stopped by user")
            except Exception as e:
                logger.error(f"Worker error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                exit(1)
                
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        exit(1)
