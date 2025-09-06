"""
Rule-based analyzer for asbest reports.
"""
import time
import datetime as dt
from typing import List
from uuid import UUID

from app.schemas.analysis import AnalysisDTO, FindingDTO
from app.services.analyzer.scoring import compute_score

# Rules version
RULES_VERSION = "rules-1.0.0"


def _has_any(text: str, terms: List[str]) -> bool:
    """Check if text contains any of the given terms."""
    text_lower = text.lower()
    return any(term.lower() in text_lower for term in terms)


def run_rules_v1(text: str) -> List[FindingDTO]:
    """
    Run rule-based analysis on extracted text.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        List of findings
    """
    findings: List[FindingDTO] = []
    
    # R-001 Missing Project Info (MEDIUM)
    required_project_terms = ["project", "opdrachtgever", "adres", "inspectiedatum", "uitvoerder"]
    if not _has_any(text, required_project_terms):
        findings.append(FindingDTO(
            rule_id="R-001",
            section="Project info",
            severity="MEDIUM",
            message="Projectgegevens onvolledig of niet aangetroffen.",
            suggestion="Voeg sectie 'Projectgegevens' toe met projectnaam/adres, opdrachtgever, uitvoerder en inspectiedatum.",
            evidence={"required": required_project_terms},
            tags=["completeness"]
        ))
    
    # R-002 Missing Inspector License (HIGH)
    license_terms = ["licentie", "certificaat", "certificaatnummer", "certificate", "license"]
    if not _has_any(text, license_terms):
        findings.append(FindingDTO(
            rule_id="R-002",
            section="Kwalificaties",
            severity="HIGH",
            message="Inspecteurslicentie/certificaat niet gevonden.",
            suggestion="Vermeld naam inspecteur, certificaatnummer en geldigheid.",
            tags=["legal", "compliance"]
        ))
    
    # R-003 Risk Class Inconsistency (HIGH)
    risk_terms = ["risicoklasse", "risk class", "risk category"]
    norm_terms = ["nen", "en ", "norm", "richtlijn"]
    has_risk = _has_any(text, risk_terms)
    has_norm = _has_any(text, norm_terms)
    if has_risk and not has_norm:
        findings.append(FindingDTO(
            rule_id="R-003",
            section="Risico",
            severity="HIGH",
            message="Risicoklasse genoemd, maar ontbrekende onderbouwing met norm.",
            suggestion="Onderbouw risicoklasse met methode en verwijzing naar relevante norm.",
            tags=["consistency"]
        ))
    
    # R-004 Inventory Table Completeness (MEDIUM)
    inventory_terms = ["inventaris", "tabel", "locatie", "materiaal", "hoeveelheid", "toestand", "foto"]
    if not _has_any(text, inventory_terms):
        findings.append(FindingDTO(
            rule_id="R-004",
            section="Inventaris",
            severity="MEDIUM",
            message="Inventarisatietabel lijkt onvolledig of ontbreekt.",
            suggestion="Neem tabel op met: locatie, materiaaltype, hechtgebondenheid, hoeveelheid, toestand, foto-referenties.",
            tags=["completeness"]
        ))
    
    # R-005 Lab Results Referenced (MEDIUM)
    lab_terms = ["lab", "laboratorium", "rapport", "analyse", "monsterneming", "sample", "rapportnummer"]
    if not _has_any(text, lab_terms):
        findings.append(FindingDTO(
            rule_id="R-005",
            section="Lab",
            severity="MEDIUM",
            message="Laboratoriumverwijzingen ontbreken of zijn onvolledig.",
            suggestion="Verwijs naar laboratoriumrapport met nummer, methode, datum en uitslag.",
            tags=["traceability"]
        ))
    
    # R-006 Photo Evidence Mismatch (LOW)
    photo_terms = ["foto", "figuur", "afbeelding", "image"]
    if not _has_any(text, photo_terms):
        findings.append(FindingDTO(
            rule_id="R-006",
            section="Bewijs",
            severity="LOW",
            message="Fotobewijs niet aangetroffen.",
            suggestion="Voorzie inventarisitems van duidelijke foto's met captions en locatie-referentie.",
            tags=["evidence"]
        ))
    
    # R-007 Conclusion Structure (LOW)
    conclusion_terms = ["conclusie", "samenvatting", "aanbeveling"]
    if not _has_any(text, conclusion_terms):
        findings.append(FindingDTO(
            rule_id="R-007",
            section="Conclusie",
            severity="LOW",
            message="Conclusie/samenvatting ontbreekt of is te summier.",
            suggestion="Breid de conclusie uit met samenvatting en aanbevelingen.",
            tags=["structure"]
        ))
    
    # R-008 Legal Reference Present (MEDIUM)
    legal_terms = ["wet", "regelgeving", "richtlijn", "norm", "compliance"]
    if not _has_any(text, legal_terms):
        findings.append(FindingDTO(
            rule_id="R-008",
            section="Juridisch",
            severity="MEDIUM",
            message="Geen verwijzing naar toepasselijke normen/wetgeving.",
            suggestion="Voeg verwijzing toe naar relevante wet- en regelgeving/richtlijnen.",
            tags=["legal"]
        ))
    
    return findings


def analyze_text_to_result(report_id: UUID, text: str) -> AnalysisDTO:
    """
    Analyze text and return analysis result.
    
    Args:
        report_id: Report UUID
        text: Extracted text from PDF
        
    Returns:
        Analysis result with findings
    """
    start_time = time.time()
    
    # Run rules analysis
    findings = run_rules_v1(text)
    
    # Compute score
    findings_dict = [f.dict() for f in findings]
    score = compute_score(findings_dict)
    
    # Calculate metrics
    rules_passed = 0  # For now, we only track failed rules
    rules_failed = len(findings)
    
    # Generate summary
    summary = "Automatische regelgebaseerde screening uitgevoerd. Belangrijkste aandachtspunten uitgelicht; zie tabel voor details en vervolgstappen."
    
    end_time = time.time()
    duration_ms = int((end_time - start_time) * 1000)
    
    return AnalysisDTO(
        report_id=report_id,
        engine="rules",
        engine_version=RULES_VERSION,
        score=round(score, 2),
        summary=summary,
        rules_passed=rules_passed,
        rules_failed=rules_failed,
        started_at=dt.datetime.utcfromtimestamp(start_time),
        finished_at=dt.datetime.utcfromtimestamp(end_time),
        duration_ms=duration_ms,
        findings=findings
    )
