import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.auth.auth import get_user_manager


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Setup test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Get test database session."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Get test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def system_owner(db_session):
    """Create a system owner user."""
    user_manager = await anext(get_user_manager(db_session))
    
    system_owner_data = {
        "email": "system@test.nl",
        "password": "SystemOwner123!",
        "first_name": "System",
        "last_name": "Owner",
        "role": UserRole.SYSTEM_OWNER,
        "tenant_id": None,
        "is_active": True,
        "is_superuser": True,
        "is_verified": True
    }
    
    user = await user_manager.create(system_owner_data)
    return user


@pytest.fixture
async def tenant(db_session):
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Bedrijf",
        kvk="87654321",
        contact_email="admin@testbedrijf.nl",
        is_active=True
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def tenant_admin(db_session, tenant):
    """Create a tenant admin user."""
    user_manager = await anext(get_user_manager(db_session))
    
    tenant_admin_data = {
        "email": "admin@testbedrijf.nl",
        "password": "Admin123!",
        "first_name": "Admin",
        "last_name": "Test",
        "role": UserRole.ADMIN,
        "tenant_id": tenant.id,
        "is_active": True,
        "is_superuser": False,
        "is_verified": True
    }
    
    user = await user_manager.create(tenant_admin_data)
    return user


@pytest.fixture
async def tenant_user(db_session, tenant):
    """Create a regular tenant user."""
    user_manager = await anext(get_user_manager(db_session))
    
    tenant_user_data = {
        "email": "user@testbedrijf.nl",
        "password": "User123!",
        "first_name": "User",
        "last_name": "Test",
        "role": UserRole.USER,
        "tenant_id": tenant.id,
        "is_active": True,
        "is_superuser": False,
        "is_verified": True
    }
    
    user = await user_manager.create(tenant_user_data)
    return user
