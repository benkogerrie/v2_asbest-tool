"""
Report schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.report import ReportStatus


class ReportBase(BaseModel):
    """Base report schema."""
    filename: str = Field(..., description="Original filename")
    status: ReportStatus = Field(ReportStatus.PROCESSING, description="Processing status")
    finding_count: int = Field(0, description="Number of findings detected")
    score: Optional[float] = Field(None, description="Risk score (0-100)")
    source_object_key: str = Field(..., description="Storage key for source file")
    conclusion_object_key: Optional[str] = Field(None, description="Storage key for conclusion file")


class ReportCreate(ReportBase):
    """Schema for creating a report."""
    tenant_id: str = Field(..., description="Tenant ID")
    uploaded_by: str = Field(..., description="User ID who uploaded the file")


class ReportOut(ReportBase):
    """Schema for report responses."""
    id: str = Field(..., description="Report ID")
    tenant_id: str = Field(..., description="Tenant ID")
    uploaded_by: str = Field(..., description="User ID who uploaded the file")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        from_attributes = True


class ReportAuditLogBase(BaseModel):
    """Base audit log schema."""
    action: str = Field(..., description="Action performed")
    note: Optional[str] = Field(None, description="Additional notes")


class ReportAuditLogCreate(ReportAuditLogBase):
    """Schema for creating an audit log entry."""
    report_id: str = Field(..., description="Report ID")
    actor_user_id: Optional[str] = Field(None, description="User ID who performed the action")


class ReportAuditLogOut(ReportAuditLogBase):
    """Schema for audit log responses."""
    id: str = Field(..., description="Audit log ID")
    report_id: str = Field(..., description="Report ID")
    actor_user_id: Optional[str] = Field(None, description="User ID who performed the action")
    created_at: datetime = Field(..., description="Action timestamp")
    
    class Config:
        from_attributes = True
