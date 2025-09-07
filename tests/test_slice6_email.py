"""
Unit tests for Slice 6 email service functionality.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from app.services.email import EmailService
from app.models.report import Report, ReportStatus
from app.models.user import User, UserRole
from app.models.tenant import Tenant


@pytest.fixture
def email_service():
    """Create email service instance for testing."""
    return EmailService()


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
        file_size=1024000,
        checksum="abc123def456",
        summary="Test analysis summary",
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/test_report.pdf"
    )


@pytest.fixture
def failed_report(test_tenant, test_user):
    return Report(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        uploaded_by=test_user.id,
        filename="failed_report.pdf",
        status=ReportStatus.FAILED,
        error_message="PDF processing failed due to corrupted file",
        uploaded_at=datetime.utcnow(),
        source_object_key="tenants/test/reports/test/source/failed_report.pdf"
    )


class TestEmailService:
    """Test email service functionality."""
    
    def test_is_configured_with_valid_config(self, email_service):
        """✅ Email service is configured when all required settings are present."""
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        
        assert email_service.is_configured() is True
    
    def test_is_configured_missing_host(self, email_service):
        """❌ Email service not configured when SMTP host is missing."""
        email_service.smtp_host = ""
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        
        assert email_service.is_configured() is False
    
    def test_is_configured_missing_username(self, email_service):
        """❌ Email service not configured when SMTP username is missing."""
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = ""
        email_service.smtp_password = "password123"
        
        assert email_service.is_configured() is False
    
    def test_is_configured_missing_password(self, email_service):
        """❌ Email service not configured when SMTP password is missing."""
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = ""
        
        assert email_service.is_configured() is False
    
    @patch('app.services.email.smtplib.SMTP')
    def test_send_notification_success(self, mock_smtp_class, email_service):
        """✅ Send notification successfully."""
        # Configure email service
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_port = 587
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        email_service.smtp_use_tls = True
        email_service.from_email = "noreply@test.com"
        
        # Mock SMTP
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # Execute
        result = email_service.send_notification(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            html_content="<h1>Test HTML</h1>",
            text_content="Test Text"
        )
        
        # Verify success
        assert result is True
        
        # Verify SMTP was called correctly
        mock_smtp_class.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "password123")
        mock_smtp.send_message.assert_called_once()
    
    @patch('app.services.email.smtplib.SMTP')
    def test_send_notification_failure(self, mock_smtp_class, email_service):
        """❌ Send notification failure."""
        # Configure email service
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        
        # Mock SMTP to raise exception
        mock_smtp_class.side_effect = Exception("SMTP connection failed")
        
        # Execute
        result = email_service.send_notification(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            html_content="<h1>Test HTML</h1>"
        )
        
        # Verify failure
        assert result is False
    
    def test_send_notification_not_configured(self, email_service):
        """❌ Send notification when not configured returns False."""
        # Don't configure email service
        
        # Execute
        result = email_service.send_notification(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            html_content="<h1>Test HTML</h1>"
        )
        
        # Verify failure
        assert result is False
    
    @patch('app.services.email.smtplib.SMTP')
    def test_send_report_completion_notification_done(self, mock_smtp_class, email_service, done_report, test_user):
        """✅ Send completion notification for DONE report."""
        # Configure email service
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        email_service.from_email = "noreply@test.com"
        
        # Mock SMTP
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # Execute
        result = email_service.send_report_completion_notification(
            report=done_report,
            user=test_user
        )
        
        # Verify success
        assert result is True
        
        # Verify email was sent
        mock_smtp.send_message.assert_called_once()
        
        # Verify email content
        sent_message = mock_smtp.send_message.call_args[0][0]
        assert sent_message['Subject'] == "✅ Rapport 'test_report.pdf' is klaar"
        assert sent_message['From'] == "noreply@test.com"
        assert sent_message['To'] == "test@example.com"
    
    @patch('app.services.email.smtplib.SMTP')
    def test_send_report_completion_notification_failed(self, mock_smtp_class, email_service, failed_report, test_user):
        """✅ Send completion notification for FAILED report."""
        # Configure email service
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        email_service.from_email = "noreply@test.com"
        
        # Mock SMTP
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # Execute
        result = email_service.send_report_completion_notification(
            report=failed_report,
            user=test_user
        )
        
        # Verify success
        assert result is True
        
        # Verify email was sent
        mock_smtp.send_message.assert_called_once()
        
        # Verify email content
        sent_message = mock_smtp.send_message.call_args[0][0]
        assert sent_message['Subject'] == "❌ Rapport 'failed_report.pdf' verwerking mislukt"
        assert sent_message['From'] == "noreply@test.com"
        assert sent_message['To'] == "test@example.com"
    
    @patch('app.services.email.smtplib.SMTP')
    def test_send_report_completion_with_tenant_admins(self, mock_smtp_class, email_service, done_report, test_user):
        """✅ Send notification to multiple recipients (uploader + tenant admins)."""
        # Create tenant admin
        tenant_admin = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            tenant_id=test_user.tenant_id,
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        # Configure email service
        email_service.smtp_host = "smtp.gmail.com"
        email_service.smtp_username = "test@gmail.com"
        email_service.smtp_password = "password123"
        email_service.from_email = "noreply@test.com"
        
        # Mock SMTP
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # Execute
        result = email_service.send_report_completion_notification(
            report=done_report,
            user=test_user,
            tenant_admins=[tenant_admin]
        )
        
        # Verify success
        assert result is True
        
        # Verify email was sent
        mock_smtp.send_message.assert_called_once()
        
        # Verify email recipients
        sent_message = mock_smtp.send_message.call_args[0][0]
        assert sent_message['To'] == "test@example.com, admin@example.com"
    
    def test_generate_report_notification_html_done(self, email_service, done_report, test_user):
        """✅ HTML template renders without errors for DONE report."""
        html_content = email_service._generate_report_notification_html(
            report=done_report,
            user=test_user,
            status_text="succesvol verwerkt",
            status_color="#28a745"
        )
        
        # Verify HTML content
        assert "<!DOCTYPE html>" in html_content
        assert "Test User" in html_content
        assert "test_report.pdf" in html_content
        assert "85.5" in html_content
        assert "3" in html_content
        assert "Test analysis summary" in html_content
        assert "#28a745" in html_content  # Success color
    
    def test_generate_report_notification_html_failed(self, email_service, failed_report, test_user):
        """✅ HTML template renders without errors for FAILED report."""
        html_content = email_service._generate_report_notification_html(
            report=failed_report,
            user=test_user,
            status_text="mislukt",
            status_color="#dc3545"
        )
        
        # Verify HTML content
        assert "<!DOCTYPE html>" in html_content
        assert "Test User" in html_content
        assert "failed_report.pdf" in html_content
        assert "PDF processing failed due to corrupted file" in html_content
        assert "#dc3545" in html_content  # Error color
    
    def test_generate_report_notification_text(self, email_service, done_report, test_user):
        """✅ Text template renders without errors."""
        text_content = email_service._generate_report_notification_text(
            report=done_report,
            user=test_user,
            status_text="succesvol verwerkt"
        )
        
        # Verify text content
        assert "Test User" in text_content
        assert "test_report.pdf" in text_content
        assert "85.5" in text_content
        assert "3" in text_content
        assert "Test analysis summary" in text_content
        assert "succesvol verwerkt" in text_content
    
    def test_format_file_size(self, email_service):
        """✅ File size formatting works correctly."""
        # Test various sizes
        assert email_service._format_file_size(1024) == "1.0 KB"
        assert email_service._format_file_size(1024 * 1024) == "1.0 MB"
        assert email_service._format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert email_service._format_file_size(512) == "512.0 B"
        assert email_service._format_file_size(None) == "Onbekend"
        assert email_service._format_file_size(0) == "0.0 B"
    
    def test_send_report_completion_unexpected_status(self, email_service, test_user):
        """❌ Unexpected report status returns False."""
        # Create report with unexpected status
        unexpected_report = Report(
            id=uuid.uuid4(),
            tenant_id=test_user.tenant_id,
            uploaded_by=test_user.id,
            filename="unexpected.pdf",
            status=ReportStatus.PROCESSING,  # Unexpected for completion notification
            uploaded_at=datetime.utcnow(),
            source_object_key="tenants/test/reports/test/source/unexpected.pdf"
        )
        
        # Execute
        result = email_service.send_report_completion_notification(
            report=unexpected_report,
            user=test_user
        )
        
        # Verify failure
        assert result is False
