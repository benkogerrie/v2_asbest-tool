"""
Analysis model for rule-based analysis results.
"""
import uuid
import datetime as dt
from sqlalchemy import Column, Text, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    """Analysis model for storing analysis results."""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), index=True, nullable=False)
    engine = Column(Text, nullable=False)  # "rules"
    engine_version = Column(Text, nullable=False)  # "rules-1.0.0"
    score = Column(Numeric(5,2), nullable=False)
    summary = Column(Text, nullable=False)
    rules_passed = Column(Integer, nullable=False, default=0)
    rules_failed = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=False, default=dt.datetime.utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=False, default=dt.datetime.utcnow)
    duration_ms = Column(Integer, nullable=False, default=0)
    raw_metadata = Column(JSONB)
    
    # Relationships
    findings = relationship("Finding", cascade="all, delete-orphan", backref="analysis")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, report_id={self.report_id}, engine={self.engine}, score={self.score})>"
