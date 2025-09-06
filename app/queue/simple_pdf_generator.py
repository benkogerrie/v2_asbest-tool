"""
Simple PDF generator using reportlab as fallback for WeasyPrint issues.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_simple_pdf(
    filename: str,
    summary: str,
    findings: List[Dict[str, Any]],
    report_id: uuid.UUID,
    timestamp: datetime
) -> bytes:
    """
    Generate a simple PDF using reportlab as fallback.
    
    Args:
        filename: Original report filename
        summary: Report summary text
        findings: List of findings with code, severity, title, detail_text
        report_id: Report UUID
        timestamp: Processing timestamp
        
    Returns:
        bytes: PDF content
    """
    if not REPORTLAB_AVAILABLE:
        raise Exception("ReportLab not available - cannot generate PDF")
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("Conclusie & Aanbevelingen", title_style))
    story.append(Spacer(1, 20))
    
    # Project info
    story.append(Paragraph("Project Informatie", heading_style))
    project_data = [
        ["Bestandsnaam:", filename],
        ["Rapport ID:", str(report_id)],
        ["Verwerkt op:", timestamp.strftime('%d-%m-%Y %H:%M:%S')]
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(project_table)
    story.append(Spacer(1, 20))
    
    # Summary
    story.append(Paragraph("Samenvatting", heading_style))
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Findings
    story.append(Paragraph(f"Bevindingen ({len(findings)} gevonden)", heading_style))
    
    for finding in findings:
        # Finding header
        finding_text = f"<b>{finding['code']} - {finding['severity']}:</b> {finding['title']}"
        story.append(Paragraph(finding_text, styles['Normal']))
        
        # Finding detail
        story.append(Paragraph(finding['detail_text'], styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"Dit rapport is automatisch gegenereerd door het Asbest Tool systeem.<br/>Rapport ID: {report_id} | Verwerkt op: {timestamp.strftime('%d-%m-%Y %H:%M:%S')}"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
