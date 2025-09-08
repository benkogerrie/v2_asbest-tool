#!/usr/bin/env python3
"""
Create a test PDF with asbest-related content for testing the AI analysis pipeline
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def create_test_asbest_pdf():
    """Create a test PDF with asbest inventory content"""
    
    # Create PDF file
    filename = "test_asbest_rapport.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkred
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("ASBEST INVENTARISATIE RAPPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Header information
    header_data = [
        ['Locatie:', 'Test Gebouw, Amsterdam'],
        ['Adres:', 'Teststraat 123, 1000 AB Amsterdam'],
        ['Datum onderzoek:', '15 januari 2024'],
        ['Inspecteur:', 'Jan de Vries'],
        ['Certificaat:', 'ASC-2024-001'],
        ['Opdrachtgever:', 'Test B.V.']
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("SAMENVATTING", heading_style))
    story.append(Paragraph(
        "Dit rapport bevat een inventarisatie van asbesthoudende materialen in het onderzochte gebouw. "
        "Het onderzoek is uitgevoerd conform de Nederlandse wet- en regelgeving voor asbestinventarisatie. "
        "Er zijn verschillende materialen gevonden die asbest bevatten en die een risico kunnen vormen voor "
        "de gezondheid van bewoners en werknemers.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    
    # Scope
    story.append(Paragraph("SCOPE VAN ONDERZOEK", heading_style))
    story.append(Paragraph(
        "Het onderzoek omvat een visuele inspectie van alle toegankelijke delen van het gebouw, "
        "inclusief technische ruimtes, kruipruimtes en zolders. Er zijn monsters genomen van verdachte "
        "materialen voor laboratoriumanalyse.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    
    # Findings
    story.append(Paragraph("BEVINDINGEN", heading_style))
    
    findings_data = [
        ['Locatie', 'Materiaal', 'Type Asbest', 'Conditie', 'Risico'],
        ['Dak', 'Asbestcementplaten', 'Chrysotiel', 'Slecht', 'KRITIEK'],
        ['CV-ruimte', 'Asbestisolatie leidingen', 'Chrysotiel', 'Matig', 'HOOG'],
        ['Vloer', 'Asbesthoudende vloerbedekking', 'Chrysotiel', 'Goed', 'MEDIUM'],
        ['Wand', 'Asbesthoudende lijm', 'Chrysotiel', 'Slecht', 'HOOG'],
        ['Plafond', 'Asbesthoudende plafondplaten', 'Chrysotiel', 'Matig', 'MEDIUM']
    ]
    
    findings_table = Table(findings_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(findings_table)
    story.append(Spacer(1, 12))
    
    # Risk Assessment
    story.append(Paragraph("RISICOBEOORDELING", heading_style))
    story.append(Paragraph(
        "De gevonden asbesthoudende materialen zijn beoordeeld op basis van hun conditie, "
        "toegankelijkheid en het risico op vezelvrijstelling. Materialen in slechte conditie "
        "of met een hoog risico op beschadiging zijn als kritiek geclassificeerd.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    
    # Recommendations
    story.append(Paragraph("AANBEVELINGEN", heading_style))
    recommendations = [
        "Directe verwijdering van kritieke asbesthoudende materialen",
        "Professionele sanering door gecertificeerd bedrijf",
        "Periodieke controle van overige asbesthoudende materialen",
        "Informatieverstrekking aan bewoners en werknemers",
        "Opstellen van beheersplan voor asbesthoudende materialen"
    ]
    
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Legal Framework
    story.append(Paragraph("WETTELIJK KADER", heading_style))
    story.append(Paragraph(
        "Dit onderzoek is uitgevoerd conform de Arbowet, het Asbestbesluit en de "
        "NEN 2990 norm voor asbestinventarisatie. Alle bevindingen zijn gedocumenteerd "
        "volgens de geldende richtlijnen.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    
    # Signature
    story.append(Paragraph("HANDTEKENING", heading_style))
    story.append(Paragraph("Inspecteur: Jan de Vries", normal_style))
    story.append(Paragraph("Certificaat: ASC-2024-001", normal_style))
    story.append(Paragraph("Datum: 15 januari 2024", normal_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Test PDF created: {filename}")
    print(f"📄 File size: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    create_test_asbest_pdf()
