"""
PDF generation for report conclusions using WeasyPrint.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Template

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def generate_conclusion_pdf(
    filename: str,
    summary: str,
    findings: List[Dict[str, Any]],
    report_id: uuid.UUID,
    timestamp: datetime
) -> bytes:
    """
    Generate a conclusion PDF using WeasyPrint.
    
    Args:
        filename: Original report filename
        summary: Report summary text
        findings: List of findings with code, severity, title, detail_text
        report_id: Report UUID
        timestamp: Processing timestamp
        
    Returns:
        bytes: PDF content
    """
    # HTML template for the PDF
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Conclusie & Aanbevelingen</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }
            .header {
                text-align: center;
                border-bottom: 3px solid #2c3e50;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #2c3e50;
                margin: 0;
                font-size: 28px;
            }
            .project-info {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 25px;
            }
            .project-info h3 {
                margin-top: 0;
                color: #495057;
            }
            .summary-section {
                margin-bottom: 30px;
            }
            .summary-section h3 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
            }
            .findings-section h3 {
                color: #2c3e50;
                border-bottom: 2px solid #e74c3c;
                padding-bottom: 5px;
            }
            .finding {
                margin-bottom: 20px;
                padding: 15px;
                border-left: 4px solid #e74c3c;
                background-color: #fff5f5;
            }
            .finding-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .finding-code {
                font-weight: bold;
                color: #e74c3c;
                font-size: 14px;
            }
            .finding-severity {
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .severity-major {
                background-color: #f39c12;
                color: white;
            }
            .severity-critical {
                background-color: #e74c3c;
                color: white;
            }
            .severity-minor {
                background-color: #f1c40f;
                color: #2c3e50;
            }
            .severity-info {
                background-color: #3498db;
                color: white;
            }
            .finding-title {
                font-weight: bold;
                margin-bottom: 5px;
                color: #2c3e50;
            }
            .finding-detail {
                color: #555;
                font-size: 14px;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Conclusie & Aanbevelingen</h1>
        </div>
        
        <div class="project-info">
            <h3>Project Informatie</h3>
            <p><strong>Bestandsnaam:</strong> {{ filename }}</p>
            <p><strong>Rapport ID:</strong> {{ report_id }}</p>
            <p><strong>Verwerkt op:</strong> {{ timestamp.strftime('%d-%m-%Y %H:%M:%S') }}</p>
        </div>
        
        <div class="summary-section">
            <h3>Samenvatting</h3>
            <p>{{ summary }}</p>
        </div>
        
        <div class="findings-section">
            <h3>Bevindingen ({{ findings|length }} gevonden)</h3>
            {% for finding in findings %}
            <div class="finding">
                <div class="finding-header">
                    <span class="finding-code">{{ finding.code }}</span>
                    <span class="finding-severity severity-{{ finding.severity.lower() }}">
                        {{ finding.severity }}
                    </span>
                </div>
                <div class="finding-title">{{ finding.title }}</div>
                <div class="finding-detail">{{ finding.detail_text }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Dit rapport is automatisch gegenereerd door het Asbest Tool systeem.</p>
            <p>Rapport ID: {{ report_id }} | Verwerkt op: {{ timestamp.strftime('%d-%m-%Y %H:%M:%S') }}</p>
        </div>
    </body>
    </html>
    """
    
    # Render template
    template = Template(html_template)
    html_content = template.render(
        filename=filename,
        report_id=str(report_id),
        timestamp=timestamp,
        summary=summary,
        findings=findings
    )
    
    # Generate PDF with multiple fallback strategies
    import logging
    logger = logging.getLogger(__name__)
    
    # Strategy 1: Try with CSS and font config
    try:
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        css = CSS(string='', font_config=font_config)
        pdf_bytes = html.write_pdf(stylesheets=[css], font_config=font_config)
        logger.info("PDF generated successfully with CSS and font config")
        return pdf_bytes
    except Exception as e1:
        logger.warning(f"PDF generation with CSS failed: {e1}, trying simple version")
        
        # Strategy 2: Try simple PDF without CSS
        try:
            html = HTML(string=html_content)
            pdf_bytes = html.write_pdf()
            logger.info("PDF generated successfully with simple method")
            return pdf_bytes
        except Exception as e2:
            logger.warning(f"Simple PDF generation failed: {e2}, trying minimal HTML")
            
            # Strategy 3: Try with minimal HTML (no complex styling)
            try:
                minimal_html = f"""
                <!DOCTYPE html>
                <html>
                <head><meta charset="UTF-8"><title>Conclusie</title></head>
                <body>
                    <h1>Conclusie & Aanbevelingen</h1>
                    <p><strong>Bestandsnaam:</strong> {filename}</p>
                    <p><strong>Rapport ID:</strong> {report_id}</p>
                    <p><strong>Verwerkt op:</strong> {timestamp.strftime('%d-%m-%Y %H:%M:%S')}</p>
                    <h2>Samenvatting</h2>
                    <p>{summary}</p>
                    <h2>Bevindingen ({len(findings)} gevonden)</h2>
                    {"".join([f"<p><strong>{f['code']} - {f['severity']}:</strong> {f['title']}<br>{f['detail_text']}</p>" for f in findings])}
                </body>
                </html>
                """
                html = HTML(string=minimal_html)
                pdf_bytes = html.write_pdf()
                logger.info("PDF generated successfully with minimal HTML")
                return pdf_bytes
            except Exception as e3:
                logger.error(f"All PDF generation strategies failed: {e3}")
                raise Exception(f"PDF generation failed after all fallback attempts: {e3}")
