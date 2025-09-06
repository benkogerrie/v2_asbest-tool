"""
Base analyzer interface.
"""
from typing import Protocol
from uuid import UUID
from app.schemas.analysis import AnalysisDTO


class AnalysisEngine(Protocol):
    """Protocol for analysis engines."""
    
    def analyze(self, report_id: UUID) -> AnalysisDTO:
        """Analyze a report and return results."""
        ...
