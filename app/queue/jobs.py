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
from app.services.storage import storage
from app.services.analyzer.rules import analyze_text_to_result, run_rules_v1, RULES_VERSION
from app.services.analyzer.text_extraction import extract_text_from_pdf
from app.services.pdf.conclusion_reportlab import build_conclusion_pdf

logger = logging.getLogger(__name__)


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

            # Upload PDF to storage
            conclusion_key = f"tenants/{report.tenant_id}/reports/{report.id}/conclusion/conclusie.pdf"
            
            # TODO: Upload PDF to DigitalOcean Spaces
            # For now, we'll use the existing storage service
            with open(pdf_temp_path, 'rb') as pdf_file:
                pdf_buffer = BytesIO(pdf_file.read())
                
                if not storage.upload_fileobj(
                    pdf_buffer,
                    conclusion_key,
                    "application/pdf"
                ):
                    raise Exception("Failed to upload conclusion PDF")

            # Update report with results
            report.status = ReportStatus.DONE
            report.score = analysis_result.score
            report.finding_count = len(raw_findings)
            report.conclusion_object_key = conclusion_key
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

            logger.info(f"Successfully processed report {report.id}: score={analysis_result.score}, findings={len(raw_findings)}")
            return True

        except Exception as e:
            logger.error(f"Error processing report {report.id}: {e}")

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
