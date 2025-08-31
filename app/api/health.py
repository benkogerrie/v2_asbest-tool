from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": "2024-01-01T00:00:00Z"
    }
