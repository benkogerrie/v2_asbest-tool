"""
Job processing functions for the queue worker.
"""
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.database import get_db_url
from app.models.report import Report, ReportAuditLog, ReportStatus, AuditAction
from app.services.storage import storage
from app.queue.pdf_generator import generate_conclusion_pdf

logger = logging.getLogger(__name__)


def process_report(report_id: str) -> bool:
    """
    Process a report with dummy AI analysis and generate conclusion PDF.
    
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
                note="Report processing started"
            )
            session.add(audit_start)
            session.commit()
            
            logger.info(f"Starting processing for report {report_id}")
            
            # Generate dummy AI analysis
            summary = "Rapport is grotendeels compleet; aanvulling nodig voor maatregel 2A (dummy)."
            findings = [
                {
                    "code": "R001",
                    "severity": "MAJOR",
                    "title": "Projectadres onvolledig",
                    "detail_text": "Postcode ontbreekt (dummy)"
                },
                {
                    "code": "R012", 
                    "severity": "CRITICAL",
                    "title": "Maatregelen onduidelijk",
                    "detail_text": "2A niet uitgewerkt (dummy)"
                }
            ]
            score = 89
            finding_count = len(findings)
            
            # Generate PDF conclusion
            pdf_content = generate_conclusion_pdf(
                report.filename,
                summary,
                findings,
                report.id,
                datetime.utcnow()
            )
            
            # Upload PDF to storage
            conclusion_key = f"tenants/{report.tenant_id}/reports/{report.id}/conclusion/conclusie.pdf"
            pdf_buffer = BytesIO(pdf_content)
            
            if not storage.upload_fileobj(
                pdf_buffer,
                conclusion_key,
                "application/pdf"
            ):
                raise Exception("Failed to upload conclusion PDF")
            
            # Update report with results
            report.status = ReportStatus.DONE
            report.score = score
            report.finding_count = finding_count
            report.conclusion_object_key = conclusion_key
            # Store findings as JSON in a new column (we'll add this via migration)
            report.findings_json = findings
            report.summary = summary
            
            session.commit()
            
            # Create audit log for process completion
            audit_done = ReportAuditLog(
                report_id=report.id,
                action=AuditAction.PROCESS_DONE,
                note=f"Processing completed: score={score}, findings={finding_count}"
            )
            session.add(audit_done)
            session.commit()
            
            logger.info(f"Successfully processed report {report_id}: score={score}, findings={finding_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing report {report_id}: {e}")
            
            # Update report status to failed
            try:
                report.status = ReportStatus.FAILED
                session.commit()
                
                # Create audit log for process failure
                audit_fail = ReportAuditLog(
                    report_id=report.id,
                    action=AuditAction.PROCESS_FAIL,
                    note=f"Processing failed: {str(e)}"
                )
                session.add(audit_fail)
                session.commit()
            except:
                pass  # Ignore cleanup errors
                
            return False
