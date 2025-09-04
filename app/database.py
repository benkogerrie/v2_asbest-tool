from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from typing import Optional

from app.config import settings

# Base class for models
Base = declarative_base()

# Lazy initialization
_engine: Optional[object] = None
_AsyncSessionLocal: Optional[object] = None


def get_engine():
    """Get database engine, creating it if necessary."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            poolclass=NullPool,
        )
    return _engine


def get_async_session_local():
    """Get session factory, creating it if necessary."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with get_async_session_local()() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db_url() -> str:
    """Get database URL for sync operations (used by RQ worker)."""
    return settings.database_url_sync
