"""
Report service for database queries and business logic.
"""
import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportStatus
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.schemas.report import ReportListItem, ReportDetail


class ReportService:
    """Service for report-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_reports_with_filters(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ReportStatus] = None,
        tenant_id: Optional[str] = None,
        q: Optional[str] = None,
        sort: str = "uploaded_at_desc"
    ) -> Tuple[List[ReportListItem], int]:
        """
        Get reports with filtering, sorting and pagination.
        
        Args:
            current_user: Current authenticated user
            page: Page number (1-based)
            page_size: Items per page (max 100)
            status: Filter by status
            tenant_id: Filter by tenant (only for SYSTEM_OWNER)
            q: Search query for filename
            sort: Sort order
            
        Returns:
            Tuple of (reports, total_count)
        """
        # Validate page_size
        page_size = min(page_size, 100)
        page_size = max(page_size, 1)
        
        # Build base query
        query = select(Report)
        
        # Add tenant join for SYSTEM_OWNER to get tenant_name
        if current_user.role == UserRole.SYSTEM_OWNER:
            query = query.outerjoin(Tenant, Report.tenant_id == Tenant.id)
        
        # Apply RBAC filters
        if current_user.role == UserRole.SYSTEM_OWNER:
            # SYSTEM_OWNER can see all reports, including soft-deleted
            # Only filter by tenant_id if explicitly provided
            if tenant_id:
                query = query.where(Report.tenant_id == uuid.UUID(tenant_id))
        else:
            # USER/ADMIN can only see reports from their tenant, excluding soft-deleted
            query = query.where(
                and_(
                    Report.tenant_id == current_user.tenant_id,
                    Report.status != ReportStatus.DELETED_SOFT
                )
            )
        
        # Apply status filter
        if status:
            query = query.where(Report.status == status)
        
        # Apply search filter
        if q:
            query = query.where(Report.filename.ilike(f"%{q}%"))
        
        # Get total count with same filters
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        if sort == "uploaded_at_asc":
            query = query.order_by(asc(Report.uploaded_at))
        elif sort == "filename_asc":
            query = query.order_by(asc(Report.filename))
        elif sort == "filename_desc":
            query = query.order_by(desc(Report.filename))
        else:  # uploaded_at_desc (default)
            query = query.order_by(desc(Report.uploaded_at))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await self.session.execute(query)
        reports = result.scalars().all()
        
        # Convert to DTOs
        report_items = []
        for report in reports:
            tenant_name = None
            if current_user.role == UserRole.SYSTEM_OWNER:
                # For SYSTEM_OWNER, we need to check if tenant was loaded
                if hasattr(report, 'tenant') and report.tenant is not None:
                    tenant_name = report.tenant.name
            
            report_item = ReportListItem(
                id=str(report.id),
                filename=report.filename,
                status=report.status,
                finding_count=report.finding_count,
                score=int(report.score) if report.score else None,
                uploaded_at=report.uploaded_at,
                tenant_name=tenant_name
            )
            report_items.append(report_item)
        
        return report_items, total
    
    async def get_report_detail(
        self,
        report_id: str,
        current_user: User
    ) -> Optional[ReportDetail]:
        """
        Get detailed report information.
        
        Args:
            report_id: Report ID
            current_user: Current authenticated user
            
        Returns:
            ReportDetail or None if not found/accessible
        """
        # Build query with joins for tenant and user information
        query = select(Report).options(
            selectinload(Report.tenant),
            selectinload(Report.uploaded_by_user)
        ).where(Report.id == uuid.UUID(report_id))
        
        result = await self.session.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Check RBAC access
        if current_user.role == UserRole.SYSTEM_OWNER:
            # SYSTEM_OWNER can see all reports
            pass
        else:
            # USER/ADMIN can only see reports from their tenant, excluding soft-deleted
            if (report.tenant_id != current_user.tenant_id or 
                report.status == ReportStatus.DELETED_SOFT):
                return None
        
        # Build uploaded_by_name
        uploaded_by_name = None
        if report.uploaded_by_user:
            first_name = report.uploaded_by_user.first_name or ""
            last_name = report.uploaded_by_user.last_name or ""
            uploaded_by_name = f"{first_name} {last_name}".strip()
        
        # Build tenant_name (only for SYSTEM_OWNER)
        tenant_name = None
        if current_user.role == UserRole.SYSTEM_OWNER and report.tenant:
            tenant_name = report.tenant.name
        
        # Create ReportDetail with placeholders for summary and findings
        report_detail = ReportDetail(
            id=str(report.id),
            filename=report.filename,
            summary="Nog geen conclusie beschikbaar",  # Placeholder until Slice 4
            findings=[],  # Placeholder until Slice 4
            uploaded_at=report.uploaded_at,
            uploaded_by_name=uploaded_by_name,
            tenant_name=tenant_name,
            status=report.status,
            finding_count=report.finding_count,
            score=int(report.score) if report.score else None
        )
        
        return report_detail
