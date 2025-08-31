"""
RQ Worker runner for processing reports.
"""
import os
import logging
from rq import Worker, Queue, Connection
from app.queue.conn import redis_conn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting RQ worker for report processing...")
    
    with Connection(redis_conn()):
        # Create worker for the reports queue
        worker = Worker([Queue("reports")])
        logger.info("Worker created, starting work...")
        worker.work(with_scheduler=True)
