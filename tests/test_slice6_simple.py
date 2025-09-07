"""
Eenvoudige unit tests voor Slice 6 functionaliteit.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.report import Report, ReportStatus
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.config import settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_tenant():
    return Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def test_user(test_tenant):
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        tenant_id=test_tenant.id,
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def done_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="test_report.pdf",
        status=ReportStatus.DONE,
        storage_key="reports/test_report_final.pdf",
        checksum="abc123def456",
        file_size=1024000,
        uploaded_at=datetime.utcnow(),
    )


def test_download_endpoint_exists():
    """Test dat de download endpoint bestaat."""
    client = TestClient(app)
    
    # Test dat de endpoint bestaat (zonder authenticatie)
    response = client.get("/reports/123/download")
    
    # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
    # Dit bewijst dat de endpoint bestaat
    assert response.status_code == 401


def test_storage_service_has_presigned_url_method():
    """Test dat de storage service de presigned_get_url methode heeft."""
    from app.services.storage import storage
    
    # Test dat de methode bestaat
    assert hasattr(storage, 'presigned_get_url')
    assert callable(getattr(storage, 'presigned_get_url'))


def test_report_service_has_download_method():
    """Test dat de ReportService de get_report_for_download methode heeft."""
    from app.services.reports import ReportService
    
    # Test dat de methode bestaat
    assert hasattr(ReportService, 'get_report_for_download')
    assert callable(getattr(ReportService, 'get_report_for_download'))


def test_config_has_download_settings():
    """Test dat de config de download instellingen heeft."""
    # Test dat de instellingen bestaan
    assert hasattr(settings, 'download_ttl')
    assert hasattr(settings, 'purge_delay_days')
    
    # Test dat ze de juiste types hebben
    assert isinstance(settings.download_ttl, int)
    assert isinstance(settings.purge_delay_days, int)


def test_report_model_has_storage_fields():
    """Test dat het Report model de nieuwe storage velden heeft."""
    # Test dat de velden bestaan
    assert hasattr(Report, 'storage_key')
    assert hasattr(Report, 'checksum')
    assert hasattr(Report, 'file_size')
    assert hasattr(Report, 'error_message')
    assert hasattr(Report, 'deleted_at')


def test_audit_action_has_new_actions():
    """Test dat AuditAction de nieuwe acties heeft."""
    from app.models.report import AuditAction
    
    # Test dat de nieuwe acties bestaan
    assert hasattr(AuditAction, 'REPORT_DOWNLOAD')
    assert hasattr(AuditAction, 'NOTIFICATION_SENT')
    assert hasattr(AuditAction, 'REPORT_PURGE')


def test_email_service_exists():
    """Test dat de email service bestaat."""
    from app.services.email import EmailService
    
    # Test dat de service bestaat
    assert EmailService is not None
    assert hasattr(EmailService, 'send_report_completion_notification')


def test_sse_endpoint_exists():
    """Test dat de SSE endpoint bestaat."""
    client = TestClient(app)
    
    # Test dat de endpoint bestaat (zonder authenticatie)
    response = client.get("/reports/stream")
    
    # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
    # Dit bewijst dat de endpoint bestaat
    assert response.status_code == 401


def test_soft_delete_endpoint_exists():
    """Test dat de soft delete endpoint bestaat."""
    client = TestClient(app)
    
    # Test dat de endpoint bestaat (zonder authenticatie)
    response = client.delete("/reports/123")
    
    # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
    # Dit bewijst dat de endpoint bestaat
    assert response.status_code == 401


def test_worker_has_purge_function():
    """Test dat de worker de purge functie heeft."""
    from app.queue.jobs import purge_deleted_reports
    
    # Test dat de functie bestaat
    assert callable(purge_deleted_reports)


def test_frontend_has_sse_client():
    """Test dat de frontend SSE client code heeft."""
    import os
    
    # Test dat de frontend file bestaat
    frontend_path = "ui/user/index.html"
    assert os.path.exists(frontend_path)
    
    # Test dat het SSE client code bevat
    with open(frontend_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'EventSource' in content
        assert 'startSSEConnection' in content
        assert 'downloadReport' in content
