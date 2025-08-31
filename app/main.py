from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api import health
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# Add CORS middleware
def get_cors_origins():
    """Get CORS origins with fallback to wildcard."""
    if not settings.cors_origins:
        return ["*"]
    
    origins = [origin.strip() for origin in settings.cors_origins.split(",")]
    # If "*" is in the list, return wildcard
    if "*" in origins:
        return ["*"]
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only health router for now
app.include_router(health.router)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asbest Tool API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "starting up - database connection pending"
    }

@app.get("/auth/jwt/login")
async def login_placeholder():
    """Placeholder login endpoint."""
    return {
        "message": "Login endpoint placeholder - database connection required",
        "status": "service starting up"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
