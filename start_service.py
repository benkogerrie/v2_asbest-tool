#!/usr/bin/env python3
"""
Smart service starter that detects which service to run based on environment variables.
"""
import os
import sys
import subprocess

def main():
    """Start the appropriate service based on environment variables."""
    
    # Check if this is a worker service
    service_name = os.getenv("RAILWAY_SERVICE_NAME", "")
    service_type = os.getenv("SERVICE_TYPE", "")
    
    print(f"🔍 Service detection:")
    print(f"   RAILWAY_SERVICE_NAME: {service_name}")
    print(f"   SERVICE_TYPE: {service_type}")
    
    # Determine which service to start
    if "worker" in service_name.lower() or service_type == "worker":
        print("🚀 Starting WORKER service...")
        cmd = ["python", "-m", "worker.run"]
    else:
        print("🚀 Starting API service...")
        cmd = ["python", "startup.py"]
    
    print(f"   Command: {' '.join(cmd)}")
    
    # Start the service
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Service failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Service stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
