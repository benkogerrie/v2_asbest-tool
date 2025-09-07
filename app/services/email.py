"""
Email notification service for Slice 6.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime

from app.config import settings
from app.models.report import Report, ReportAuditLog, AuditAction
from app.models.user import User

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service."""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.from_email = settings.from_email
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(
            self.smtp_host and 
            self.smtp_username and 
            self.smtp_password
        )
    
    def send_notification(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email notification.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            
        Returns:
            bool: True if email was sent successfully
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping notification")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {to_emails}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def send_report_completion_notification(
        self,
        report: Report,
        user: User,
        tenant_admins: Optional[List[User]] = None
    ) -> bool:
        """
        Send notification when report processing is completed (DONE or FAILED).
        
        Args:
            report: The report that was processed
            user: The user who uploaded the report
            tenant_admins: Optional list of tenant admins to notify
            
        Returns:
            bool: True if notification was sent successfully
        """
        # Determine notification type and content
        if report.status.value == "DONE":
            subject = f"✅ Rapport '{report.filename}' is klaar"
            status_text = "succesvol verwerkt"
            status_color = "#28a745"
        elif report.status.value == "FAILED":
            subject = f"❌ Rapport '{report.filename}' verwerking mislukt"
            status_text = "mislukt"
            status_color = "#dc3545"
        else:
            logger.warning(f"Unexpected report status for notification: {report.status}")
            return False
        
        # Prepare recipient list
        recipients = [user.email]
        if tenant_admins:
            for admin in tenant_admins:
                if admin.email not in recipients:
                    recipients.append(admin.email)
        
        # Generate HTML content
        html_content = self._generate_report_notification_html(
            report, user, status_text, status_color
        )
        
        # Generate text content
        text_content = self._generate_report_notification_text(
            report, user, status_text
        )
        
        return self.send_notification(
            to_emails=recipients,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _generate_report_notification_html(
        self,
        report: Report,
        user: User,
        status_text: str,
        status_color: str
    ) -> str:
        """Generate HTML content for report notification."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .status {{ display: inline-block; padding: 8px 16px; border-radius: 4px; color: white; background: {status_color}; }}
                .details {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Asbest Tool - Rapport Update</h2>
                    <p>Beste {user.first_name} {user.last_name},</p>
                </div>
                
                <p>Uw rapport <strong>"{report.filename}"</strong> is {status_text}.</p>
                
                <div class="details">
                    <h3>Rapport Details:</h3>
                    <ul>
                        <li><strong>Bestandsnaam:</strong> {report.filename}</li>
                        <li><strong>Status:</strong> <span class="status">{report.status.value}</span></li>
                        <li><strong>Geüpload op:</strong> {report.uploaded_at.strftime('%d-%m-%Y %H:%M') if report.uploaded_at else 'Onbekend'}</li>
                        {f'<li><strong>Score:</strong> {report.score}</li>' if report.score is not None else ''}
                        {f'<li><strong>Aantal bevindingen:</strong> {report.finding_count}</li>' if report.finding_count else ''}
                        {f'<li><strong>Bestandsgrootte:</strong> {self._format_file_size(report.file_size)}</li>' if report.file_size else ''}
                    </ul>
                </div>
                
                {f'<div class="details"><h3>Samenvatting:</h3><p>{report.summary}</p></div>' if report.summary else ''}
                
                {f'<div class="details" style="background: #fff3cd; border: 1px solid #ffeaa7;"><h3>Foutmelding:</h3><p>{report.error_message}</p></div>' if report.error_message else ''}
                
                <p>U kunt het rapport bekijken en downloaden via de Asbest Tool applicatie.</p>
                
                <div class="footer">
                    <p>Deze email is automatisch gegenereerd door het Asbest Tool systeem.</p>
                    <p>Voor vragen kunt u contact opnemen met uw systeembeheerder.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_report_notification_text(
        self,
        report: Report,
        user: User,
        status_text: str
    ) -> str:
        """Generate plain text content for report notification."""
        return f"""
Asbest Tool - Rapport Update

Beste {user.first_name} {user.last_name},

Uw rapport "{report.filename}" is {status_text}.

Rapport Details:
- Bestandsnaam: {report.filename}
- Status: {report.status.value}
- Geüpload op: {report.uploaded_at.strftime('%d-%m-%Y %H:%M') if report.uploaded_at else 'Onbekend'}
{f'- Score: {report.score}' if report.score is not None else ''}
{f'- Aantal bevindingen: {report.finding_count}' if report.finding_count else ''}
{f'- Bestandsgrootte: {self._format_file_size(report.file_size)}' if report.file_size else ''}

{f'Samenvatting: {report.summary}' if report.summary else ''}

{f'Foutmelding: {report.error_message}' if report.error_message else ''}

U kunt het rapport bekijken en downloaden via de Asbest Tool applicatie.

---
Deze email is automatisch gegenereerd door het Asbest Tool systeem.
Voor vragen kunt u contact opnemen met uw systeembeheerder.
        """
    
    def _format_file_size(self, size_bytes: Optional[int]) -> str:
        """Format file size in human readable format."""
        if not size_bytes:
            return "Onbekend"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


# Global email service instance
email_service = EmailService()