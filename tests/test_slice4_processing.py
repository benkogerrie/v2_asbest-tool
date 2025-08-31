"""
Tests for Slice 4 - Processing Pipeline (Queue + Worker, dummy AI + PDF).
"""
import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from datetime import datetime

from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.queue.jobs import process_report
from app.queue.conn import reports_queue
from app.services.storage import storage


class TestReportProcessing:
    """Test report processing functionality."""
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage service."""
        with patch('app.queue.jobs.storage') as mock_storage:
            mock_storage.upload_fileobj.return_value = True
            yield mock_storage
    
    @pytest.fixture
    def sample_report(self, db_session):
        """Create a sample report for testing."""
        # Create tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Test Tenant",
            domain="test.com"
        )
        db_session.add(tenant)
        db_session.commit()
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="test@test.com",
            tenant_id=tenant.id,
            role=UserRole.ADMIN,
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create report
        report = Report(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            uploaded_by=user.id,
            filename="test_report.pdf",
            status=ReportStatus.PROCESSING,
            source_object_key="tenants/test/reports/test/source/test_report.pdf"
        )
        db_session.add(report)
        db_session.commit()
        
        return report
    
    def test_process_report_success(self, mock_storage, sample_report, db_session):
        """Test successful report processing."""
        # Run the job
        result = process_report(str(sample_report.id))
        
        # Verify result
        assert result is True
        
        # Refresh report from database
        db_session.refresh(sample_report)
        
        # Verify report was updated
        assert sample_report.status == ReportStatus.DONE
        assert sample_report.score == 89
        assert sample_report.finding_count == 2
        assert sample_report.summary == "Rapport is grotendeels compleet; aanvulling nodig voor maatregel 2A (dummy)."
        assert sample_report.findings_json is not None
        assert len(sample_report.findings_json) == 2
        assert sample_report.conclusion_object_key is not None
        assert "conclusion/conclusie.pdf" in sample_report.conclusion_object_key
        
        # Verify findings
        findings = sample_report.findings_json
        assert findings[0]["code"] == "R001"
        assert findings[0]["severity"] == "MAJOR"
        assert findings[1]["code"] == "R012"
        assert findings[1]["severity"] == "CRITICAL"
        
        # Verify audit logs
        audit_logs = db_session.query(ReportAuditLog).filter_by(report_id=sample_report.id).all()
        audit_actions = [log.action for log in audit_logs]
        assert AuditAction.PROCESS_START in audit_actions
        assert AuditAction.PROCESS_DONE in audit_actions
        
        # Verify PDF was uploaded
        mock_storage.upload_fileobj.assert_called_once()
        call_args = mock_storage.upload_fileobj.call_args
        assert call_args[0][1] == sample_report.conclusion_object_key
        assert call_args[0][2] == "application/pdf"
    
    def test_process_report_not_found(self, mock_storage, db_session):
        """Test processing non-existent report."""
        fake_id = str(uuid.uuid4())
        result = process_report(fake_id)
        assert result is False
    
    def test_process_report_storage_failure(self, mock_storage, sample_report, db_session):
        """Test processing when storage upload fails."""
        # Make storage upload fail
        mock_storage.upload_fileobj.return_value = False
        
        # Run the job
        result = process_report(str(sample_report.id))
        
        # Verify result
        assert result is False
        
        # Refresh report from database
        db_session.refresh(sample_report)
        
        # Verify report status is failed
        assert sample_report.status == ReportStatus.FAILED
        
        # Verify audit logs
        audit_logs = db_session.query(ReportAuditLog).filter_by(report_id=sample_report.id).all()
        audit_actions = [log.action for log in audit_logs]
        assert AuditAction.PROCESS_START in audit_actions
        assert AuditAction.PROCESS_FAIL in audit_actions
    
    def test_process_report_idempotent(self, mock_storage, sample_report, db_session):
        """Test that processing the same report twice doesn't cause issues."""
        # Process first time
        result1 = process_report(str(sample_report.id))
        assert result1 is True
        
        # Process second time
        result2 = process_report(str(sample_report.id))
        assert result2 is True
        
        # Verify report is still in DONE state
        db_session.refresh(sample_report)
        assert sample_report.status == ReportStatus.DONE
        assert sample_report.score == 89


