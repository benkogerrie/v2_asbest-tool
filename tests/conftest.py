"""
Test configuration and fixtures.
"""
import asyncio
import pytest
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.report import Report, ReportStatus


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
    # Check if user already exists
    existing_user = await test_session.execute(
        select(User).where(User.email == "test@user.com")
    )
    user = existing_user.scalar_one_or_none()
    
    if not user:
        user = User(
            email="test@user.com",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            tenant_id=test_tenant.id,
            is_active=True,
            is_superuser=False,
            is_verified=True,
            hashed_password="hashed_password_for_testing"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
    
    return user


@pytest.fixture
async def test_system_owner(test_session, test_tenant):
    """Create a test system owner user."""
    # Check if user already exists
    existing_user = await test_session.execute(
        select(User).where(User.email == "admin@system.com")
    )
    user = existing_user.scalar_one_or_none()
    
    if not user:
        user = User(
            email="admin@system.com",
            first_name="System",
            last_name="Owner",
            role=UserRole.SYSTEM_OWNER,
            tenant_id=test_tenant.id,
            is_active=True,
            is_superuser=True,
            is_verified=True,
            hashed_password="hashed_password_for_testing"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
    
    return user


@pytest.fixture
async def test_report(test_session, test_user):
    """Create a test report."""
    report = Report(
        tenant_id=test_user.tenant_id,  # Use the same tenant as test_user
        uploaded_by=test_user.id,
        filename="test_report.pdf",
        status=ReportStatus.DONE,
        finding_count=5,
        score=75.5,
        source_object_key="tenants/test/reports/test/source/test_report.pdf",
        conclusion_object_key=None
    )
    test_session.add(report)
    await test_session.commit()
    await test_session.refresh(report)
    return report


@pytest.fixture
async def test_reports_data(test_session, test_tenant, test_user):
    """Create multiple test reports for testing."""
    reports = []
    
    # Create different types of reports
    report_data = [
        ("report1.pdf", ReportStatus.DONE, 3, 85.2),
        ("report2.pdf", ReportStatus.PROCESSING, 0, None),
        ("report3.pdf", ReportStatus.FAILED, 0, None),
        ("report4.pdf", ReportStatus.DONE, 7, 92.1),
    ]
    
    for filename, status, finding_count, score in report_data:
        report = Report(
            tenant_id=test_tenant.id,  # Use the same tenant as test_user
            uploaded_by=test_user.id,
            filename=filename,
            status=status,
            finding_count=finding_count,
            score=score,
            source_object_key=f"tenants/test/reports/test/source/{filename}",
            conclusion_object_key=None
        )
        test_session.add(report)
        reports.append(report)
    
    await test_session.commit()
    
    # Refresh all reports
    for report in reports:
        await test_session.refresh(report)
    
    return reports
