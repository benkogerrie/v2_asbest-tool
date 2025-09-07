"""
Backend test configuration and fixtures voor Slice 6 tests.
"""
import os
import asyncio
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Jouw project imports
from app.main import app
from app.database import get_db, Base, get_async_session_local
from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.services.storage import storage
from app.auth.auth import fastapi_users

# Test settings
os.environ.setdefault("DOWNLOAD_TTL", "120")
os.environ.setdefault("PURGE_DELAY_DAYS", "7")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import event
    from sqlalchemy.schema import CreateTable
    
    # Use SQLite for testing with JSONB compatibility
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_slice6.db"
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # Create tables with JSONB compatibility for SQLite
    async with engine.begin() as conn:
        # Drop all tables first
        await conn.run_sync(Base.metadata.drop_all)
        
        # Create tables with JSONB mapped to TEXT for SQLite
        for table in Base.metadata.tables.values():
            # Replace JSONB with TEXT for SQLite compatibility
            for column in table.columns:
                if hasattr(column.type, 'python_type') and str(column.type).startswith('JSONB'):
                    column.type = column.type.__class__(astext_type=None)
        
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def client(test_session):
    """Create test client with database override."""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# ---- Fake auth context ----
@pytest.fixture
async def test_tenant(test_session):
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant Alpha",
        kvk="12345678",
        contact_email="test@tenant.com",
        is_active=True
    )
    test_session.add(tenant)
    await test_session.commit()
    await test_session.refresh(tenant)
    return tenant

@pytest.fixture
async def test_user(test_session, test_tenant):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        tenant_id=test_tenant.id,
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
        hashed_password="hashed_password_for_testing"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user, test_tenant):
    """Create auth headers for testing."""
    # Mock authentication by overriding the dependency
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[fastapi_users.current_user(active=True)] = override_get_current_user
    
    return {
        "Authorization": f"Bearer test-token-{test_user.id}",
        "X-Test-User": str(test_user.id),
        "X-Test-Tenant": str(test_tenant.id)
    }

# ---- Storage mock ----
class DummyStorage:
    """Mock storage service for testing."""
    def __init__(self):
        self.bucket = "test-bucket"
        self.objects = {}  # key -> bytes

    def upload_fileobj_with_checksum(self, fileobj, object_key: str, content_type: str):
        """Mock upload with checksum calculation."""
        fileobj.seek(0)
        data = fileobj.read()
        file_size = len(data)
        
        import hashlib
        checksum = hashlib.sha256(data).hexdigest()
        
        self.objects[object_key] = data
        
        return True, checksum, file_size

    def presigned_get_url(self, object_key: str, expires: int) -> str:
        """Generate mock presigned URL."""
        if object_key not in self.objects:
            raise FileNotFoundError(f"Object {object_key} not found")
        return f"https://presigned.test/{object_key}?exp={expires}"

    def delete_object(self, object_key: str):
        """Delete mock object."""
        self.objects.pop(object_key, None)

@pytest.fixture
def mock_storage(monkeypatch):
    """Mock storage service."""
    dummy_storage = DummyStorage()
    
    # Patch storage service
    monkeypatch.setattr("app.services.storage.storage", dummy_storage, raising=False)
    monkeypatch.setattr("app.api.reports.storage", dummy_storage, raising=False)
    monkeypatch.setattr("app.queue.jobs.storage", dummy_storage, raising=False)
    
    return dummy_storage

# Helper om een report record te maken
@pytest.fixture
def make_report(test_session, test_tenant, test_user):
    """Helper to create test reports."""
    async def _make(
        id=None,
        tenant_id=None,
        uploaded_by=None,
        filename="Test.pdf",
        status=ReportStatus.PENDING,
        storage_key=None,
        checksum=None,
        file_size=None,
        finding_count=0,
        score=0,
        deleted_at=None,
        error_message=None,
    ):
        if id is None:
            id = uuid.uuid4()
        if tenant_id is None:
            tenant_id = test_tenant.id
        if uploaded_by is None:
            uploaded_by = test_user.id
            
        report = Report(
            id=id,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            filename=filename,
            status=status,
            storage_key=storage_key,
            checksum=checksum,
            file_size=file_size,
            finding_count=finding_count,
            score=score,
            deleted_at=deleted_at,
            error_message=error_message,
            uploaded_at=datetime.now(timezone.utc),
        )
        test_session.add(report)
        await test_session.commit()
        await test_session.refresh(report)
        return report
    return _make
