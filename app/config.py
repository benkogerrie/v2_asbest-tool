import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway compatibility
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/asbest_tool"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
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
    redis_url: str = "redis://localhost:6379/0"
    worker_concurrency: int = 1
    job_timeout_seconds: int = 120
    job_max_retries: int = 3
    
    # CORS Configuration
    cors_origins: Optional[str] = "https://v21-asbest-tool-nutv.vercel.app,http://localhost:3000,http://localhost:8080,*"
    
    # Railway Port (for local testing compatibility)
    port: int = int(os.getenv("PORT", "8000"))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use DATABASE_URL as-is from environment (no conversion)
        if "DATABASE_URL" in os.environ:
            self.database_url = os.environ["DATABASE_URL"]
    
    class Config:
        env_file = ".env"
        # Map environment variables for Railway compatibility
        fields = {
            'secret_key': {'env': 'JWT_SECRET'},
            'database_url': {'env': 'DATABASE_URL'},
            'redis_url': {'env': 'REDIS_URL'}
        }


settings = Settings()
