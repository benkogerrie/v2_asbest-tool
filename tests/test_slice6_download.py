"""
Unit tests for Slice 6 download endpoint functionality.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.config import settings
from app.auth.auth import fastapi_users


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
        score=85.5,
        finding_count=3,
        storage_key="tenants/test/reports/test/output.pdf",
        checksum="abc123def456",
        file_size=1024000,
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/test_report.pdf"
    )


@pytest.fixture
def processing_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="processing_report.pdf",
        status=ReportStatus.PROCESSING,
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/processing_report.pdf"
    )


@pytest.fixture
def failed_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="failed_report.pdf",
        status=ReportStatus.FAILED,
        error_message="Processing failed due to invalid PDF format",
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/failed_report.pdf"
    )


@pytest.fixture
def deleted_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="deleted_report.pdf",
        status=ReportStatus.DONE,
        deleted_at=datetime.utcnow(),
        uploaded_at=datetime.utcnow() - timedelta(hours=1),
        source_object_key="tenants/test/reports/test/source/deleted_report.pdf"
    )


class TestDownloadEndpoint:
    """Test download endpoint functionality."""
    
    @patch('app.services.reports.ReportService')
    @patch('app.api.reports.storage')
    def test_download_done_report_success(self, mock_storage, mock_service, client, done_report, test_user, mock_auth_dependencies):
        """✅ DONE → 200 met {url, expires_in} en audit REPORT_DOWNLOAD geschreven."""
        # Setup mocks
        mock_service.return_value.get_report_for_download.return_value = done_report
        mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
        
        # Mock authentication by overriding the dependency
        def override_get_current_user():
            return test_user
        
        app.dependency_overrides[fastapi_users.current_user(active=True)] = override_get_current_user
        
        try:
            response = client.get(f"/reports/{done_report.id}/download")
        finally:
            # Clean up the override
            app.dependency_overrides.pop(fastapi_users.current_user(active=True), None)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "url" in data
        assert "expires_in" in data
        assert "filename" in data
        assert "file_size" in data
        assert "checksum" in data
        
        assert data["url"] == "https://storage.example.com/presigned-url"
        assert data["expires_in"] == settings.download_ttl
        assert data["filename"] == "test_report.pdf"
        assert data["file_size"] == 1024000
        assert data["checksum"] == "abc123def456"
        
        # Verify storage call
        mock_storage.presigned_get_url.assert_called_once_with(
            object_key=done_report.storage_key,
            expires=settings.download_ttl
        )
    
    @patch('app.services.reports.ReportService')
    def test_download_processing_report_404(self, mock_service, client, processing_report, test_user):
        """❌ PROCESSING → 404 'Not available'."""
        mock_service.return_value.get_report_for_download.return_value = processing_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{processing_report.id}/download")
        
        assert response.status_code == 400
        assert "not ready for download" in response.json()["detail"]
        assert "PROCESSING" in response.json()["detail"]
    
    @patch('app.services.reports.ReportService')
    def test_download_failed_report_404(self, mock_service, client, failed_report, test_user):
        """❌ FAILED → 404 'Not available'."""
        mock_service.return_value.get_report_for_download.return_value = failed_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{failed_report.id}/download")
        
        assert response.status_code == 400
        assert "not ready for download" in response.json()["detail"]
        assert "FAILED" in response.json()["detail"]
    
    @patch('app.services.reports.ReportService')
    def test_download_deleted_report_404(self, mock_service, client, deleted_report, test_user):
        """❌ deleted_at IS NOT NULL → 404."""
        mock_service.return_value.get_report_for_download.return_value = deleted_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{deleted_report.id}/download")
        
        assert response.status_code == 404
        assert "deleted" in response.json()["detail"]
    
    @patch('app.services.reports.ReportService')
    def test_download_tenant_mismatch_404(self, mock_service, client, done_report, test_user):
        """❌ Tenant mismatch → 404 (niet 403; geen leakage)."""
        mock_service.return_value.get_report_for_download.return_value = None
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{done_report.id}/download")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('app.services.reports.ReportService')
    def test_download_expires_in_matches_config(self, mock_service, client, done_report, test_user):
        """✅ expires_in == settings.download_ttl."""
        mock_service.return_value.get_report_for_download.return_value = done_report
        
        with patch('app.api.reports.storage') as mock_storage:
            mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
            
            with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
                response = client.get(f"/reports/{done_report.id}/download")
        
        assert response.status_code == 200
        data = response.json()
        assert data["expires_in"] == settings.download_ttl
    
    @patch('app.services.reports.ReportService')
    def test_download_url_contains_correct_key(self, mock_service, client, done_report, test_user):
        """✅ URL bevat juiste key (storage_key) en is S3v4 gesigned."""
        mock_service.return_value.get_report_for_download.return_value = done_report
        
        with patch('app.api.reports.storage') as mock_storage:
            mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
            
            with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
                response = client.get(f"/reports/{done_report.id}/download")
        
        assert response.status_code == 200
        
        # Verify storage service was called with correct key
        mock_storage.presigned_get_url.assert_called_once_with(
            object_key=done_report.storage_key,
            expires=settings.download_ttl
        )
    
    @patch('app.services.reports.ReportService')
    def test_download_fallback_to_conclusion_key(self, mock_service, client, test_tenant, test_user):
        """✅ Fallback naar conclusion_object_key als storage_key niet bestaat."""
        report_without_storage_key = Report(
            id=uuid.uuid4(),
            tenant_id=test_tenant.id,
            uploaded_by=test_user.id,
            filename="fallback_report.pdf",
            status=ReportStatus.DONE,
            conclusion_object_key="tenants/test/reports/test/conclusion.pdf",
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/fallback_report.pdf"
        )
        
        mock_service.return_value.get_report_for_download.return_value = report_without_storage_key
        
        with patch('app.api.reports.storage') as mock_storage:
            mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
            
            with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
                response = client.get(f"/reports/{report_without_storage_key.id}/download")
        
        assert response.status_code == 200
        
        # Verify storage service was called with conclusion_object_key
        mock_storage.presigned_get_url.assert_called_once_with(
            object_key=report_without_storage_key.conclusion_object_key,
            expires=settings.download_ttl
        )
    
    @patch('app.services.reports.ReportService')
    def test_download_no_storage_key_404(self, mock_service, client, test_tenant, test_user):
        """❌ Geen storage_key of conclusion_object_key → 404."""
        report_without_keys = Report(
            id=uuid.uuid4(),
            tenant_id=test_tenant.id,
            uploaded_by=test_user.id,
            filename="no_keys_report.pdf",
            status=ReportStatus.DONE,
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/no_keys_report.pdf"
        )
        
        mock_service.return_value.get_report_for_download.return_value = report_without_keys
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{report_without_keys.id}/download")
        
        assert response.status_code == 404
        assert "not found in storage" in response.json()["detail"]
    
    @patch('app.services.reports.ReportService')
    def test_download_storage_error_500(self, mock_service, client, done_report, test_user):
        """❌ Storage error → 500."""
        mock_service.return_value.get_report_for_download.return_value = done_report
        
        with patch('app.api.reports.storage') as mock_storage:
            mock_storage.presigned_get_url.return_value = None  # Simulate storage error
            
            with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
                response = client.get(f"/reports/{done_report.id}/download")
        
        assert response.status_code == 500
        assert "Failed to generate download URL" in response.json()["detail"]
