"""
Reports API endpoints for file uploads.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.user import User, UserRole
from app.models.report import Report, ReportAuditLog, ReportStatus, AuditAction
from app.models.analysis import Analysis
from app.models.finding import Finding
from app.schemas.report import ReportOut, ReportListResponse, ReportDetail
from app.auth.auth import fastapi_users
from app.auth.dependencies import get_current_admin_or_system_owner
from app.services.storage import storage
from app.exceptions import UnsupportedFileTypeError, FileTooLargeError, StorageError
from app.config import settings
from app.queue.conn import reports_queue, redis_conn
from rq import Retry
from pydantic import BaseModel
from typing import Dict
from sqlalchemy import or_

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
            # Check Redis availability before enqueuing
            redis_conn().ping()
            reports_queue().enqueue(
                "app.queue.jobs.process_report",
                report_id=str(report.id),
                retry=Retry(max=settings.job_max_retries),
                job_timeout=settings.job_timeout_seconds
            )
            logger.info(f"Processing job enqueued for report {report.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue processing job for report {report.id}: {e}")
            # Fail the upload if job enqueue fails - user should know the system is not fully functional
            raise HTTPException(
                status_code=503,
                detail="Queue service unavailable - report uploaded but processing cannot be scheduled"
            )
        
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
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """List reports with filtering, sorting and pagination."""
    
    # STEP 4: Add ReportService back with original logic
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
    current_user: User = Depends(fastapi_users.current_user(active=True)),
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
    current_user: User = Depends(fastapi_users.current_user(active=True)),
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
    current_user: User = Depends(fastapi_users.current_user(active=True)),
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


@router.post("/{report_id}/reprocess")
async def reprocess_report(
    report_id: str,
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """Reprocess a report with new analysis."""
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    # Check if report exists and user has access
    service = ReportService(session)
    report = await service.get_report_for_download(report_id, current_user)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Enqueue reprocessing job
    try:
        # Check Redis availability before enqueuing
        redis_conn().ping()
        job = reports_queue().enqueue(
            "app.queue.jobs.process_report",
            report_id=report_id,
            retry=Retry(max=settings.job_max_retries),
            job_timeout=settings.job_timeout_seconds
        )
        logger.info(f"Reprocessing job enqueued for report {report_id}: {job.id}")
        
        return {
            "job_id": job.id,
            "status": "ENQUEUED",
            "message": "Report reprocessing started"
        }
        
    except Exception as e:
        logger.error(f"Failed to enqueue reprocessing job for report {report_id}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Queue service unavailable - reprocessing cannot be scheduled"
        )


# --- Pydantic response schemas for findings ---
class FindingOut(BaseModel):
    id: str
    code: str
    severity: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    message: str
    page: Optional[int] = None
    evidence: Optional[str] = None

class FindingsAgg(BaseModel):
    total: int
    by_severity: Dict[str, int]

class FindingsResponse(BaseModel):
    report_id: str
    score: Optional[float] = None
    findings: List[FindingOut]
    agg: FindingsAgg

@router.get("/{report_id}/findings", response_model=FindingsResponse)
async def get_report_findings(
    report_id: str,
    severity: Optional[List[str]] = Query(default=None, description="Filter by severity (repeatable)"),
    q: Optional[str] = Query(default=None, description="Search in message/evidence"),
    page: Optional[int] = Query(default=None, ge=0),
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db),
):
    """Get findings for a report with filtering."""
    # 1) Tenant-scoped report
    try:
        rid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Report not found")

    res_report = await session.execute(
        select(Report).where(
            Report.id == rid,
            Report.tenant_id == current_user.tenant_id,
            Report.deleted_at.is_(None)
        )
    )
    report = res_report.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 2) Laatste analysis
    res_analysis = await session.execute(
        select(Analysis).where(Analysis.report_id == rid).order_by(Analysis.finished_at.desc())
    )
    analysis = res_analysis.scalar_one_or_none()
    if not analysis:
        return FindingsResponse(
            report_id=report_id,
            score=float(report.score) if report.score is not None else None,
            findings=[],
            agg=FindingsAgg(total=0, by_severity={"LOW":0,"MEDIUM":0,"HIGH":0,"CRITICAL":0})
        )

    # 3) Findings query (filters)
    qry = select(Finding).where(Finding.analysis_id == analysis.id)
    if severity:
        qry = qry.where(Finding.severity.in_(severity))
    if page is not None:
        # Note: We don't have page field yet, so this filter is ignored
        pass
    if q:
        like = f"%{q}%"
        qry = qry.where(or_(Finding.message.ilike(like), Finding.evidence.ilike(like)))

    res_findings = await session.execute(qry.order_by(Finding.id.asc()))
    findings_rows = res_findings.scalars().all()

    # 4) Map → schema
    findings_out = [
        FindingOut(
            id=str(f.id),
            code=f.rule_id,            # bij jullie: rule_id representeert de code
            severity=f.severity,
            message=f.message,
            page=None,  # We don't have page field yet
            evidence=(str(f.evidence) if f.evidence else None),
        )
        for f in findings_rows
    ]

    # 5) Aggregatie
    agg = {"LOW":0,"MEDIUM":0,"HIGH":0,"CRITICAL":0}
    for f in findings_rows:
        if f.severity in agg:
            agg[f.severity] += 1

    return FindingsResponse(
        report_id=report_id,
        score=float(report.score) if report.score is not None else None,
        findings=findings_out,
        agg=FindingsAgg(total=len(findings_rows), by_severity=agg),
    )


@router.get("/{report_id}/download")
async def get_download_url(
    report_id: str,
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """
    Generate a presigned URL for downloading a report.
    
    This endpoint generates a temporary, secure download URL that expires after
    the configured TTL period. The URL provides direct access to the report
    file in storage without requiring authentication.
    """
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    # Get report with tenant scoping
    service = ReportService(session)
    report = await service.get_report_for_download(report_id, current_user)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Check if report is ready for download
    if report.status != ReportStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Report is not ready for download. Current status: {report.status}"
        )
    
    # Check if report is soft deleted
    if report.deleted_at:
        raise HTTPException(
            status_code=404,
            detail="Report has been deleted"
        )
    
    # Use storage_key if available, otherwise fall back to conclusion_object_key
    storage_key = report.storage_key or report.conclusion_object_key
    if not storage_key:
        raise HTTPException(
            status_code=404,
            detail="Report file not found in storage"
        )
    
    try:
        # Generate presigned URL
        download_url = storage.presigned_get_url(
            object_key=storage_key,
            expires=settings.download_ttl
        )
        
        if not download_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate download URL"
            )
        
        # Create audit log for download
        audit_log = ReportAuditLog(
            report_id=report.id,
            actor_user_id=current_user.id,
            action=AuditAction.REPORT_DOWNLOAD,
            note=f"Download URL generated (TTL: {settings.download_ttl}s)"
        )
        session.add(audit_log)
        await session.commit()
        
        logger.info(f"Download URL generated for report {report_id} by user {current_user.id}")
        
        return {
            "url": download_url,
            "expires_in": settings.download_ttl,
            "filename": report.filename,
            "file_size": report.file_size,
            "checksum": report.checksum
        }
        
    except Exception as e:
        logger.error(f"Error generating download URL for report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate download URL"
        )


@router.get("/stream")
async def stream_reports(
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """
    Server-Sent Events endpoint for real-time report updates.
    
    This endpoint provides a stream of report status updates for the current user's tenant.
    The client can listen to this stream to receive real-time notifications when reports
    change status (PROCESSING -> DONE/FAILED).
    """
    from app.services.reports import ReportService
    import asyncio
    import json
    
    async def event_generator():
        """Generate SSE events for report updates."""
        service = ReportService(session)
        
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established'})}\n\n"
        
        # Get initial reports state
        reports = await service.get_reports_for_user(current_user)
        initial_data = {
            'type': 'initial_state',
            'reports': [
                {
                    'id': str(report.id),
                    'status': report.status,
                    'score': report.score,
                    'finding_count': report.finding_count,
                    'updated_at': report.uploaded_at.isoformat() if report.uploaded_at else None
                }
                for report in reports
            ]
        }
        yield f"data: {json.dumps(initial_data)}\n\n"
        
        # Poll for updates every 2 seconds
        last_check = datetime.utcnow()
        
        while True:
            try:
                # Check for new or updated reports
                current_reports = await service.get_reports_for_user(current_user)
                
                # Find reports that have been updated since last check
                for report in current_reports:
                    if report.uploaded_at and report.uploaded_at > last_check:
                        update_data = {
                            'type': 'report_update',
                            'report': {
                                'id': str(report.id),
                                'status': report.status,
                                'score': report.score,
                                'finding_count': report.finding_count,
                                'updated_at': report.uploaded_at.isoformat(),
                                'filename': report.filename
                            }
                        }
                        yield f"data: {json.dumps(update_data)}\n\n"
                
                # Send heartbeat every 30 seconds
                if (datetime.utcnow() - last_check).seconds >= 30:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                    last_check = datetime.utcnow()
                
                # Wait 2 seconds before next check
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                # Client disconnected
                logger.info(f"SSE connection closed for user {current_user.id}")
                break
            except Exception as e:
                logger.error(f"Error in SSE stream for user {current_user.id}: {e}")
                error_data = {
                    'type': 'error',
                    'message': 'An error occurred while streaming updates'
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(5)  # Wait before retrying
    
    return Response(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.delete("/{report_id}")
async def soft_delete_report(
    report_id: str,
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """
    Soft delete a report.
    
    This marks the report as deleted (sets deleted_at timestamp) but keeps
    the record in the database. The report will be hidden from normal queries
    and eventually purged by a background job.
    """
    from app.services.reports import ReportService
    
    # Validate report_id format
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid report_id format"
        )
    
    # Get report with tenant scoping
    service = ReportService(session)
    report = await service.get_report_for_download(report_id, current_user)
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Check if already deleted
    if report.deleted_at:
        raise HTTPException(
            status_code=400,
            detail="Report is already deleted"
        )
    
    try:
        # Soft delete the report
        report.deleted_at = datetime.utcnow()
        session.add(report)
        
        # Create audit log
        audit_log = ReportAuditLog(
            report_id=report.id,
            actor_user_id=current_user.id,
            action=AuditAction.SOFT_DELETE,
            note=f"Report soft deleted by {current_user.email}"
        )
        session.add(audit_log)
        await session.commit()
        
        logger.info(f"Report {report_id} soft deleted by user {current_user.id}")
        
        return {
            "message": "Report deleted successfully",
            "deleted_at": report.deleted_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error soft deleting report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete report"
        )


@router.post("/{report_id}/reanalyze")
async def reanalyze_report(
    report_id: str,
    current_user: User = Depends(get_current_admin_or_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Reanalyze a report with the current active AI prompt."""
    try:
        # Get the report
        result = await session.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        if report.deleted_at:
            raise HTTPException(
                status_code=400,
                detail="Cannot reanalyze deleted report"
            )
        
        # Reset report status and clear old analysis
        report.status = ReportStatus.PROCESSING
        report.score = None
        report.finding_count = None
        report.analysis_object_key = None
        report.conclusion_object_key = None
        
        # Delete old analysis and findings
        from sqlalchemy import delete
        await session.execute(
            delete(Analysis).where(Analysis.report_id == report_id)
        )
        await session.execute(
            delete(Finding).where(Finding.report_id == report_id)
        )
        
        # Create audit log
        audit_log = ReportAuditLog(
            report_id=report.id,
            actor_user_id=current_user.id,
            action=AuditAction.REANALYZE,
            note=f"Report reanalysis triggered by {current_user.email}"
        )
        session.add(audit_log)
        
        await session.commit()
        
        # Enqueue AI analysis job
        job = reports_queue.enqueue(
            'app.queue.jobs.process_report_ai',
            report_id,
            retry=Retry(max=3, interval=60)
        )
        
        logger.info(f"Report {report_id} reanalysis queued with job {job.id}")
        
        return {
            "success": True,
            "message": "Report reanalysis started",
            "job_id": job.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reanalyzing report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to start reanalysis"
        )
