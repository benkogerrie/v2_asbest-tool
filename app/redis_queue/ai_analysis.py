"""
AI Analysis job processing functions for the queue worker - Slice 8 version.
"""
import uuid
import logging
from datetime import datetime, timezone
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
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService
from app.services.analyzer.text_extraction import extract_text_from_pdf
from app.services.pdf_generator import generate_conclusion_pdf

logger = logging.getLogger(__name__)


async def run_ai_analysis(report_id: str, tenant_id: str, pdf_bytes: bytes):
    """
    Run AI analysis on a report using LLM services.
    
    Args:
        report_id: The UUID of the report to analyze
        tenant_id: The tenant ID for prompt overrides
        pdf_bytes: The PDF content as bytes
    """
    logger.info(f"Starting AI analysis for report {report_id}")
    
    try:
        # Create async database session
        db_url = get_db_url()
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            try:
                # Log analysis start
                audit_start = ReportAuditLog(
                    report_id=uuid.UUID(report_id),
                    action=AuditAction.PROCESS_START,
                    note="AI analysis started"
                )
                session.add(audit_start)
                await session.commit()

                # 1) Extract text from PDF
                temp_pdf_path = f"/tmp/ai_analysis_{report_id}.pdf"
                with open(temp_pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                
                try:
                    text = extract_text_from_pdf(Path(temp_pdf_path))
                    logger.info(f"Extracted {len(text)} characters from PDF")
                except Exception as e:
                    logger.error(f"Text extraction failed: {e}")
                    raise

                # 2) Get active prompt with tenant override
                ps = PromptService(session)
                prompt_template = await ps.get_active_prompt("analysis_v1", tenant_id=tenant_id)
                
                # 3) Inject placeholders
                mapping = {
                    "CHECKLIST": """
- Scope van onderzoek
- Risicobeoordeling  
- Handtekening inspecteur
- Wettelijk kader
- Methode van onderzoek
- Locatiegegevens
- Monstergegevens
- Foto's en bewijs
- Aanbevelingen
""",
                    "SEVERITY_WEIGHTS": '{"CRITICAL":30,"HIGH":15,"MEDIUM":7,"LOW":3}',
                    "OUTPUT_SCHEMA": """
{
  "report_summary": "string",
  "score": "number (0-100)",
  "findings": [
    {
      "code": "string",
      "title": "string", 
      "category": "FORMAL|CONTENT|RISK|CONSISTENCY|ADMIN",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "status": "PASS|FAIL|UNKNOWN",
      "page": "number (optional)",
      "evidence_snippet": "string (max 300 chars)",
      "suggested_fix": "string (optional)"
    }
  ]
}
"""
                }
                system_prompt = ps.inject_placeholders(prompt_template, mapping)
                user_prompt = text[:50000]  # Limit to 50k chars for API limits

                # 4) Call LLM
                llm = LLMService()
                ai_output = await llm.call(system_prompt, user_prompt)
                
                logger.info(f"AI analysis completed: score={ai_output.score}, findings={len(ai_output.findings)}")

                # 5) Create Analysis record
                analysis = Analysis(
                    id=uuid.uuid4(),
                    report_id=uuid.UUID(report_id),
                    engine="ai_anthropic",
                    engine_version="claude-3-5-sonnet-20241022",
                    score=ai_output.score,
                    summary=ai_output.report_summary or "AI analyse voltooid",
                    rules_passed=0,  # AI doesn't use rules
                    rules_failed=0,
                    started_at=datetime.now(timezone.utc),
                    finished_at=datetime.now(timezone.utc),
                    duration_ms=0,  # Could be calculated
                    raw_metadata={"ai_analysis": True, "provider": "anthropic"}
                )
                session.add(analysis)
                await session.flush()  # Get the analysis ID

                # 6) Create Finding records
                for finding in ai_output.findings:
                    finding_record = Finding(
                        analysis_id=analysis.id,
                        rule_id=finding.code,
                        section="AI Analysis",  # AI findings don't have sections
                        severity=finding.severity,
                        message=finding.title or finding.code,
                        suggestion=finding.suggested_fix,
                        evidence=finding.evidence_snippet,
                        tags=[]  # AI findings don't have tags
                    )
                    session.add(finding_record)
                
                # Commit all changes
                await session.commit()

                # 7) Update Report
                report = await session.get(Report, uuid.UUID(report_id))
                if report:
                    report.score = ai_output.score
                    report.finding_count = len(ai_output.findings)
                    report.status = ReportStatus.DONE
                    report.updated_at = datetime.now(timezone.utc)
                    await session.commit()

                # 8) Generate conclusion PDF
                try:
                    logger.info(f"Generating conclusion PDF for report {report_id}")
                    
                    # Prepare report metadata
                    report_meta = {
                        "Opdrachtgever": report.uploaded_by_user.name if report.uploaded_by_user else "Onbekend",
                        "Projectnummer": report.filename,  # Use filename as project number for now
                        "Objectlocatie": "Te bepalen",  # Could be extracted from PDF content
                        "Rapportdatum": report.uploaded_at.strftime("%Y-%m-%d"),
                        "Versie": "1.0",
                        "Opsteller": "AI Analyse Systeem"
                    }
                    
                    # Convert AI output to dict for PDF generator
                    ai_analysis_dict = {
                        "report_summary": ai_output.report_summary,
                        "score": ai_output.score,
                        "findings": [
                            {
                                "code": f.code,
                                "title": f.title,
                                "status": f.status,
                                "severity": f.severity,
                                "evidence_snippet": f.evidence_snippet
                            }
                            for f in ai_output.findings
                        ]
                    }
                    
                    # Generate PDF
                    temp_pdf_path = f"/tmp/conclusion_{report_id}.pdf"
                    generate_conclusion_pdf(
                        output_path=temp_pdf_path,
                        report_meta=report_meta,
                        ai_analysis=ai_analysis_dict,
                        bag_data=None,  # Could be added later
                        streetview_path=None  # Could be added later
                    )
                    
                    # Upload PDF to storage
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        conclusion_key = f"tenants/{tenant_id}/reports/{report_id}/conclusion/conclusion.pdf"
                        await storage.upload_file(
                            key=conclusion_key,
                            file_obj=pdf_file,
                            content_type="application/pdf"
                        )
                    
                    # Update report with conclusion key
                    report.conclusion_object_key = conclusion_key
                    await session.commit()
                    
                    # Cleanup temp PDF
                    Path(temp_pdf_path).unlink(missing_ok=True)
                    
                    logger.info(f"Conclusion PDF generated and uploaded for report {report_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate conclusion PDF for report {report_id}: {e}")
                    # Don't fail the entire process if PDF generation fails
                
                await session.commit()

                # Log analysis completion
                audit_done = ReportAuditLog(
                    report_id=uuid.UUID(report_id),
                    action=AuditAction.PROCESS_DONE,
                    note=f"AI analysis completed with score {ai_output.score}"
                )
                session.add(audit_done)
                await session.commit()

                logger.info(f"AI analysis successfully completed for report {report_id}")

            except Exception as e:
                await session.rollback()
                logger.error(f"AI analysis failed for report {report_id}: {e}")
                
                # Log analysis failure
                audit_failed = ReportAuditLog(
                    report_id=uuid.UUID(report_id),
                    action=AuditAction.PROCESS_FAIL,
                    note=f"AI analysis failed: {str(e)}"
                )
                session.add(audit_failed)
                await session.commit()
                
                raise
            finally:
                # Cleanup temp file
                try:
                    Path(temp_pdf_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file: {e}")
                
    except Exception as e:
        logger.error(f"AI analysis pipeline failed for report {report_id}: {e}")
        raise
