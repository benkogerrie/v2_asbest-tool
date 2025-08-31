"""
Report models for file uploads and processing.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class ReportStatus(str, Enum):
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"
    DELETED_SOFT = "DELETED_SOFT"


class AuditAction(str, Enum):
    UPLOAD = "UPLOAD"
    PROCESS_START = "PROCESS_START"
    PROCESS_DONE = "PROCESS_DONE"
    PROCESS_FAIL = "PROCESS_FAIL"
    SOFT_DELETE = "SOFT_DELETE"
    RESTORE = "RESTORE"


class Report(Base):
    """Report model for uploaded files."""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PROCESSING, nullable=False)
    score = Column(Float, nullable=True)
    finding_count = Column(Integer, default=0, nullable=False)
    summary = Column(Text, nullable=True)
    findings_json = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_object_key = Column(String, nullable=False)
    conclusion_object_key = Column(String, nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="reports")
    uploaded_by_user = relationship("User", back_populates="reports")
    audit_logs = relationship("ReportAuditLog", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Report(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class ReportAuditLog(Base):
    """Audit log for report actions."""
    __tablename__ = "report_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(SQLEnum(AuditAction), nullable=False)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    report = relationship("Report", back_populates="audit_logs")
    actor_user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<ReportAuditLog(id={self.id}, action='{self.action}', created_at='{self.created_at}')>"
