"""
Reports API endpoints for file uploads.
"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.models.report import Report, ReportAuditLog, ReportStatus, AuditAction
from app.schemas.report import ReportOut
from app.auth.dependencies import get_current_active_user, get_current_admin_or_system_owner
from app.services.storage import storage
from app.exceptions import UnsupportedFileTypeError, FileTooLargeError, StorageError
from app.config import settings

router = APIRouter(prefix="/reports", tags=["reports"])

# Allowed file extensions and their content types
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

# Maximum file size in bytes
MAX_FILE_SIZE = settings.max_upload_mb * 1024 * 1024


def validate_file_upload(file: UploadFile) -> None:
    """Validate file upload."""
    # Check file extension
    if not file.filename:
        raise UnsupportedFileTypeError("No filename provided")
    
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if f'.{file_ext}' not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}")
    
    # Check content type
    if file.content_type not in ALLOWED_EXTENSIONS.values():
        raise UnsupportedFileTypeError(f"Invalid content type: {file.content_type}")


@router.post("/", response_model=ReportOut, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    tenant_id: Optional[str] = Query(None, description="Tenant ID (required for system owner)"),
    current_user: User = Depends(get_current_admin_or_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Upload a report file."""
    # Validate file
    validate_file_upload(file)
    
    # Determine tenant ID based on user role
    if current_user.role == UserRole.SYSTEM_OWNER:
        if not tenant_id:
            raise HTTPException(
                status_code=400,
                detail="tenant_id query parameter is required for system owner"
            )
        target_tenant_id = uuid.UUID(tenant_id)
    else:
        # Regular users can only upload to their own tenant
        if tenant_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot specify tenant_id - can only upload to own tenant"
            )
        target_tenant_id = current_user.tenant_id
    
    # Generate unique object key
    file_ext = file.filename.lower().split('.')[-1]
    object_key = f"reports/{target_tenant_id}/{uuid.uuid4()}.{file_ext}"
    
    try:
        # Ensure bucket exists
        if not storage.ensure_bucket():
            raise StorageError("Failed to ensure storage bucket exists")
        
        # Upload file to storage
        if not storage.upload_fileobj(
            file.file,
            object_key,
            ALLOWED_EXTENSIONS[f'.{file_ext}']
        ):
            raise StorageError("Failed to upload file to storage")
        
        # Create report record
        report = Report(
            tenant_id=target_tenant_id,
            uploaded_by=current_user.id,
            filename=file.filename,
            status=ReportStatus.PROCESSING,
            finding_count=0,
            score=None,
            source_object_key=object_key,
            conclusion_object_key=None
        )
        
        session.add(report)
        await session.commit()
        await session.refresh(report)
        
        # Create audit log entry
        audit_log = ReportAuditLog(
            report_id=report.id,
            actor_user_id=current_user.id,
            action=AuditAction.UPLOAD,
            note=f"File uploaded: {file.filename} ({file.size} bytes)"
        )
        
        session.add(audit_log)
        await session.commit()
        
        logger.info(f"Report uploaded successfully: {report.id} by user {current_user.id}")
        
        return report
        
    except Exception as e:
        logger.error(f"Error uploading report: {e}")
        # Try to clean up uploaded file if report creation failed
        try:
            storage.delete_object(object_key)
        except:
            pass  # Ignore cleanup errors
        raise StorageError(f"Failed to process upload: {str(e)}")


@router.get("/", response_model=list[ReportOut])
async def list_reports(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """List reports based on user role."""
    from sqlalchemy import select
    
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner sees all reports
        result = await session.execute(select(Report))
        reports = result.scalars().all()
    else:
        # Regular users see only reports from their tenant
        result = await session.execute(
            select(Report).where(Report.tenant_id == current_user.tenant_id)
        )
        reports = result.scalars().all()
    
    return reports


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific report."""
    from sqlalchemy import select
    
    result = await session.execute(
        select(Report).where(Report.id == uuid.UUID(report_id))
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check access rights
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner can see all reports
        pass
    else:
        # Regular users can only see reports from their tenant
        if report.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return report
