from __future__ import annotations
import os
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# NL-tekens ondersteunen
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

# ---------- Optioneel: Street View downloaden (als je niet met lokale file werkt) ----------

def download_streetview_image(
    out_path: str,
    *,
    api_key: str,
    lat: float,
    lng: float,
    heading: int = 0,
    pitch: int = 0,
    fov: int = 80,
    size: str = "640x400"
) -> str:
    """
    Download een Google Street View afbeelding via de Static API.
    - Vereist een geldige Google Maps Platform API Key met Street View Static API enabled.
    - Zorg voor correcte attributie in de PDF (© Google). Zie Google TOS.
    """
    import urllib.parse, urllib.request
    base = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": size, "location": f"{lat},{lng}", "heading": str(heading),
        "pitch": str(pitch), "fov": str(fov), "key": api_key
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    urllib.request.urlretrieve(url, out_path)
    return out_path

# ---------- PDF helpers ----------

def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontName="HeiseiMin-W3"))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontName="HeiseiMin-W3"))
    styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], fontName="HeiseiMin-W3"))
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontName="HeiseiMin-W3", leading=14))
    styles.add(ParagraphStyle(name="SmallMuted", parent=styles["Normal"], fontName="HeiseiMin-W3", fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name="Meta", parent=styles["Normal"], fontName="HeiseiMin-W3", leading=13))
    return styles

