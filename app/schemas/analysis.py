"""
Analysis schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Literal, Optional
from uuid import UUID
from datetime import datetime


class FindingDTO(BaseModel):
    """Finding data transfer object."""
    id: Optional[UUID] = None
    rule_id: str
    section: Optional[str] = None
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    message: str
    suggestion: Optional[str] = None
    evidence: Optional[dict] = None
    tags: Optional[List[str]] = None


class AnalysisDTO(BaseModel):
    """Analysis data transfer object."""
    id: Optional[UUID] = None
    report_id: UUID
    engine: str
    engine_version: str
    score: float
    summary: str
    rules_passed: int
    rules_failed: int
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    findings: List[FindingDTO] = []
