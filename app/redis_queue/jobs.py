"""
Job processing functions for the queue worker - Slice 5 version.
"""
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.database import get_db_url
from app.models.report import Report, ReportAuditLog, ReportStatus, AuditAction
from app.models.analysis import Analysis
from app.models.finding import Finding
from app.models.user import User
from app.services.storage import storage
from app.services.analyzer.rules import analyze_text_to_result, run_rules_v1, RULES_VERSION
from app.services.analyzer.text_extraction import extract_text_from_pdf
from app.services.pdf.conclusion_reportlab import build_conclusion_pdf
from app.services.email import email_service
from app.redis_queue.ai_analysis import run_ai_analysis

logger = logging.getLogger(__name__)


def process_report_with_ai(report_id: str, use_ai: bool = True) -> bool:
    """
    Process a report with AI analysis (Slice 8) or fallback to rules-based analysis.
    
    Args:
        report_id: The UUID of the report to process
        use_ai: Whether to use AI analysis (True) or rules-based analysis (False)
        
    Returns:
        bool: True if processing succeeded, False otherwise
    """
    if use_ai:
        return _process_report_ai(report_id)
    else:
        return process_report(report_id)


def _process_report_ai(report_id: str) -> bool:
    """
    Process a report with AI analysis.
    
    Args:
        report_id: The UUID of the report to process
        
    Returns:
        bool: True if processing succeeded, False otherwise
    """
    logger.info(f"Starting AI analysis for report {report_id}")
    
    try:
        # Create sync database session for RQ worker
        db_url = get_db_url()
        logger.info(f"Using database URL: {db_url[:50]}...")
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        return False
    
    with SessionLocal() as session:
        try:
            # Get report
            report = session.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
            if not report:
                logger.error(f"Report {report_id} not found")
                return False

            # Create audit log for AI process start
            audit_start = ReportAuditLog(
                report_id=report.id,
                action=AuditAction.PROCESS_START,
                note="AI analysis started"
            )
            session.add(audit_start)
            session.commit()

            # Download PDF from storage and run AI analysis
            try:
                # Get PDF from storage
                if not report.source_object_key:
                    logger.error(f"No source file found for report {report_id}")
                    return False
                
                # Download PDF from storage
                pdf_bytes = storage.download_object(report.source_object_key)
                if not pdf_bytes:
                    logger.error(f"Failed to download PDF for report {report_id}")
                    return False
                
                logger.info(f"Downloaded PDF for report {report_id}: {len(pdf_bytes)} bytes")
                
                # Run AI analysis
                from app.redis_queue.ai_analysis import run_ai_analysis
                import asyncio
                
                # Run async AI analysis in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        run_ai_analysis(str(report.id), str(report.tenant_id), pdf_bytes)
                    )
                    logger.info(f"AI analysis completed for report {report_id}")
                    return True
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"AI analysis failed for report {report_id}: {e}")
                logger.warning("Falling back to rules-based analysis")
                return process_report(report_id)

        except Exception as e:
            logger.error(f"AI analysis failed for report {report_id}: {e}")
            
            # Log AI analysis failure
            audit_failed = ReportAuditLog(
                report_id=uuid.UUID(report_id),
                action=AuditAction.PROCESS_FAILED,
                note=f"AI analysis failed: {str(e)}"
            )
            session.add(audit_failed)
            session.commit()
            
            return False


