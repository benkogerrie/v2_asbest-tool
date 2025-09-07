"""
Basis tests voor Slice 6 functionaliteit - geen complexe mocking.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestSlice6Basic:
    """Basis tests voor Slice 6 functionaliteit."""
    
    def test_download_endpoint_exists(self):
        """Test dat de download endpoint bestaat."""
        client = TestClient(app)
        
        # Test dat de endpoint bestaat (zonder authenticatie)
        response = client.get("/reports/123/download")
        
        # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
        # Dit bewijst dat de endpoint bestaat
        assert response.status_code == 401

    def test_sse_stream_endpoint_exists(self):
        """Test dat de SSE stream endpoint bestaat."""
        client = TestClient(app)
        
        # Test dat de endpoint bestaat (zonder authenticatie)
        response = client.get("/reports/stream")
        
        # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
        # Dit bewijst dat de endpoint bestaat
        assert response.status_code == 401

    def test_soft_delete_endpoint_exists(self):
        """Test dat de soft delete endpoint bestaat."""
        client = TestClient(app)
        
        # Test dat de endpoint bestaat (zonder authenticatie)
        response = client.delete("/reports/123")
        
        # We verwachten een 401 (Unauthorized) omdat we niet geauthenticeerd zijn
        # Dit bewijst dat de endpoint bestaat
        assert response.status_code == 401

    def test_storage_service_has_presigned_url_method(self):
        """Test dat de storage service de presigned_get_url methode heeft."""
        from app.services.storage import storage
        
        # Test dat de methode bestaat
        assert hasattr(storage, 'presigned_get_url')
        assert callable(getattr(storage, 'presigned_get_url'))

    def test_report_service_has_download_method(self):
        """Test dat de ReportService de get_report_for_download methode heeft."""
        from app.services.reports import ReportService
        
        # Test dat de methode bestaat
        assert hasattr(ReportService, 'get_report_for_download')
        assert callable(getattr(ReportService, 'get_report_for_download'))

    def test_config_has_download_settings(self):
        """Test dat de config de download instellingen heeft."""
        from app.config import settings
        
        # Test dat de instellingen bestaan
        assert hasattr(settings, 'download_ttl')
        assert hasattr(settings, 'purge_delay_days')
        
        # Test dat ze de juiste types hebben
        assert isinstance(settings.download_ttl, int)
        assert isinstance(settings.purge_delay_days, int)

    def test_report_model_has_storage_fields(self):
        """Test dat het Report model de nieuwe storage velden heeft."""
        from app.models.report import Report
        
        # Test dat de velden bestaan
        assert hasattr(Report, 'storage_key')
        assert hasattr(Report, 'checksum')
        assert hasattr(Report, 'file_size')
        assert hasattr(Report, 'error_message')
        assert hasattr(Report, 'deleted_at')

    def test_audit_action_has_new_actions(self):
        """Test dat AuditAction de nieuwe acties heeft."""
        from app.models.report import AuditAction
        
        # Test dat de nieuwe acties bestaan
        assert hasattr(AuditAction, 'REPORT_DOWNLOAD')
        assert hasattr(AuditAction, 'NOTIFICATION_SENT')
        assert hasattr(AuditAction, 'REPORT_PURGE')

    def test_email_service_exists(self):
        """Test dat de email service bestaat."""
        from app.services.email import EmailService
        
        # Test dat de service bestaat
        assert EmailService is not None
        assert hasattr(EmailService, 'send_report_completion_notification')

    def test_worker_has_purge_function(self):
        """Test dat de worker de purge functie heeft."""
        from app.queue.jobs import purge_deleted_reports
        
        # Test dat de functie bestaat
        assert callable(purge_deleted_reports)

    def test_frontend_has_sse_client(self):
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

    def test_download_endpoint_route_registered(self):
        """Test dat de download endpoint route geregistreerd is."""
        from app.main import app
        
        # Check if the route is registered
        routes = [route.path for route in app.routes]
        assert "/reports/{report_id}/download" in routes

    def test_sse_stream_route_registered(self):
        """Test dat de SSE stream route geregistreerd is."""
        from app.main import app
        
        # Check if the route is registered
        routes = [route.path for route in app.routes]
        assert "/reports/stream" in routes

    def test_soft_delete_route_registered(self):
        """Test dat de soft delete route geregistreerd is."""
        from app.main import app
        
        # Check if the route is registered
        routes = [route.path for route in app.routes]
        assert "/reports/{report_id}" in routes
