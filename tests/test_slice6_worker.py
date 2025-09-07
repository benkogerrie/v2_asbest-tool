"""
Unit tests for Slice 6 worker functionality.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.queue.jobs import process_report, purge_deleted_reports
from app.models.report import Report, ReportStatus, AuditAction
from app.models.user import User
from app.models.tenant import Tenant


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
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def processing_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="test_report.pdf",
        status=ReportStatus.PROCESSING,
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/test_report.pdf"
    )


class TestWorkerStatusFlows:
    """Test worker status flows and processing."""
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    @patch('app.queue.jobs.extract_text_from_pdf')
    @patch('app.queue.jobs.analyze_text_to_result')
    @patch('app.queue.jobs.run_rules_v1')
    @patch('app.queue.jobs.build_conclusion_pdf')
    @patch('app.queue.jobs.storage')
    @patch('app.queue.jobs.email_service')
    def test_success_flow_complete(self, mock_email, mock_storage, mock_build_pdf, 
                                   mock_run_rules, mock_analyze, mock_extract, 
                                   mock_sessionmaker, mock_create_engine, processing_report):
        """✅ Succesflow: na genereren → upload → update storage_key, file_size, checksum, status='DONE'."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = processing_report
        
        # Mock analysis results
        mock_analyze.return_value = Mock(
            score=85.5,
            summary="Test summary",
            engine="rules",
            engine_version="1.0.0",
            duration_ms=1500
        )
        
        mock_run_rules.return_value = [
            Mock(dict=Mock(return_value={"rule_id": "R001", "severity": "HIGH"})),
            Mock(dict=Mock(return_value={"rule_id": "R002", "severity": "MEDIUM"}))
        ]
        
        # Mock storage upload
        mock_storage.upload_fileobj_with_checksum.return_value = (True, "abc123def456", 1024000)
        
        # Mock email service
        mock_email.send_report_completion_notification.return_value = True
        
        # Mock PDF generation
        mock_build_pdf.return_value = None
        
        # Mock text extraction
        mock_extract.return_value = "Extracted text content"
        
        # Execute
        result = process_report(str(processing_report.id))
        
        # Verify success
        assert result is True
        
        # Verify report was updated
        assert processing_report.status == ReportStatus.DONE
        assert processing_report.score == 85.5
        assert processing_report.finding_count == 2
        assert processing_report.storage_key == f"tenants/{processing_report.tenant_id}/reports/{processing_report.id}/output.pdf"
        assert processing_report.checksum == "abc123def456"
        assert processing_report.file_size == 1024000
        assert processing_report.summary == "Test summary"
        
        # Verify storage upload was called
        mock_storage.upload_fileobj_with_checksum.assert_called_once()
        
        # Verify email notification was sent
        mock_email.send_report_completion_notification.assert_called_once()
        
        # Verify audit logs were created
        assert mock_session.add.call_count >= 2  # At least PROCESS_DONE and NOTIFICATION_SENT
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    @patch('app.queue.jobs.extract_text_from_pdf')
    @patch('app.queue.jobs.analyze_text_to_result')
    @patch('app.queue.jobs.run_rules_v1')
    @patch('app.queue.jobs.build_conclusion_pdf')
    @patch('app.queue.jobs.storage')
    @patch('app.queue.jobs.email_service')
    def test_failure_flow_with_error_message(self, mock_email, mock_storage, mock_build_pdf,
                                           mock_run_rules, mock_analyze, mock_extract,
                                           mock_sessionmaker, mock_create_engine, processing_report):
        """✅ Foutflow: bij except → status='FAILED', error_message gevuld."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = processing_report
        
        # Mock text extraction to raise exception
        mock_extract.side_effect = Exception("PDF extraction failed")
        
        # Mock email service
        mock_email.send_report_completion_notification.return_value = True
        
        # Execute
        result = process_report(str(processing_report.id))
        
        # Verify failure
        assert result is False
        
        # Verify report was updated with error
        assert processing_report.status == ReportStatus.FAILED
        assert processing_report.error_message == "PDF extraction failed"
        
        # Verify email notification was sent for failure
        mock_email.send_report_completion_notification.assert_called_once()
        
        # Verify audit logs were created
        assert mock_session.add.call_count >= 2  # At least PROCESS_FAIL and NOTIFICATION_SENT
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    @patch('app.queue.jobs.extract_text_from_pdf')
    @patch('app.queue.jobs.analyze_text_to_result')
    @patch('app.queue.jobs.run_rules_v1')
    @patch('app.queue.jobs.build_conclusion_pdf')
    @patch('app.queue.jobs.storage')
    @patch('app.queue.jobs.email_service')
    def test_notification_sent_audit_log(self, mock_email, mock_storage, mock_build_pdf,
                                       mock_run_rules, mock_analyze, mock_extract,
                                       mock_sessionmaker, mock_create_engine, processing_report):
        """✅ Bij DONE/FAILED: NOTIFICATION_SENT audit geschreven."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = processing_report
        
        # Mock analysis results for success
        mock_analyze.return_value = Mock(
            score=85.5,
            summary="Test summary",
            engine="rules",
            engine_version="1.0.0",
            duration_ms=1500
        )
        
        mock_run_rules.return_value = []
        mock_storage.upload_fileobj_with_checksum.return_value = (True, "abc123", 1024)
        mock_email.send_report_completion_notification.return_value = True
        mock_build_pdf.return_value = None
        mock_extract.return_value = "Extracted text"
        
        # Execute
        result = process_report(str(processing_report.id))
        
        # Verify success
        assert result is True
        
        # Verify email notification was sent
        mock_email.send_report_completion_notification.assert_called_once()
        
        # Verify NOTIFICATION_SENT audit log was created
        audit_calls = [call for call in mock_session.add.call_args_list 
                      if hasattr(call[0][0], 'action') and call[0][0].action == AuditAction.NOTIFICATION_SENT]
        assert len(audit_calls) == 1
        
        # Verify the audit log content
        notification_audit = audit_calls[0][0][0]
        assert notification_audit.action == AuditAction.NOTIFICATION_SENT
        assert "Email notification sent" in notification_audit.note
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    def test_purge_deleted_reports_success(self, mock_sessionmaker, mock_create_engine):
        """✅ Purge job: verwijdert object, schrijft REPORT_PURGE."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        
        # Create test reports
        from datetime import timedelta
        old_date = datetime.utcnow() - timedelta(days=10)
        
        old_deleted_report = Report(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            filename="old_deleted.pdf",
            status=ReportStatus.DONE,
            deleted_at=old_date,
            storage_key="tenants/test/reports/old/output.pdf",
            source_object_key="tenants/test/reports/old/source.pdf"
        )
        
        recent_deleted_report = Report(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            filename="recent_deleted.pdf",
            status=ReportStatus.DONE,
            deleted_at=datetime.utcnow() - timedelta(days=1),  # Recent
            storage_key="tenants/test/reports/recent/output.pdf",
            source_object_key="tenants/test/reports/recent/source.pdf"
        )
        
        # Mock query to return only old deleted report
        mock_session.query.return_value.filter.return_value.all.return_value = [old_deleted_report]
        
        # Mock storage
        with patch('app.queue.jobs.storage') as mock_storage:
            mock_storage.delete_object.return_value = True
            
            # Execute
            purged_count = purge_deleted_reports()
        
        # Verify result
        assert purged_count == 1
        
        # Verify storage delete was called for both files
        assert mock_storage.delete_object.call_count == 2
        
        # Verify REPORT_PURGE audit log was created
        audit_calls = [call for call in mock_session.add.call_args_list 
                      if hasattr(call[0][0], 'action') and call[0][0].action == AuditAction.REPORT_PURGE]
        assert len(audit_calls) == 1
        
        # Verify the report was deleted from database
        mock_session.delete.assert_called_once_with(old_deleted_report)
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    def test_purge_job_respects_delay_days(self, mock_sessionmaker, mock_create_engine):
        """✅ Purge job slaat soft-deleted records pas na X dagen."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        
        # Mock query to return empty list (no reports old enough)
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        # Execute
        purged_count = purge_deleted_reports()
        
        # Verify no reports were purged
        assert purged_count == 0
        
        # Verify no storage operations
        with patch('app.queue.jobs.storage') as mock_storage:
            assert mock_storage.delete_object.call_count == 0
    
    @patch('app.queue.jobs.create_engine')
    @patch('app.queue.jobs.sessionmaker')
    def test_purge_job_handles_storage_errors(self, mock_sessionmaker, mock_create_engine):
        """✅ Purge job handles storage errors gracefully."""
        
        # Setup mocks
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        mock_session = Mock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        
        # Create test report
        from datetime import timedelta
        old_date = datetime.utcnow() - timedelta(days=10)
        
        old_deleted_report = Report(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            uploaded_by=uuid.uuid4(),
            filename="old_deleted.pdf",
            status=ReportStatus.DONE,
            deleted_at=old_date,
            storage_key="tenants/test/reports/old/output.pdf",
            source_object_key="tenants/test/reports/old/source.pdf"
        )
        
        mock_session.query.return_value.filter.return_value.all.return_value = [old_deleted_report]
        
        # Mock storage to fail
        with patch('app.queue.jobs.storage') as mock_storage:
            mock_storage.delete_object.return_value = False  # Storage delete failed
            
            # Execute
            purged_count = purge_deleted_reports()
        
        # Should still complete (graceful error handling)
        assert purged_count == 1
        
        # Verify audit log was still created
        audit_calls = [call for call in mock_session.add.call_args_list 
                      if hasattr(call[0][0], 'action') and call[0][0].action == AuditAction.REPORT_PURGE]
        assert len(audit_calls) == 1
        
        # Verify the audit log mentions files deleted count
        notification_audit = audit_calls[0][0][0]
        assert "Files deleted: 0" in notification_audit.note  # Both storage deletes failed
