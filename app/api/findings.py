"""
Findings API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List, Literal, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.finding import Finding
from app.models.analysis import Analysis
from app.models.report import Report
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/reports/{report_id}/findings")
async def list_findings(
    report_id: UUID,
    severity: Optional[List[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]]] = Query(default=None),
    rule_id: Optional[List[str]] = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
):
    """List findings for a report with optional filtering."""
    # First check if user has access to the report
    report = session.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # TODO: Add multi-tenant access check
    # For now, allow access to all reports
    
    # Get latest analysis for this report
    latest_analysis = session.query(Analysis).filter(
        Analysis.report_id == report_id
    ).order_by(Analysis.finished_at.desc()).first()
    
    if not latest_analysis:
        return []
    
    # Query findings for the latest analysis
    query = session.query(Finding).filter(Finding.analysis_id == latest_analysis.id)
    
    # Apply filters
    if severity:
        query = query.filter(Finding.severity.in_(severity))
    if rule_id:
        query = query.filter(Finding.rule_id.in_(rule_id))
    
    findings = query.all()
    
    return [{
        "id": str(f.id),
        "rule_id": f.rule_id,
        "section": f.section,
        "severity": f.severity,
        "message": f.message,
        "suggestion": f.suggestion,
        "evidence": f.evidence,
        "tags": f.tags,
    } for f in findings]
