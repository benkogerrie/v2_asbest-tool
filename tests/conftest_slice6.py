"""
Pytest configuration and fixtures for Slice 6 tests.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User, UserRole
from app.models.tenant import Tenant


@pytest.fixture(scope="session")
def test_tenant_alpha():
    """Test tenant Alpha for isolation testing."""
    return Tenant(
        id=uuid.uuid4(),
        name="Alpha Tenant",
        created_at=datetime.utcnow()
    )


@pytest.fixture(scope="session")
def test_tenant_beta():
    """Test tenant Beta for isolation testing."""
    return Tenant(
        id=uuid.uuid4(),
        name="Beta Tenant",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def alpha_uploader(test_tenant_alpha):
    """User who uploads reports in Alpha tenant."""
    return User(
        id=uuid.uuid4(),
        email="uploader@alpha.com",
        tenant_id=test_tenant_alpha.id,
        first_name="Alpha",
        last_name="Uploader",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def alpha_viewer(test_tenant_alpha):
    """User who views reports in Alpha tenant."""
    return User(
        id=uuid.uuid4(),
        email="viewer@alpha.com",
        tenant_id=test_tenant_alpha.id,
        first_name="Alpha",
        last_name="Viewer",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def beta_outsider(test_tenant_beta):
    """User from different tenant (Beta) for isolation testing."""
    return User(
        id=uuid.uuid4(),
        email="outsider@beta.com",
        tenant_id=test_tenant_beta.id,
        first_name="Beta",
        last_name="Outsider",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def r_done(test_tenant_alpha, alpha_uploader):
    """Report in DONE status with existing object in Spaces."""
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant_alpha.id,
        uploaded_by=alpha_uploader.id,
        filename="R_DONE.pdf",
        status=ReportStatus.DONE,
        score=85.5,
        finding_count=3,
        storage_key="tenants/alpha/reports/r_done/output.pdf",
        checksum="abc123def456",
        file_size=1024000,
        summary="Test analysis completed successfully",
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/alpha/reports/r_done/source/R_DONE.pdf"
    )


@pytest.fixture
def r_proc(test_tenant_alpha, alpha_uploader):
    """Report in PROCESSING status."""
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant_alpha.id,
        uploaded_by=alpha_uploader.id,
        filename="R_PROC.pdf",
        status=ReportStatus.PROCESSING,
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/alpha/reports/r_proc/source/R_PROC.pdf"
    )


@pytest.fixture
def r_fail(test_tenant_alpha, alpha_uploader):
    """Report in FAILED status with error message."""
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant_alpha.id,
        uploaded_by=alpha_uploader.id,
        filename="R_FAIL.pdf",
        status=ReportStatus.FAILED,
        error_message="PDF processing failed due to corrupted file format",
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/alpha/reports/r_fail/source/R_FAIL.pdf"
    )


@pytest.fixture
def r_del(test_tenant_alpha, alpha_uploader):
    """Report that has been soft deleted."""
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant_alpha.id,
        uploaded_by=alpha_uploader.id,
        filename="R_DEL.pdf",
        status=ReportStatus.DONE,
        deleted_at=datetime.utcnow(),
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/alpha/reports/r_del/source/R_DEL.pdf"
    )


@pytest.fixture
def r_beta(test_tenant_beta, beta_outsider):
    """Report in Beta tenant for isolation testing."""
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant_beta.id,
        uploaded_by=beta_outsider.id,
        filename="R_BETA.pdf",
        status=ReportStatus.DONE,
        score=92.0,
        finding_count=1,
        storage_key="tenants/beta/reports/r_beta/output.pdf",
        checksum="def456ghi789",
        file_size=2048000,
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/beta/reports/r_beta/source/R_BETA.pdf"
    )


@pytest.fixture
def mock_storage_service():
    """Mock storage service for testing."""
    with patch('app.services.storage.storage') as mock_storage:
        mock_storage.presigned_get_url.return_value = "https://test.example.com/presigned-url"
        mock_storage.upload_fileobj_with_checksum.return_value = (True, "test-checksum", 1024)
        mock_storage.delete_object.return_value = True
        yield mock_storage


@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    with patch('app.services.email.email_service') as mock_email:
        mock_email.send_report_completion_notification.return_value = True
        mock_email.is_configured.return_value = True
        yield mock_email


@pytest.fixture
def mock_report_service():
    """Mock report service for testing."""
    with patch('app.api.reports.ReportService') as mock_service:
        mock_service.return_value.get_report_for_download.return_value = None
        mock_service.return_value.get_reports_for_user.return_value = []
        yield mock_service


@pytest.fixture
def test_database_session():
    """Mock database session for testing."""
    with patch('app.database.get_db') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value.__aenter__.return_value = mock_session
        yield mock_session


# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "frontend: Frontend tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


# Test data fixtures for different scenarios
@pytest.fixture
def slice6_test_data(r_done, r_proc, r_fail, r_del, r_beta):
    """Complete test dataset for Slice 6 testing."""
    return {
        'reports': {
            'r_done': r_done,
            'r_proc': r_proc,
            'r_fail': r_fail,
            'r_del': r_del,
            'r_beta': r_beta
        },
        'expected_behavior': {
            'downloadable': ['r_done'],
            'not_downloadable': ['r_proc', 'r_fail', 'r_del'],
            'tenant_alpha': ['r_done', 'r_proc', 'r_fail', 'r_del'],
            'tenant_beta': ['r_beta']
        }
    }


# Performance test fixtures
@pytest.fixture
def large_report_list(test_tenant_alpha, alpha_uploader):
    """Generate large list of reports for performance testing."""
    reports = []
    for i in range(1000):
        report = Report(
            id=uuid.uuid4(),
            tenant_id=test_tenant_alpha.id,
            uploaded_by=alpha_uploader.id,
            filename=f"report_{i:04d}.pdf",
            status=ReportStatus.DONE,
            score=float(i % 100),
            finding_count=i % 10,
            uploaded_at=datetime.utcnow(),
            source_object_key=f"tenants/alpha/reports/report_{i}/source/report_{i:04d}.pdf"
        )
        reports.append(report)
    return reports


# Security test fixtures
@pytest.fixture
def malicious_report_data():
    """Malicious report data for security testing."""
    return {
        'filename': '../../../etc/passwd',
        'storage_key': '../../../../etc/passwd',
        'checksum': '<script>alert("xss")</script>',
        'error_message': '<img src=x onerror=alert("xss")>'
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Cleanup code here if needed
    pass
