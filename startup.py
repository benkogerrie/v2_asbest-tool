#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from urllib.parse import urlparse

def check_database_url():
    """Check if DATABASE_URL is properly set."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    if database_url.startswith('$shared.'):
        print("❌ DATABASE_URL is still using shared reference format")
        return False
    
    try:
        parsed = urlparse(database_url)
        if not parsed.hostname or not parsed.username or not parsed.password:
            print("❌ DATABASE_URL is incomplete")
            return False
        print("✅ DATABASE_URL looks valid")
        return True
    except Exception as e:
        print(f"❌ DATABASE_URL parsing error: {e}")
        return False

def run_migrations():
    """Run database migrations."""
    print("🔄 Running database migrations...")
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        print("✅ Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def start_app():
    """Start the FastAPI application."""
    print("🚀 Starting FastAPI application...")
    port = os.getenv('PORT', '8000')
    subprocess.run(['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', port])

if __name__ == "__main__":
    print("🔍 Checking database configuration...")
    
    # Wait a bit for Railway to set up environment
    time.sleep(2)
    
    if not check_database_url():
        print("❌ Database not ready, exiting...")
        sys.exit(1)
    
    if not run_migrations():
        print("❌ Failed to run migrations, exiting...")
        sys.exit(1)
    
    start_app()