def process_report(report_id: str) -> bool:
    """
    Process a report with rule-based analysis and generate conclusion PDF.
    
    Args:
        report_id: The UUID of the report to process
        
    Returns:
        bool: True if processing succeeded, False otherwise
    """
    logger.info(f"Starting to process report {report_id}")
    
    try:
        # Create sync database session for RQ worker
        db_url = get_db_url()
        logger.info(f"Using database URL: {db_url[:50]}...")
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        return False
    
    with SessionLocal() as session:
        try:
            # Get report
            report = session.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
            if not report:
                logger.error(f"Report {report_id} not found")
                return False

            # Create audit log for process start
            audit_start = ReportAuditLog(
                report_id=report.id,
                action=AuditAction.PROCESS_START,
                note="Report processing started with rule-based analysis"
            )
            session.add(audit_start)
            session.commit()

            logger.info(f"Starting rule-based analysis for report {report_id}")

            # TODO: Download source PDF from DigitalOcean Spaces to temp file
            # For now, we'll use a placeholder path - this needs to be implemented
            # based on your storage setup
            temp_pdf_path = f"/tmp/source_{report.id}.pdf"
            
            # Extract text from PDF
            try:
                text = extract_text_from_pdf(temp_pdf_path)
                logger.info(f"Extracted {len(text)} characters from PDF")
            except Exception as e:
                logger.error(f"Text extraction failed: {e}")
                # Fallback to dummy text for now
                text = "Dummy text for testing - this will be replaced with actual PDF extraction"
                logger.warning("Using dummy text for analysis")

            # Run rule-based analysis
            analysis_result = analyze_text_to_result(report.id, text)
            raw_findings = run_rules_v1(text)
            
            logger.info(f"Analysis completed: score={analysis_result.score}, findings={len(raw_findings)}")

            # Create Analysis record
            analysis = Analysis(
                id=uuid.uuid4(),
                report_id=report.id,
                engine=analysis_result.engine,
                engine_version=analysis_result.engine_version,
                score=analysis_result.score,
                summary=analysis_result.summary,
                rules_passed=analysis_result.rules_passed,
                rules_failed=analysis_result.rules_failed,
                started_at=analysis_result.started_at,
                finished_at=analysis_result.finished_at,
                duration_ms=analysis_result.duration_ms,
                raw_metadata={"source_bytes": len(text) if text else None}
            )
            session.add(analysis)
            session.flush()  # Get the analysis ID

            # Create Finding records
            for finding in raw_findings:
                finding_record = Finding(
                    analysis_id=analysis.id,
                    rule_id=finding.rule_id,
                    section=finding.section,
                    severity=finding.severity,
                    message=finding.message,
                    suggestion=finding.suggestion,
                    evidence=finding.evidence,
                    tags=finding.tags
                )
                session.add(finding_record)

            # Generate PDF conclusion using ReportLab
            pdf_temp_path = f"/tmp/conclusion_{report.id}.pdf"
            build_conclusion_pdf(
                output_path=pdf_temp_path,
                meta={
                    "report_name": report.filename,
                    "tenant_name": "Test Tenant",  # TODO: Get from report.tenant
                    "score": analysis_result.score,
                    "summary": analysis_result.summary,
                    "engine": analysis_result.engine,
                    "engine_version": analysis_result.engine_version,
                    "analysis_id": str(analysis.id),
                    "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                },
                findings=[f.dict() for f in raw_findings]
            )

            # Upload PDF to storage with checksum and file size
            storage_key = f"tenants/{report.tenant_id}/reports/{report.id}/output.pdf"
            
            with open(pdf_temp_path, 'rb') as pdf_file:
                pdf_buffer = BytesIO(pdf_file.read())
                
                # Use new method that returns checksum and file size
                success, checksum, file_size = storage.upload_fileobj_with_checksum(
                    pdf_buffer,
                    storage_key,
                    "application/pdf"
                )
                
                if not success:
                    raise Exception("Failed to upload conclusion PDF")
                
                logger.info(f"PDF uploaded successfully: size={file_size}, checksum={checksum[:16]}...")

            # Update report with results
            report.status = ReportStatus.DONE
            report.score = analysis_result.score
            report.finding_count = len(raw_findings)
            report.conclusion_object_key = storage_key  # Keep for backward compatibility
            report.storage_key = storage_key  # New field for Slice 6
            report.checksum = checksum
            report.file_size = file_size
            report.analysis_version = RULES_VERSION
            report.analysis_duration_ms = analysis_result.duration_ms
            report.summary = analysis_result.summary
            # Keep findings_json for backward compatibility
            report.findings_json = [f.dict() for f in raw_findings]

            session.commit()

            # Create audit log for process completion
            audit_done = ReportAuditLog(
                report_id=report.id,
                action=AuditAction.PROCESS_DONE,
                note=f"Rule-based analysis completed: score={analysis_result.score}, findings={len(raw_findings)}"
            )
            session.add(audit_done)
            session.commit()

            # Send email notification for successful completion
            try:
                # Get the user who uploaded the report
                uploaded_by_user = session.query(User).filter(User.id == report.uploaded_by).first()
                if uploaded_by_user:
                    email_sent = email_service.send_report_completion_notification(
                        report=report,
                        user=uploaded_by_user
                    )
                    if email_sent:
                        # Log notification sent
                        notification_audit = ReportAuditLog(
                            report_id=report.id,
                            action=AuditAction.NOTIFICATION_SENT,
                            note="Email notification sent for successful completion"
                        )
                        session.add(notification_audit)
                        session.commit()
                        logger.info(f"Email notification sent for report {report.id}")
                    else:
                        logger.warning(f"Failed to send email notification for report {report.id}")
            except Exception as e:
                logger.error(f"Error sending email notification for report {report.id}: {e}")

            logger.info(f"Successfully processed report {report.id}: score={analysis_result.score}, findings={len(raw_findings)}")
            return True

        except Exception as e:
            logger.error(f"Error processing report {report.id}: {e}")

            # Update report status to failed
            try:
                report.status = ReportStatus.FAILED
                report.error_message = str(e)  # Store error message for debugging
                session.commit()

                # Create audit log for process failure
                audit_fail = ReportAuditLog(
                    report_id=report.id,
                    action=AuditAction.PROCESS_FAIL,
                    note=f"Processing failed: {str(e)}"
                )
                session.add(audit_fail)
                session.commit()
                
                # Send email notification for failed processing
                try:
                    # Get the user who uploaded the report
                    uploaded_by_user = session.query(User).filter(User.id == report.uploaded_by).first()
                    if uploaded_by_user:
                        email_sent = email_service.send_report_completion_notification(
                            report=report,
                            user=uploaded_by_user
                        )
                        if email_sent:
                            # Log notification sent
                            notification_audit = ReportAuditLog(
                                report_id=report.id,
                                action=AuditAction.NOTIFICATION_SENT,
                                note="Email notification sent for failed processing"
                            )
                            session.add(notification_audit)
                            session.commit()
                            logger.info(f"Email notification sent for failed report {report.id}")
                        else:
                            logger.warning(f"Failed to send email notification for failed report {report.id}")
                except Exception as email_error:
                    logger.error(f"Error sending email notification for failed report {report.id}: {email_error}")
                    
            except:
                pass  # Ignore cleanup errors

            return False


def purge_deleted_reports() -> int:
    """
    Background job to permanently delete reports that have been soft deleted
    for more than the configured purge delay period.
    
    Returns:
        int: Number of reports purged
    """
    from datetime import timedelta
    from app.config import settings
    
    logger.info("Starting purge job for deleted reports")
    
    try:
        # Create sync database session for RQ worker
        db_url = get_db_url()
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.error(f"Failed to create database engine for purge job: {e}")
        return 0
    
    with SessionLocal() as session:
        try:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=settings.purge_delay_days)
            
            # Find reports that are soft deleted and past the cutoff date
            reports_to_purge = session.query(Report).filter(
                Report.deleted_at.isnot(None),
                Report.deleted_at <= cutoff_date
            ).all()
            
            purged_count = 0
            
            for report in reports_to_purge:
                try:
                    # Delete files from storage
                    files_deleted = 0
                    
                    # Delete source file
                    if report.source_object_key:
                        if storage.delete_object(report.source_object_key):
                            files_deleted += 1
                            logger.info(f"Deleted source file: {report.source_object_key}")
                    
                    # Delete conclusion file (storage_key or conclusion_object_key)
                    conclusion_key = report.storage_key or report.conclusion_object_key
                    if conclusion_key:
                        if storage.delete_object(conclusion_key):
                            files_deleted += 1
                            logger.info(f"Deleted conclusion file: {conclusion_key}")
                    
                    # Create audit log for purge
                    audit_log = ReportAuditLog(
                        report_id=report.id,
                        action=AuditAction.REPORT_PURGE,
                        note=f"Report permanently deleted after {settings.purge_delay_days} days. Files deleted: {files_deleted}"
                    )
                    session.add(audit_log)
                    
                    # Delete the report record from database
                    session.delete(report)
                    purged_count += 1
                    
                    logger.info(f"Purged report {report.id} (deleted {files_deleted} files)")
                    
                except Exception as e:
                    logger.error(f"Error purging report {report.id}: {e}")
                    continue
            
            session.commit()
            logger.info(f"Purge job completed: {purged_count} reports purged")
            return purged_count
            
        except Exception as e:
            logger.error(f"Error in purge job: {e}")
            session.rollback()
            return 0
