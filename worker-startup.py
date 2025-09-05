#!/usr/bin/env python3
"""
Worker startup script for Railway deployment.
"""
import os
import sys
import time
import subprocess
from urllib.parse import urlparse

def check_redis_url():
    """Check if REDIS_URL is properly set."""
    redis_url = os.getenv('REDIS_URL')
    print(f"🔍 REDIS_URL from environment: {redis_url}")
    
    if not redis_url:
        print("❌ REDIS_URL not set")
        return False
    
    try:
        parsed = urlparse(redis_url)
        print(f"🔍 Parsed Redis URL - Hostname: {parsed.hostname}, Port: {parsed.port}")
        if not parsed.hostname or not parsed.port:
            print("❌ REDIS_URL is incomplete")
            return False
        print("✅ REDIS_URL looks valid")
        return True
        
    except Exception as e:
        print(f"❌ REDIS_URL parsing error: {e}")
        return False

def start_worker():
    """Start the RQ worker."""
    print("🚀 Starting RQ worker...")
    subprocess.run(['python', '-m', 'worker.run'])

if __name__ == "__main__":
    print("🔍 Checking Redis configuration...")
    
    # Wait a bit for Railway to set up environment
    time.sleep(2)
    
    if not check_redis_url():
        print("❌ Redis not ready, exiting...")
        sys.exit(1)
    
    start_worker()
