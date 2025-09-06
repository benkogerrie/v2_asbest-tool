"""
ReportLab-based conclusion PDF generator.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Severity color mapping
SEVERITY_COLOR = {
    "CRITICAL": colors.HexColor("#b71c1c"),
    "HIGH": colors.HexColor("#e65100"),
    "MEDIUM": colors.HexColor("#f9a825"),
    "LOW": colors.HexColor("#2e7d32"),
}


def build_conclusion_pdf(output_path: Path, meta: Dict, findings: List[Dict]) -> None:
    """
    Build conclusion PDF using ReportLab.
    
    Args:
        output_path: Path where PDF will be saved
        meta: Metadata dictionary with report info
        findings: List of finding dictionaries
    """
    try:
        # Create document
        doc = SimpleDocTemplate(
            str(output_path), 
            pagesize=A4, 
            leftMargin=36, 
            rightMargin=36, 
            topMargin=40, 
            bottomMargin=36
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleBig", 
            parent=styles["Title"], 
            fontSize=20, 
            leading=24
        )
        h2_style = ParagraphStyle(
            "H2", 
            parent=styles["Heading2"], 
            spaceAfter=6
        )
        normal_style = styles["BodyText"]
        
        # Build story
        story = []
        
        # Header
        story.append(Paragraph("Asbest Tool – Conclusie", title_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Rapport:</b> {meta.get('report_name', '-')} &nbsp;&nbsp; "
            f"<b>Tenant:</b> {meta.get('tenant_name', '-')}", 
            normal_style
        ))
        story.append(Paragraph(
            f"<b>Score:</b> {meta.get('score', '-')} &nbsp;&nbsp; "
            f"<b>Engine:</b> {meta.get('engine', '-')} ({meta.get('engine_version', '-')})", 
            normal_style
        ))
        story.append(Paragraph(
            f"<b>Gegenereerd:</b> {meta.get('generated_at', '-')} &nbsp;&nbsp; "
            f"<b>Analyse ID:</b> {meta.get('analysis_id', '-')}", 
            normal_style
        ))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Samenvatting", h2_style))
        story.append(Paragraph(meta.get("summary", "-"), normal_style))
        story.append(Spacer(1, 12))
        
        # Findings table
        if findings:
            table_data = [["Severity", "Rule", "Section", "Message", "Suggestion"]]
            for finding in findings:
                table_data.append([
                    finding.get("severity", ""),
                    finding.get("rule_id", ""),
                    finding.get("section", "") or "",
                    finding.get("message", ""),
                    finding.get("suggestion", "") or "",
                ])
            
            # Create table
            table = Table(
                table_data, 
                repeatRows=1, 
                colWidths=[65, 55, 85, None, None]
            )
            
            # Table style
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
            
            # Add severity color bands
            for row_idx, row in enumerate(table_data[1:], start=1):
                severity = row[0]
                bg_color = SEVERITY_COLOR.get(severity, colors.whitesmoke)
                table_style.add("TEXTCOLOR", (0, row_idx), (0, row_idx), colors.white)
                table_style.add("BACKGROUND", (0, row_idx), (0, row_idx), bg_color)
            
            table.setStyle(table_style)
            story.append(Paragraph("Bevindingen", h2_style))
            story.append(table)
        else:
            story.append(Paragraph("Bevindingen", h2_style))
            story.append(Paragraph("Geen bevindingen gevonden.", normal_style))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF generated successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise Exception(f"PDF generation failed: {e}")
