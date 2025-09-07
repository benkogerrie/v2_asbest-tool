import asyncio
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db, Base
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.auth.dependencies import get_current_system_owner

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    from sqlalchemy.ext.asyncio import create_async_engine
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_admin.db"
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    from sqlalchemy.orm import sessionmaker
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
def client(test_session):
    async def override_get_db():
        yield test_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
async def system_owner(test_session):
    user = User(
        id=uuid.uuid4(),
        email="system@test.nl",
        first_name="System",
        last_name="Owner",
        role=UserRole.SYSTEM_OWNER,
        tenant_id=None,
        is_active=True,
        is_superuser=True,
        is_verified=True,
        hashed_password="hashed_password"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
def auth_override(system_owner):
    def override_get_current_system_owner():
        return system_owner
    app.dependency_overrides[get_current_system_owner] = override_get_current_system_owner
    yield
    app.dependency_overrides.pop(get_current_system_owner, None)
