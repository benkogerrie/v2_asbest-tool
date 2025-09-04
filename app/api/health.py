from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Health check endpoint with extensive debug logging."""
    import datetime
    import os
    import traceback
    from app.database import get_db, get_engine
    from app.queue.conn import redis_conn
    from app.config import settings
    
    health_status = {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "redis": "unknown"
        },
        "debug": {
            "environment": {},
            "database_config": {},
            "redis_config": {},
            "errors": []
        }
    }
    
    # Debug: Environment variables
    health_status["debug"]["environment"] = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "NOT_SET"),
        "REDIS_URL": os.getenv("REDIS_URL", "NOT_SET"),
        "PORT": os.getenv("PORT", "NOT_SET"),
        "PYTHONPATH": os.getenv("PYTHONPATH", "NOT_SET")
    }
    
    # Debug: Database configuration
    health_status["debug"]["database_config"] = {
        "database_url": settings.database_url,
        "engine_created": get_engine() is not None
    }
    
    # Debug: Redis configuration
    health_status["debug"]["redis_config"] = {
        "redis_url": settings.redis_url
    }
    
    # Check database connection with extensive logging
    print("🔍 HEALTHCHECK: Starting database check...")
    try:
        print(f"🔍 HEALTHCHECK: Database URL: {settings.database_url}")
        print(f"🔍 HEALTHCHECK: Engine created: {get_engine() is not None}")
        
        from sqlalchemy import text
        print("🔍 HEALTHCHECK: Getting database session...")
        
        async for session in get_db():
            print("🔍 HEALTHCHECK: Database session obtained")
            print("🔍 HEALTHCHECK: Executing test query...")
            
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"🔍 HEALTHCHECK: Test query result: {test_value}")
            
            # Test table existence
            print("🔍 HEALTHCHECK: Checking if tables exist...")
            tables_result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5
            """))
            tables = [row[0] for row in tables_result.fetchall()]
            print(f"🔍 HEALTHCHECK: Found tables: {tables}")
            
            health_status["checks"]["database"] = "healthy"
            health_status["debug"]["database_config"]["tables_found"] = tables
            break
            
    except Exception as e:
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        print(f"❌ HEALTHCHECK: Database error: {error_msg}")
        print(f"❌ HEALTHCHECK: Full traceback: {error_traceback}")
        
        health_status["checks"]["database"] = f"unhealthy: {error_msg}"
        health_status["status"] = "degraded"
        health_status["debug"]["errors"].append({
            "type": "database",
            "message": error_msg,
            "traceback": error_traceback
        })
    
    # Check Redis connection with extensive logging
    print("🔍 HEALTHCHECK: Starting Redis check...")
    try:
        print(f"🔍 HEALTHCHECK: Redis URL: {settings.redis_url}")
        
        conn = redis_conn()
        print("🔍 HEALTHCHECK: Redis connection object created")
        
        ping_result = conn.ping()
        print(f"🔍 HEALTHCHECK: Redis ping result: {ping_result}")
        
        # Test Redis operations
        test_key = "healthcheck_test"
        conn.set(test_key, "test_value", ex=10)
        test_value = conn.get(test_key)
        conn.delete(test_key)
        print(f"🔍 HEALTHCHECK: Redis test operations successful: {test_value}")
        
        health_status["checks"]["redis"] = "healthy"
        
    except Exception as e:
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        print(f"❌ HEALTHCHECK: Redis error: {error_msg}")
        print(f"❌ HEALTHCHECK: Full traceback: {error_traceback}")
        
        health_status["checks"]["redis"] = f"unhealthy: {error_msg}"
        health_status["status"] = "degraded"
        health_status["debug"]["errors"].append({
            "type": "redis",
            "message": error_msg,
            "traceback": error_traceback
        })
    
    print(f"🔍 HEALTHCHECK: Final status: {health_status['status']}")
    return health_status

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asbest Tool API",
        "version": "1.0.0",
        "docs": "/docs"
    }
