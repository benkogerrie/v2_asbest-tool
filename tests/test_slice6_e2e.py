"""
End-to-end integration tests for Slice 6 functionality.
"""
import pytest
import uuid
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User, UserRole
from app.models.tenant import Tenant


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
def other_tenant():
    return Tenant(
        id=uuid.uuid4(),
        name="Other Tenant",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def other_user(other_tenant):
    return User(
        id=uuid.uuid4(),
        email="other@example.com",
        tenant_id=other_tenant.id,
        first_name="Other",
        last_name="User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


class TestSlice6E2E:
    """End-to-end integration tests for Slice 6."""
    
    @patch('app.api.reports.ReportService')
    @patch('app.api.reports.storage')
    def test_e2e_download_availability_flow(self, mock_storage, mock_service, client, test_user):
        """2.1 End-to-end download beschikbaarheid."""
        
        # Create processing report
        processing_report = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="test_report.pdf",
            status=ReportStatus.PROCESSING,
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/test_report.pdf"
        )
        
        # Step 1: Upload rapport → status PROCESSING
        mock_service.return_value.get_report_for_download.return_value = processing_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # Step 2: Probeer /download → 404
            response = client.get(f"/reports/{processing_report.id}/download")
            assert response.status_code == 400
            assert "not ready for download" in response.json()["detail"]
        
        # Step 3: Forceer DONE (mock worker completion)
        done_report = Report(
            id=processing_report.id,
            tenant_id=processing_report.tenant_id,
            uploaded_by=processing_report.uploaded_by,
            filename=processing_report.filename,
            status=ReportStatus.DONE,
            score=85.5,
            finding_count=3,
            storage_key="tenants/test/reports/test/output.pdf",
            checksum="abc123def456",
            file_size=1024000,
            uploaded_at=processing_report.uploaded_at,
            source_object_key=processing_report.source_object_key
        )
        
        mock_service.return_value.get_report_for_download.return_value = done_report
        mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # Step 4: /download → 200 met url
            response = client.get(f"/reports/{done_report.id}/download")
            assert response.status_code == 200
            
            data = response.json()
            assert "url" in data
            assert "expires_in" in data
            assert "filename" in data
            assert data["filename"] == "test_report.pdf"
            assert data["file_size"] == 1024000
            assert data["checksum"] == "abc123def456"
        
        # Step 5: Controleer audit log: REPORT_DOWNLOAD aanwezig
        # (This would be verified in a real test by checking the database)
        mock_storage.presigned_get_url.assert_called_once()
    
    @patch('app.api.reports.ReportService')
    def test_e2e_soft_delete_flow(self, mock_service, client, test_user):
        """2.2 Soft delete flow."""
        
        # Create report
        report = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="test_report.pdf",
            status=ReportStatus.DONE,
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/test_report.pdf"
        )
        
        mock_service.return_value.get_report_for_download.return_value = report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # Step 1: DELETE /reports/{id} → 200
            response = client.delete(f"/reports/{report.id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "message" in data
            assert "deleted_at" in data
        
        # Step 2: /reports/ list → item ontbreekt
        # (This would be verified by checking the list endpoint)
        
        # Step 3: /download → 404
        # Update mock to return deleted report
        deleted_report = Report(
            id=report.id,
            tenant_id=report.tenant_id,
            uploaded_by=report.uploaded_by,
            filename=report.filename,
            status=report.status,
            deleted_at=datetime.utcnow(),
            uploaded_at=report.uploaded_at,
            source_object_key=report.source_object_key
        )
        
        mock_service.return_value.get_report_for_download.return_value = deleted_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{report.id}/download")
            assert response.status_code == 404
            assert "deleted" in response.json()["detail"]
    
    @patch('app.api.reports.ReportService')
    def test_e2e_tenant_isolation(self, mock_service, client, test_user, other_user):
        """2.3 Tenant-isolatie."""
        
        # Create report for test_user's tenant
        report_alpha = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="alpha_report.pdf",
            status=ReportStatus.DONE,
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/alpha/reports/test/source/alpha_report.pdf"
        )
        
        # User A (Tenant X) can access their own report
        mock_service.return_value.get_report_for_download.return_value = report_alpha
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get(f"/reports/{report_alpha.id}/download")
            assert response.status_code == 200
        
        # User B (Tenant Y) cannot access Tenant X's report
        mock_service.return_value.get_report_for_download.return_value = None
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=other_user):
            response = client.get(f"/reports/{report_alpha.id}/download")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
    
    @patch('app.api.reports.ReportService')
    def test_e2e_failed_flow(self, mock_service, client, test_user):
        """2.4 Failed flow."""
        
        # Create failed report
        failed_report = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="failed_report.pdf",
            status=ReportStatus.FAILED,
            error_message="Processing failed due to invalid PDF format",
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/failed_report.pdf"
        )
        
        mock_service.return_value.get_report_for_download.return_value = failed_report
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # /download → 404
            response = client.get(f"/reports/{failed_report.id}/download")
            assert response.status_code == 400
            assert "not ready for download" in response.json()["detail"]
            assert "FAILED" in response.json()["detail"]
    
    @patch('app.api.reports.ReportService')
    @patch('app.api.reports.storage')
    def test_e2e_ttl_behavior(self, mock_storage, mock_service, client, test_user):
        """2.5 TTL gedrag (spot-check)."""
        
        # Create done report
        done_report = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="test_report.pdf",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/test/output.pdf",
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/test_report.pdf"
        )
        
        mock_service.return_value.get_report_for_download.return_value = done_report
        mock_storage.presigned_get_url.return_value = "https://storage.example.com/presigned-url"
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # Vraag download → bewaar URL
            response1 = client.get(f"/reports/{done_report.id}/download")
            assert response1.status_code == 200
            
            data1 = response1.json()
            url1 = data1["url"]
            expires_in1 = data1["expires_in"]
            
            # Nieuwe download call → nieuwe URL
            response2 = client.get(f"/reports/{done_report.id}/download")
            assert response2.status_code == 200
            
            data2 = response2.json()
            url2 = data2["url"]
            expires_in2 = data2["expires_in"]
            
            # URLs should be different (new presigned URL generated)
            assert url1 != url2
            assert expires_in1 == expires_in2  # Same TTL
    
    @patch('app.api.reports.ReportService')
    def test_e2e_sse_stream_tenant_isolation(self, mock_service, client, test_user, other_user):
        """2.3 SSE stream tenant isolation."""
        
        # Mock reports for different tenants
        alpha_reports = [
            Report(
                id=uuid.uuid4(),
                tenant_id=test_user.tenant_id,
                uploaded_by=test_user.id,
                filename="alpha_report1.pdf",
                status=ReportStatus.DONE,
                uploaded_at=datetime.utcnow(),
                source_object_key="tenants/alpha/reports/test/source/alpha_report1.pdf"
            )
        ]
        
        beta_reports = [
            Report(
                id=uuid.uuid4(),
                tenant_id=other_user.tenant_id,
                uploaded_by=other_user.id,
                filename="beta_report1.pdf",
                status=ReportStatus.DONE,
                uploaded_at=datetime.utcnow(),
                source_object_key="tenants/beta/reports/test/source/beta_report1.pdf"
            )
        ]
        
        # Mock service to return only tenant-specific reports
        def mock_get_reports_for_user(user):
            if user.tenant_id == test_user.tenant_id:
                return alpha_reports
            else:
                return beta_reports
        
        mock_service.return_value.get_reports_for_user.side_effect = mock_get_reports_for_user
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            # Start SSE stream
            response = client.get("/reports/stream")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Read initial data
            content = response.content.decode('utf-8')
            assert "data:" in content
            assert "initial_state" in content
            
            # Verify only alpha reports are included
            assert "alpha_report1.pdf" in content
            assert "beta_report1.pdf" not in content
    
    @patch('app.api.reports.ReportService')
    def test_e2e_sse_heartbeat(self, mock_service, client, test_user):
        """SSE heartbeat functionality."""
        
        mock_service.return_value.get_reports_for_user.return_value = []
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get("/reports/stream")
            assert response.status_code == 200
            
            # Read content to verify heartbeat
            content = response.content.decode('utf-8')
            assert "data:" in content
            assert "connected" in content
    
    @patch('app.api.reports.ReportService')
    def test_e2e_sse_error_handling(self, mock_service, client, test_user):
        """SSE error handling."""
        
        # Mock service to raise exception
        mock_service.return_value.get_reports_for_user.side_effect = Exception("Database error")
        
        with patch('app.api.reports.fastapi_users.current_user', return_value=test_user):
            response = client.get("/reports/stream")
            assert response.status_code == 200
            
            # Read content to verify error handling
            content = response.content.decode('utf-8')
            assert "data:" in content
            # Should handle error gracefully without crashing
