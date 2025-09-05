from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Simple health check endpoint."""
    import datetime
    
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asbest Tool API",
        "version": "1.0.0",
        "docs": "/docs"
    }
