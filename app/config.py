import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway compatibility
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/asbest_tool"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override database_url with environment variable if present
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            print(f"CONFIG: Environment DATABASE_URL found: {env_db_url}")
            # Convert postgresql:// to postgresql+asyncpg:// for async operations
            if env_db_url.startswith("postgresql://") and not env_db_url.startswith("postgresql+asyncpg://"):
                self.database_url = env_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                print(f"CONFIG: Converted to async URL: {self.database_url}")
            else:
                self.database_url = env_db_url
                print(f"CONFIG: Using URL as-is: {self.database_url}")
        else:
            print(f"CONFIG: No DATABASE_URL environment variable, using default: {self.database_url}")
    
    @property
    def database_url_sync(self) -> str:
        """Get database URL for sync operations (psycopg2)."""
        # Convert postgresql+asyncpg:// back to postgresql:// for sync operations
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return self.database_url
    
    # JWT
    secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_name: str = "Asbest Tool API"
    debug: bool = False
    
    # S3/MinIO Storage
    s3_endpoint: str = Field(default="https://ams3.digitaloceanspaces.com", env="S3_ENDPOINT")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_access_key_id: str = Field(default="", env="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="", env="S3_SECRET_ACCESS_KEY")
    s3_bucket: str = Field(default="asbest-tool", env="S3_BUCKET")
    s3_use_path_style: bool = Field(default=True, env="S3_USE_PATH_STYLE")
    s3_secure: bool = Field(default=True, env="S3_SECURE")
    
    # Upload limits
    max_upload_mb: int = Field(default=50, env="MAX_UPLOAD_MB")
    
    # Slice 6: Download and storage settings
    download_ttl: int = Field(default=3600, env="DOWNLOAD_TTL")  # 1 hour default
    purge_delay_days: int = Field(default=7, env="PURGE_DELAY_DAYS")  # 7 days before hard delete
    
    # Email notifications (Slice 6)
    smtp_host: str = Field(default="", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    from_email: str = Field(default="noreply@asbest-tool.com", env="FROM_EMAIL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    worker_concurrency: int = 1
    job_timeout_seconds: int = 120
    job_max_retries: int = 3
    
    # CORS Configuration
    cors_origins: Optional[str] = "https://v21-asbest-tool-nutv.vercel.app,http://localhost:3000,http://localhost:8080,*"
    
    # AI Configuration (Slice 8)
    ai_provider: str = Field(default="anthropic", env="AI_PROVIDER")
    ai_model: str = Field(default="claude-3-5-sonnet", env="AI_MODEL")
    ai_api_key: str = Field(default="", env="AI_API_KEY")
    ai_timeout: int = Field(default=60, env="AI_TIMEOUT")
    ai_max_tokens: int = Field(default=4000, env="AI_MAX_TOKENS")
    
    # Railway Port (for local testing compatibility)
    port: int = int(os.getenv("PORT", "8000"))
    
    # Force redeploy flag for AI API key
    force_redeploy: bool = Field(default=True, env="FORCE_REDEPLOY")
    
    model_config = {
        "env_file": ".env"
    }


settings = Settings()
