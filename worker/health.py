#!/usr/bin/env python3
"""
Simple health check server for the worker service.
"""
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "healthy", "service": "worker", "message": "Worker service is running"}'
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start a simple health check server."""
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start health server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Health server stopped")
