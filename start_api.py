#!/usr/bin/env python3
"""
Start script for Railway deployment.
Handles PORT environment variable correctly.
"""
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment variable with fallback
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting API server on port {port}")
    
    # Start uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
