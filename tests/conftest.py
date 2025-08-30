"""
Test configuration and fixtures.
"""
import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.tenant import Tenant


# Test database URL - using SQLite for isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_session):
    """Create test client."""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_dependencies():
    """Mock authentication dependencies for testing."""
    from app.auth.dependencies import get_current_active_user, get_current_admin_or_system_owner
    
    async def mock_get_current_active_user():
        # This will be overridden in individual tests
        pass
    
    async def mock_get_current_admin_or_system_owner():
        # This will be overridden in individual tests
        pass
    
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    app.dependency_overrides[get_current_admin_or_system_owner] = mock_get_current_admin_or_system_owner
    
    yield
    
    # Clean up
    app.dependency_overrides.pop(get_current_active_user, None)
    app.dependency_overrides.pop(get_current_admin_or_system_owner, None)


@pytest.fixture
async def test_tenant(test_session):
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Tenant",
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
        email="test@user.com",
        first_name="Test",
        last_name="User",
        role="USER",
        tenant_id=test_tenant.id,
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user
