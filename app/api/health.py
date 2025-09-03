from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    import datetime
    from app.database import get_db
    from app.queue.conn import redis_conn
    
    health_status = {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database connection
    try:
        from sqlalchemy import text
        async for session in get_db():
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            health_status["checks"]["database"] = "healthy"
            break
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connection
    try:
        redis_conn().ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Overall status
    if health_status["status"] == "degraded":
        return health_status
    else:
        return health_status

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asbest Tool API",
        "version": "1.0.0",
        "docs": "/docs"
    }
