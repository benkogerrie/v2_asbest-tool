import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api import health, tenants, users, reports, analyses, findings, debug
from app.auth.auth import fastapi_users, auth_backend
from app.models.user import User
from app.schemas.user import UserRead, UserCreate
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

# Include routers
app.include_router(health.router)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(analyses.router)
app.include_router(findings.router)
app.include_router(debug.router)

# Include FastAPI Users routes
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])

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
        "docs": "/docs"
    }





if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
