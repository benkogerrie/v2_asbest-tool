"""
Finding model for storing analysis findings.
"""
import uuid
from sqlalchemy import Column, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base

# Define severity enum
SeverityEnum = Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity_enum")


class Finding(Base):
    """Finding model for storing individual analysis findings."""
    __tablename__ = "findings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), index=True, nullable=False)
    rule_id = Column(Text, nullable=False)
    section = Column(Text)
    severity = Column(SeverityEnum, nullable=False)
    message = Column(Text, nullable=False)
    suggestion = Column(Text)
    evidence = Column(JSONB)
    tags = Column(JSONB)
    
    def __repr__(self):
        return f"<Finding(id={self.id}, rule_id={self.rule_id}, severity={self.severity})>"
