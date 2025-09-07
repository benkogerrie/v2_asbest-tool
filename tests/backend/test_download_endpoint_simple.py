"""
Eenvoudige unit tests voor download endpoint functionaliteit.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.report import ReportStatus
from app.auth.auth import fastapi_users


class TestDownloadEndpointSimple:
    """Eenvoudige tests voor download endpoint."""
    
    def test_download_endpoint_exists(self):
        """Test dat de download endpoint bestaat."""
        client = TestClient(app)
        
        # Test dat de endpoint bestaat (zonder authenticatie)
        response = client.get("/reports/123/download")
        
        # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
        # Dit bewijst dat de endpoint bestaat
        assert response.status_code == 401

    @patch('app.services.reports.ReportService')
    @patch('app.api.reports.storage')
    def test_download_service_integration(self, mock_storage, mock_service):
        """Test dat de download service correct geïntegreerd is."""
        
        # Mock report
        mock_report = Mock()
        mock_report.id = "test-123"
        mock_report.status = ReportStatus.DONE
        mock_report.storage_key = "test/report.pdf"
        mock_report.tenant_id = "tenant-123"
        mock_report.deleted_at = None
        
        # Mock service response
        mock_service.return_value.get_report_for_download.return_value = mock_report
        mock_storage.presigned_get_url.return_value = "https://presigned.test/url"
        
        # Mock authentication by overriding the dependency
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        def override_get_current_user():
            return mock_user
        
        app.dependency_overrides[fastapi_users.current_user(active=True)] = override_get_current_user
        
        try:
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            # Should call the service
            mock_service.return_value.get_report_for_download.assert_called_once_with("test-123", mock_user)
            
            # Should call storage
            mock_storage.presigned_get_url.assert_called_once_with(
                object_key="test/report.pdf",
                expires=3600  # Default TTL
            )
        finally:
            # Clean up the override
            app.dependency_overrides.pop(fastapi_users.current_user(active=True), None)

    @patch('app.services.reports.ReportService')
    def test_download_processing_report_404(self, mock_service):
        """Test dat PROCESSING reports niet gedownload kunnen worden."""
        
        # Mock report in PROCESSING status
        mock_report = Mock()
        mock_report.status = ReportStatus.PROCESSING
        
        mock_service.return_value.get_report_for_download.return_value = mock_report
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            assert response.status_code == 400
            assert "not ready for download" in response.json()["detail"]
            assert "PROCESSING" in response.json()["detail"]

    @patch('app.services.reports.ReportService')
    def test_download_failed_report_404(self, mock_service):
        """Test dat FAILED reports niet gedownload kunnen worden."""
        
        # Mock report in FAILED status
        mock_report = Mock()
        mock_report.status = ReportStatus.FAILED
        
        mock_service.return_value.get_report_for_download.return_value = mock_report
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            assert response.status_code == 400
            assert "not ready for download" in response.json()["detail"]
            assert "FAILED" in response.json()["detail"]

    @patch('app.services.reports.ReportService')
    def test_download_deleted_report_404(self, mock_service):
        """Test dat deleted reports niet gedownload kunnen worden."""
        
        # Mock deleted report
        mock_report = Mock()
        mock_report.status = ReportStatus.DONE
        mock_report.deleted_at = "2024-01-01T00:00:00Z"
        
        mock_service.return_value.get_report_for_download.return_value = mock_report
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            assert response.status_code == 404
            assert "deleted" in response.json()["detail"]

    @patch('app.services.reports.ReportService')
    def test_download_no_storage_key_404(self, mock_service):
        """Test dat reports zonder storage_key niet gedownload kunnen worden."""
        
        # Mock report without storage_key
        mock_report = Mock()
        mock_report.status = ReportStatus.DONE
        mock_report.storage_key = None
        mock_report.deleted_at = None
        
        mock_service.return_value.get_report_for_download.return_value = mock_report
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            assert response.status_code == 404
            assert "not found in storage" in response.json()["detail"]

    @patch('app.services.reports.ReportService')
    @patch('app.api.reports.storage')
    def test_download_success(self, mock_storage, mock_service):
        """Test succesvolle download."""
        
        # Mock report ready for download
        mock_report = Mock()
        mock_report.status = ReportStatus.DONE
        mock_report.storage_key = "test/report.pdf"
        mock_report.deleted_at = None
        
        mock_service.return_value.get_report_for_download.return_value = mock_report
        mock_storage.presigned_get_url.return_value = "https://presigned.test/url"
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/test-123/download")
            
            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            assert "expires_in" in data
            assert data["url"] == "https://presigned.test/url"
            assert data["expires_in"] == 3600  # Default TTL

    @patch('app.services.reports.ReportService')
    def test_download_report_not_found(self, mock_service):
        """Test dat niet-bestaande reports 404 retourneren."""
        
        # Mock service to return None (report not found)
        mock_service.return_value.get_report_for_download.return_value = None
        
        # Mock authentication
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.tenant_id = "tenant-123"
        
        with patch('app.api.reports.fastapi_users.current_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            client = TestClient(app)
            response = client.get("/reports/nonexistent/download")
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