class TestQueueIntegration:
    """Test queue integration."""
    
    @patch('app.queue.conn.reports_queue')
    def test_enqueue_on_upload(self, mock_queue, client, auth_headers, sample_file):
        """Test that upload enqueues processing job."""
        # Mock the queue
        mock_queue_instance = Mock()
        mock_queue.return_value = mock_queue_instance
        
        # Upload file
        response = client.post(
            "/reports/",
            files={"file": sample_file},
            headers=auth_headers
        )
        
        # Verify upload succeeded
        assert response.status_code == 201
        
        # Verify job was enqueued
        mock_queue_instance.enqueue.assert_called_once()
        call_args = mock_queue_instance.enqueue.call_args
        assert call_args[0][0] == "app.queue.jobs.process_report"
        assert "report_id" in call_args[1]


class TestDownloadEndpoints:
    """Test download endpoints."""
    
    @patch('app.services.storage.storage.download_fileobj')
    def test_download_source(self, mock_download, client, auth_headers, sample_report):
        """Test downloading source file."""
        # Mock storage response
        mock_file = BytesIO(b"test file content")
        mock_download.return_value = mock_file
        
        # Download source
        response = client.get(
            f"/reports/{sample_report.id}/source",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert sample_report.filename in response.headers["content-disposition"]
    
    @patch('app.services.storage.storage.download_fileobj')
    def test_download_conclusion(self, mock_download, client, auth_headers, sample_report):
        """Test downloading conclusion PDF."""
        # Set report to DONE with conclusion
        sample_report.status = ReportStatus.DONE
        sample_report.conclusion_object_key = "test/conclusion.pdf"
        
        # Mock storage response
        mock_file = BytesIO(b"pdf content")
        mock_download.return_value = mock_file
        
        # Download conclusion
        response = client.get(
            f"/reports/{sample_report.id}/conclusion",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
    
    def test_download_conclusion_not_available(self, client, auth_headers, sample_report):
        """Test downloading conclusion when not available."""
        # Report is still processing
        sample_report.status = ReportStatus.PROCESSING
        sample_report.conclusion_object_key = None
        
        # Download conclusion
        response = client.get(
            f"/reports/{sample_report.id}/conclusion",
            headers=auth_headers
        )
        
        # Verify 404 response
        assert response.status_code == 404
        assert "not yet available" in response.json()["detail"]
    
    def test_download_rbac_other_tenant(self, client, auth_headers, other_tenant_report):
        """Test RBAC on downloads - other tenant."""
        # Try to download from other tenant
        response = client.get(
            f"/reports/{other_tenant_report.id}/source",
            headers=auth_headers
        )
        
        # Should be denied
        assert response.status_code == 404
    
    def test_download_rbac_system_owner(self, client, system_owner_headers, other_tenant_report):
        """Test RBAC on downloads - system owner can access all."""
        # Mock storage response
        with patch('app.services.storage.storage.download_fileobj') as mock_download:
            mock_file = BytesIO(b"test content")
            mock_download.return_value = mock_file
            
            # System owner should be able to download
            response = client.get(
                f"/reports/{other_tenant_report.id}/source",
                headers=system_owner_headers
            )
            
            # Should succeed
            assert response.status_code == 200


class TestReportDetailWithFindings:
    """Test that report detail shows findings correctly."""
    
    def test_report_detail_with_findings(self, client, auth_headers, sample_report):
        """Test that report detail shows findings after processing."""
        # Process the report
        process_report(str(sample_report.id))
        
        # Get report detail
        response = client.get(
            f"/reports/{sample_report.id}",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify findings are present
        assert "findings" in data
        assert len(data["findings"]) == 2
        assert data["findings"][0]["code"] == "R001"
        assert data["findings"][0]["severity"] == "MAJOR"
        assert data["findings"][1]["code"] == "R012"
        assert data["findings"][1]["severity"] == "CRITICAL"
        
        # Verify summary
        assert "summary" in data
        assert data["summary"] == "Rapport is grotendeels compleet; aanvulling nodig voor maatregel 2A (dummy)."
        
        # Verify score
        assert data["score"] == 89
        assert data["finding_count"] == 2


# Fixtures for testing
@pytest.fixture
def sample_file():
    """Create a sample PDF file for testing."""
    return ("test_report.pdf", BytesIO(b"test pdf content"), "application/pdf")

@pytest.fixture
def other_tenant_report(db_session, sample_report):
    """Create a report from another tenant."""
    # Create another tenant
    other_tenant = Tenant(
        id=uuid.uuid4(),
        name="Other Tenant",
        domain="other.com"
    )
    db_session.add(other_tenant)
    db_session.commit()
    
    # Create report in other tenant
    other_report = Report(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        uploaded_by=sample_report.uploaded_by,
        filename="other_report.pdf",
        status=ReportStatus.PROCESSING,
        source_object_key="tenants/other/reports/other/source/other_report.pdf"
    )
    db_session.add(other_report)
    db_session.commit()
    
    return other_report
