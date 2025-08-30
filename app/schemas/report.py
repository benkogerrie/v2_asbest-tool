"""
Report schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Literal
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
        
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema with proper UUID handling."""
        data = {
            'id': str(obj.id),
            'tenant_id': str(obj.tenant_id),
            'uploaded_by': str(obj.uploaded_by),
            'uploaded_at': obj.uploaded_at,
            'filename': obj.filename,
            'status': obj.status,
            'finding_count': obj.finding_count,
            'score': obj.score,
            'source_object_key': obj.source_object_key,
            'conclusion_object_key': obj.conclusion_object_key
        }
        return cls(**data)


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


# Slice 3 schemas
class FindingItem(BaseModel):
    """Schema for individual findings."""
    code: str = Field(..., description="Finding code")
    severity: Literal['INFO', 'MINOR', 'MAJOR', 'CRITICAL'] = Field(..., description="Severity level")
    title: Optional[str] = Field(None, description="Finding title")
    detail_text: Optional[str] = Field(None, description="Detailed description")


class ReportListItem(BaseModel):
    """Schema for report list items."""
    id: str = Field(..., description="Report ID")
    filename: str = Field(..., description="Original filename")
    status: ReportStatus = Field(..., description="Processing status")
    finding_count: int = Field(..., description="Number of findings detected")
    score: Optional[float] = Field(None, description="Risk score (0-100)")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    tenant_name: Optional[str] = Field(None, description="Tenant name (only for SYSTEM_OWNER)")
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Schema for paginated report list response."""
    items: List[ReportListItem] = Field(..., description="List of reports")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of reports")


class ReportDetail(BaseModel):
    """Schema for detailed report view."""
    id: str = Field(..., description="Report ID")
    filename: str = Field(..., description="Original filename")
    summary: Optional[str] = Field(None, description="Report summary (placeholder until Slice 4)")
    findings: List[FindingItem] = Field(default_factory=list, description="List of findings (placeholder until Slice 4)")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    uploaded_by_name: Optional[str] = Field(None, description="Name of user who uploaded the file")
    tenant_name: Optional[str] = Field(None, description="Tenant name (only for SYSTEM_OWNER)")
    status: ReportStatus = Field(..., description="Processing status")
    finding_count: int = Field(..., description="Number of findings detected")
    score: Optional[float] = Field(None, description="Risk score (0-100)")
    
    class Config:
        from_attributes = True
