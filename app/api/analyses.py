"""
Analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.analysis import Analysis
from app.models.report import Report
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("/reports/{report_id}/analysis")
async def get_latest_analysis(
    report_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Get the latest analysis for a report."""
    # First check if user has access to the report
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # TODO: Add multi-tenant access check
    # For now, allow access to all reports
    
    # Get latest analysis
    result = await session.execute(select(Analysis).where(
        Analysis.report_id == report_id
    ).order_by(Analysis.finished_at.desc()))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        return None
    
    return {
        "id": str(analysis.id),
        "report_id": str(analysis.report_id),
        "engine": analysis.engine,
        "engine_version": analysis.engine_version,
        "score": float(analysis.score),
        "summary": analysis.summary,
        "rules_passed": analysis.rules_passed,
        "rules_failed": analysis.rules_failed,
        "started_at": analysis.started_at.isoformat(),
        "finished_at": analysis.finished_at.isoformat(),
        "duration_ms": analysis.duration_ms,
    }
