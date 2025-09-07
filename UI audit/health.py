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

@router.get("/healthz/storage")
async def health_check_storage():
    """Storage health check endpoint."""
    import datetime
    from app.config import settings
    from app.services.storage import storage
    
    try:
        # Test storage connection
        bucket_exists = storage.ensure_bucket()
        
        return {
            "status": "healthy" if bucket_exists else "degraded",
            "message": "Storage check completed",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "storage": {
                "endpoint": settings.s3_endpoint,
                "bucket": settings.s3_bucket,
                "region": "us-east-1",  # DO Spaces uses us-east-1 for boto3
                "bucket_exists": bucket_exists
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Storage check failed: {str(e)}",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "storage": {
                "endpoint": settings.s3_endpoint,
                "bucket": settings.s3_bucket,
                "region": "us-east-1",  # DO Spaces uses us-east-1 for boto3
                "error": str(e)
            }
        }

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asbest Tool API",
        "version": "1.0.0",
        "docs": "/docs"
    }
