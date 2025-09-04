import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway compatibility
    database_url_raw: str = Field(default="postgresql+asyncpg://postgres:password@localhost:5432/asbest_tool", env="DATABASE_URL")
    
    @property
    def database_url(self) -> str:
        """Get database URL, converting to async version if needed."""
        db_url = self.database_url_raw
        # Convert postgresql:// to postgresql+asyncpg:// for async operations
        if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return db_url
    
    @property
    def database_url_sync(self) -> str:
        """Get database URL for sync operations (psycopg2)."""
        db_url = self.database_url_raw
        # Convert postgresql+asyncpg:// back to postgresql:// for sync operations
        if db_url.startswith("postgresql+asyncpg://"):
            return db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return db_url
    
    # JWT
    secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_name: str = "Asbest Tool API"
    debug: bool = False
    
    # S3/MinIO Storage
    s3_endpoint: str = "http://localhost:9000"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket: str = "asbesttool-dev"
    s3_use_path_style: bool = True
    s3_secure: bool = False
    
    # Upload limits
    max_upload_mb: int = 50
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    worker_concurrency: int = 1
    job_timeout_seconds: int = 120
    job_max_retries: int = 3
    
    # CORS Configuration
    cors_origins: Optional[str] = "https://v21-asbest-tool-nutv.vercel.app,http://localhost:3000,http://localhost:8080,*"
    
    # Railway Port (for local testing compatibility)
    port: int = int(os.getenv("PORT", "8000"))
    
    model_config = {
        "env_file": ".env"
    }


settings = Settings()