def _kv_table(data: Dict[str, str], col1=55*mm, col2=110*mm):
    rows = [[f"<b>{k}</b>", v] for k, v in data.items() if v is not None and v != ""]
    t = Table(rows, colWidths=[col1, col2])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "HeiseiMin-W3"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.whitesmoke, colors.white]),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
        ("BOX", (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def _findings_table(findings: List[Dict], max_snippet_chars: int = 140):
    data = [["Code", "Titel", "Status", "Severity", "Snippet"]]
    for f in findings:
        snippet = (f.get("evidence_snippet") or "").strip().replace("\n", " ")
        if len(snippet) > max_snippet_chars:
            snippet = snippet[:max_snippet_chars] + "…"
        data.append([
            f.get("code", ""),
            f.get("title", ""),
            f.get("status", ""),
            f.get("severity", ""),
            snippet or "—",
        ])

    table = Table(data, colWidths=[28*mm, 52*mm, 22*mm, 22*mm, 66*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0,0), (-1,-1), "HeiseiMin-W3"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,0), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return table

# ---------- Public API ----------

def build_pdf(
    *,
    filename: str = "qa_conclusie.pdf",
    # rapport-meta (vrij in te vullen, komt op de pagina)
    meta: Optional[Dict[str, str]] = None,
    # BAGviewer-gegevens (sleutels voorbeeld hieronder)
    bag: Optional[Dict[str, str]] = None,
    # Street View plaatje: pad naar lokaal bestand (PNG/JPG); of None om over te slaan
    streetview_image_path: Optional[str] = None,
    streetview_caption: Optional[str] = "Google Street View – vooraanzicht (© Google)",
    # QA-resultaten
    score: Optional[float] = None,
    findings: Optional[List[Dict]] = None,
    # Extra hoofdstukken die je later vult: [{"title": "...", "content": [Flowables...]}]
    extra_sections: Optional[List[Dict]] = None,
):
    styles = _styles()
    story = []

    # Titel
    story.append(Paragraph("QA-Conclusierapport Asbestinventarisatie", styles["H1"]))
    story.append(Spacer(1, 8))

    # Bronverwijzing Artikel 22
    bron = (
        "Eisen conform <b>artikel 22</b> van het Certificatieschema Asbestinventarisatie en Asbestverwijdering,<br/>"
        "Bekendmaking van de Minister van Sociale Zaken en Werkgelegenheid d.d. 23 juni 2023, "
        "kenmerk 2023-0000325925 (Stcrt.), vastgesteld door Stichting Ascert op 1 juni 2023."
    )
    story.append(Paragraph(bron, styles["Body"]))
    story.append(Spacer(1, 12))

    # Rapport-metadata (links klein blokje)
    if meta:
        story.append(Paragraph("<b>Rapportmetadata</b>", styles["H2"]))
        story.append(Spacer(1, 4))
        story.append(_kv_table(meta))
        story.append(Spacer(1, 10))

    # BAGviewer sectie
    if bag:
        story.append(Paragraph("<b>BAGviewer-gegevens</b>", styles["H2"]))
        story.append(Spacer(1, 4))
        # Voorstel keys (pas aan op jullie mapping):
        # "Adres", "Plaats", "Postcode", "BAG Pand-ID", "BAG VBO-ID", "Bouwjaar", "Oppervlakte (m²)", "Gebruiksdoel", "Status"
        story.append(_kv_table(bag))
        story.append(Spacer(1, 10))

    # Street View "voorfoto"
    if streetview_image_path and os.path.exists(streetview_image_path):
        story.append(Paragraph("<b>Voorfoto (Street View)</b>", styles["H2"]))
        story.append(Spacer(1, 4))
        try:
            img = Image(streetview_image_path)
            # schalen op paginabreedte met marge
            max_width = 180 * mm
            # behoud aspect ratio
            ratio = img.imageWidth / float(img.imageHeight)
            img.drawWidth = max_width
            img.drawHeight = max_width / ratio
            story.append(img)
            story.append(Spacer(1, 4))
            story.append(Paragraph(streetview_caption or "© Google", styles["SmallMuted"]))
        except Exception as e:
            story.append(Paragraph(f"<i>Afbeelding kon niet worden geladen: {e}</i>", styles["SmallMuted"]))
        story.append(Spacer(1, 10))

    # Score + Findings
    if score is not None:
        story.append(Paragraph(f"<b>Eindscore:</b> {int(round(score))}/100", styles["H2"]))
        story.append(Spacer(1, 6))

    if findings:
        story.append(Paragraph("<b>Conclusies volgens Artikel 22</b>", styles["H2"]))
        story.append(Spacer(1, 4))
        story.append(_findings_table(findings))
        story.append(Spacer(1, 10))

    # Extra secties (placeholder hoofdstukken)
    if extra_sections:
        for sec in extra_sections:
            title = sec.get("title", "").strip()
            content = sec.get("content", [])
            if title:
                story.append(PageBreak())
                story.append(Paragraph(title, styles["H2"]))
                story.append(Spacer(1, 6))
            if content:
                story.extend(content)

    # Document bouwen
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=18*mm, bottomMargin=18*mm, leftMargin=18*mm, rightMargin=18*mm
    )
    doc.build(story)

# ---------- Integration with AI Analysis ----------

def generate_conclusion_pdf(
    *,
    output_path: str,
    report_meta: Dict[str, str],
    ai_analysis: Dict,  # AIOutput from our analysis
    bag_data: Optional[Dict[str, str]] = None,
    streetview_path: Optional[str] = None
) -> str:
    """
    Generate conclusion PDF from AI analysis results.
    
    Args:
        output_path: Path where to save the PDF
        report_meta: Report metadata (opdrachtgever, projectnummer, etc.)
        ai_analysis: AI analysis results (score, findings, summary)
        bag_data: Optional BAG viewer data
        streetview_path: Optional path to street view image
    
    Returns:
        Path to generated PDF
    """
    
    # Convert AI findings to PDF format
    findings = []
    if ai_analysis.get("findings"):
        for finding in ai_analysis["findings"]:
            findings.append({
                "code": finding.get("code", ""),
                "title": finding.get("title", ""),
                "status": finding.get("status", ""),
                "severity": finding.get("severity", ""),
                "evidence_snippet": finding.get("evidence_snippet", "")
            })
    
    # Add extra sections with AI summary
    styles = _styles()
    extra_sections = [
        {
            "title": "AI Analyse Samenvatting",
            "content": [
                Paragraph(ai_analysis.get("report_summary", "Geen samenvatting beschikbaar."), styles["Body"]),
                Spacer(1, 6),
                Paragraph("Deze analyse is uitgevoerd met behulp van AI-gebaseerde kwaliteitscontrole volgens Artikel 22 van het Certificatieschema Asbestinventarisatie.", styles["SmallMuted"]),
            ],
        },
        {
            "title": "Methodiek QA",
            "content": [
                Paragraph("De kwaliteitscontrole is uitgevoerd volgens de eisen van Artikel 22 van het Certificatieschema Asbestinventarisatie en Asbestverwijdering.", styles["Body"]),
                Spacer(1, 6),
                Paragraph("De AI-analyse controleert 14 specifieke aspecten van het asbestinventarisatierapport, waaronder metadata, scope, methodiek, bevindingen, en aanbevelingen.", styles["Body"]),
            ],
        },
    ]
    
    # Generate PDF
    build_pdf(
        filename=output_path,
        meta=report_meta,
        bag=bag_data,
        streetview_image_path=streetview_path,
        streetview_caption="Voorafbeelding locatie (© Google)" if streetview_path else None,
        score=ai_analysis.get("score"),
        findings=findings,
        extra_sections=extra_sections,
    )
    
    return output_path

