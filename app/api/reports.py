"""
Reports API endpoints for file uploads.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.user import User, UserRole
from app.models.report import Report, ReportAuditLog, ReportStatus, AuditAction
from app.schemas.report import ReportOut, ReportListResponse, ReportDetail
from app.auth.dependencies import get_current_active_user, get_current_admin_or_system_owner
from app.services.storage import storage
from app.exceptions import UnsupportedFileTypeError, FileTooLargeError, StorageError
from app.config import settings
from app.queue.conn import reports_queue

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
    
    # Check file size - handle both known size and streaming validation
    if file.size is not None:
        if file.size > MAX_FILE_SIZE:
            raise FileTooLargeError(f"File too large. Max size: {settings.max_upload_mb}MB")
    else:
        # For streaming uploads, we'll validate during upload
        logger.warning(f"File size unknown for {file.filename}, will validate during upload")


def validate_file_size_during_upload(file_stream, max_size: int) -> None:
    """Validate file size during streaming upload."""
    chunk_size = 8192  # 8KB chunks
    total_size = 0
    
    # Read file in chunks and check size
    while True:
        chunk = file_stream.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            raise FileTooLargeError(f"File too large. Max size: {settings.max_upload_mb}MB")
    
    # Reset file pointer for actual upload
    file_stream.seek(0)


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
    
    try:
        # Ensure bucket exists
        if not storage.ensure_bucket():
            raise StorageError("Failed to ensure storage bucket exists")
        
        # Create report record first to get the ID
        report = Report(
            tenant_id=target_tenant_id,
            uploaded_by=current_user.id,
            filename=file.filename,
            status=ReportStatus.PROCESSING,
            finding_count=0,
            score=None,
            source_object_key="",  # Will be updated after upload
            conclusion_object_key=None
        )
        
        session.add(report)
        await session.flush()  # Get the ID without committing
        
        # Generate object key using the actual report ID
        object_key = f"tenants/{target_tenant_id}/reports/{report.id}/source/{file.filename}"
        
        # Update the report with the correct object key
        report.source_object_key = object_key
        
        # Upload file to storage with size validation
        file_ext = file.filename.lower().split('.')[-1]
        
        # If file size is unknown, validate during upload
        if file.size is None:
            validate_file_size_during_upload(file.file, MAX_FILE_SIZE)
        
        if not storage.upload_fileobj(
            file.file,
            object_key,
            ALLOWED_EXTENSIONS[f'.{file_ext}']
        ):
            raise StorageError("Failed to upload file to storage")
        
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
        
        # Enqueue processing job
        try:
            reports_queue().enqueue(
                "app.queue.jobs.process_report",
                report_id=str(report.id),
                retry=settings.job_max_retries
            )
            logger.info(f"Processing job enqueued for report {report.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue processing job for report {report.id}: {e}")
            # Don't fail the upload if job enqueue fails
        
        logger.info(f"Report uploaded successfully: {report.id} by user {current_user.id}")
        
        return ReportOut.from_orm(report)
        
    except Exception as e:
        logger.error(f"Error uploading report: {e}")
        # Try to clean up uploaded file if report creation failed
        try:
            if 'object_key' in locals():
                storage.delete_object(object_key)
        except:
            pass  # Ignore cleanup errors
        raise StorageError(f"Failed to process upload: {str(e)}")


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID (SYSTEM_OWNER only)"),
    q: Optional[str] = Query(None, description="Search in filename"),
    sort: str = Query("uploaded_at_desc", description="Sort order"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """List reports with filtering, sorting and pagination."""
    from app.services.reports import ReportService
    
    # Validate sort parameter
    valid_sorts = ["uploaded_at_desc", "uploaded_at_asc", "filename_asc", "filename_desc"]
    if sort not in valid_sorts:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid sort parameter. Valid options: {', '.join(valid_sorts)}"
        )
    
    # Validate tenant_id parameter (only allowed for SYSTEM_OWNER)
    if tenant_id and current_user.role != UserRole.SYSTEM_OWNER:
        raise HTTPException(
            status_code=403,
            detail="tenant_id filter is only allowed for SYSTEM_OWNER"
        )
    
    # Validate tenant_id format if provided
    if tenant_id:
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid tenant_id format"
            )
    
    service = ReportService(session)
    try:
        reports, total = await service.get_reports_with_filters(
            current_user=current_user,
            page=page,
            page_size=page_size,
            status=status,
            tenant_id=tenant_id,
            q=q,
            sort=sort
        )
    except ValueError as e:
        if "Tenant not found" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
    
    return ReportListResponse(
        items=reports,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report_detail(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Get detailed report information."""
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    service = ReportService(session)
    report_detail = await service.get_report_detail(report_id, current_user)
    
    if not report_detail:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    return report_detail


@router.get("/{report_id}/source")
async def download_source(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Download the original source file."""
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    service = ReportService(session)
    report = await service.get_report_for_download(report_id, current_user)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Get file from storage
    try:
        file_stream = storage.download_fileobj(report.source_object_key)
        if not file_stream:
            raise HTTPException(
                status_code=404,
                detail="Source file not found in storage"
            )
        
        # Determine content type based on file extension
        file_ext = report.filename.lower().split('.')[-1] if '.' in report.filename else ''
        content_type = ALLOWED_EXTENSIONS.get(f'.{file_ext}', 'application/octet-stream')
        
        return StreamingResponse(
            file_stream,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={report.filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading source file for report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download source file"
        )


@router.get("/{report_id}/conclusion")
async def download_conclusion(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """Download the conclusion PDF file."""
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    service = ReportService(session)
    report = await service.get_report_for_download(report_id, current_user)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Check if conclusion exists
    if not report.conclusion_object_key:
        raise HTTPException(
            status_code=404,
            detail="Conclusion not yet available"
        )
    
    # Get file from storage
    try:
        file_stream = storage.download_fileobj(report.conclusion_object_key)
        if not file_stream:
            raise HTTPException(
                status_code=404,
                detail="Conclusion file not found in storage"
            )
        
        return StreamingResponse(
            file_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=conclusie_{report.filename}.pdf"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading conclusion file for report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download conclusion file"
        )
