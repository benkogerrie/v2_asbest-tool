"""
E-mail service for sending invitations and notifications.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import secrets
import string

from app.config import settings


class EmailService:
    """Service for sending e-mails."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        self.from_email = getattr(settings, 'from_email', 'noreply@asbest-tool.nl')
        self.from_name = getattr(settings, 'from_name', 'Asbest Tool')
    
    def generate_temp_password(self, length: int = 12) -> str:
        """Generate a temporary password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an e-mail."""
        if not self.smtp_username or not self.smtp_password:
            print(f"⚠️  E-mail not configured. Would send to {to_email}: {subject}")
            return True  # Return True for development
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ E-mail sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send e-mail to {to_email}: {e}")
            return False
    
    def send_tenant_admin_invitation(self, admin_email: str, admin_name: str, tenant_name: str, temp_password: str) -> bool:
        """Send tenant admin invitation e-mail."""
        subject = f"Uitnodiging voor {tenant_name} - Asbest Tool"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Uitnodiging Asbest Tool</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2b63ff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #2b63ff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .credentials {{ background: #e8f4fd; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welkom bij Asbest Tool</h1>
                </div>
                <div class="content">
                    <h2>Hallo {admin_name},</h2>
                    
                    <p>Je bent uitgenodigd als <strong>Tenant Admin</strong> voor <strong>{tenant_name}</strong> in de Asbest Tool applicatie.</p>
                    
                    <div class="credentials">
                        <h3>🔐 Je inloggegevens:</h3>
                        <p><strong>E-mail:</strong> {admin_email}</p>
                        <p><strong>Tijdelijk wachtwoord:</strong> <code>{temp_password}</code></p>
                    </div>
                    
                    <p><strong>Belangrijk:</strong> Wijzig je wachtwoord na de eerste inlog.</p>
                    
                    <div style="text-align: center;">
                        <a href="https://v2asbest-tool-production.up.railway.app/ui/auth/" class="button">
                            🚀 Inloggen op Asbest Tool
                        </a>
                    </div>
                    
                    <h3>Wat kun je doen?</h3>
                    <ul>
                        <li>📊 Rapporten uploaden en beheren</li>
                        <li>👥 Gebruikers uitnodigen voor jouw organisatie</li>
                        <li>📈 Analyses en bevindingen bekijken</li>
                        <li>⚙️ Organisatiegegevens beheren</li>
                    </ul>
                    
                    <p>Heb je vragen? Neem contact op met de system owner.</p>
                </div>
                <div class="footer">
                    <p>© 2025 Asbest Tool - Professionele asbest analyse</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welkom bij Asbest Tool!
        
        Hallo {admin_name},
        
        Je bent uitgenodigd als Tenant Admin voor {tenant_name} in de Asbest Tool applicatie.
        
        Je inloggegevens:
        - E-mail: {admin_email}
        - Tijdelijk wachtwoord: {temp_password}
        
        Belangrijk: Wijzig je wachtwoord na de eerste inlog.
        
        Inloggen: https://v2asbest-tool-production.up.railway.app/ui/auth/
        
        Wat kun je doen?
        - Rapporten uploaden en beheren
        - Gebruikers uitnodigen voor jouw organisatie
        - Analyses en bevindingen bekijken
        - Organisatiegegevens beheren
        
        Heb je vragen? Neem contact op met de system owner.
        
        © 2025 Asbest Tool
        """
        
        return self.send_email(admin_email, subject, html_content, text_content)


# Global instance
email_service = EmailService()
