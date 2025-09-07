"""
Test soft delete en purge functionaliteit voor Slice 6.
"""
import pytest
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from app.models.report import ReportStatus, AuditAction


class TestSoftDeleteAndPurge:
    """Test soft delete en purge functionaliteit."""
    
    @pytest.mark.asyncio
    async def test_soft_delete_blocks_download_and_list(self, client, make_report, mock_storage, test_session):
        """Test dat soft delete download en list blokkeert."""
        
        # Create report with storage
        report = await make_report(
            id="soft-del-1",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/soft-del-1/output.pdf",
            filename="soft_delete_test.pdf"
        )
        
        # Mock storage
        mock_storage.objects["tenants/test/reports/soft-del-1/output.pdf"] = b"fake pdf content"
        
        # Verify report is downloadable before soft delete
        response = client.get(f"/reports/{report.id}/download")
        assert response.status_code == HTTPStatus.OK
        
        # Verify report is in list before soft delete
        list_response = client.get("/reports/")
        assert list_response.status_code == HTTPStatus.OK
        reports = list_response.json()
        report_ids = [r["id"] for r in reports]
        assert str(report.id) in report_ids
        
        # Soft delete the report
        delete_response = client.delete(f"/reports/{report.id}")
        assert delete_response.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)
        
        # Verify report is not downloadable after soft delete
        response = client.get(f"/reports/{report.id}/download")
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "deleted" in response.json()["detail"]
        
        # Verify report is not in list after soft delete
        list_response = client.get("/reports/")
        assert list_response.status_code == HTTPStatus.OK
        reports = list_response.json()
        report_ids = [r["id"] for r in reports]
        assert str(report.id) not in report_ids
        
        # Verify deleted_at is set in database
        from app.models.report import Report
        from sqlalchemy import select
        
        db_report = await test_session.execute(
            select(Report).where(Report.id == report.id)
        )
        db_report = db_report.scalar_one()
        assert db_report.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_audit_logging(self, client, make_report, test_session):
        """Test dat soft delete acties gelogd worden in audit trail."""
        
        from app.models.report import ReportAuditLog
        from sqlalchemy import select, func
        
        report = await make_report(
            id="audit-del-1",
            status=ReportStatus.DONE,
            filename="audit_delete_test.pdf"
        )
        
        # Count audit logs before
        before_count = await test_session.execute(
            select(func.count(ReportAuditLog.id))
        )
        before_count = before_count.scalar()
        
        # Soft delete the report
        response = client.delete(f"/reports/{report.id}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)
        
        # Count audit logs after
        after_count = await test_session.execute(
            select(func.count(ReportAuditLog.id))
        )
        after_count = after_count.scalar()
        
        # Should have one more audit log
        assert after_count == before_count + 1
        
        # Check audit log content
        audit_log = await test_session.execute(
            select(ReportAuditLog)
            .where(ReportAuditLog.report_id == report.id)
            .where(ReportAuditLog.action == AuditAction.REPORT_DELETE)
            .order_by(ReportAuditLog.created_at.desc())
        )
        audit_log = audit_log.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.action == AuditAction.REPORT_DELETE

    @pytest.mark.asyncio
    async def test_purge_job_removes_old_deleted_reports(self, make_report, mock_storage, test_session):
        """Test dat purge job oude deleted reports verwijdert."""
        
        from app.queue.jobs import purge_deleted_reports
        
        # Create report deleted 8 days ago (beyond grace period)
        old_deleted_report = await make_report(
            id="purge-old-1",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/purge-old-1/output.pdf",
            deleted_at=datetime.now(timezone.utc) - timedelta(days=8),
            filename="old_deleted_report.pdf"
        )
        
        # Create report deleted 3 days ago (within grace period)
        recent_deleted_report = await make_report(
            id="purge-recent-1",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/purge-recent-1/output.pdf",
            deleted_at=datetime.now(timezone.utc) - timedelta(days=3),
            filename="recent_deleted_report.pdf"
        )
        
        # Mock storage objects
        mock_storage.objects["tenants/test/reports/purge-old-1/output.pdf"] = b"old pdf content"
        mock_storage.objects["tenants/test/reports/purge-recent-1/output.pdf"] = b"recent pdf content"
        
        # Run purge job with 7 days grace period
        await purge_deleted_reports()
        
        # Verify old report is removed from storage
        assert "tenants/test/reports/purge-old-1/output.pdf" not in mock_storage.objects
        
        # Verify recent report is still in storage
        assert "tenants/test/reports/purge-recent-1/output.pdf" in mock_storage.objects
        
        # Verify old report is removed from database
        from app.models.report import Report
        from sqlalchemy import select
        
        old_report = await test_session.execute(
            select(Report).where(Report.id == old_deleted_report.id)
        )
        assert old_report.scalar_one_or_none() is None
        
        # Verify recent report is still in database
        recent_report = await test_session.execute(
            select(Report).where(Report.id == recent_deleted_report.id)
        )
        assert recent_report.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_purge_job_audit_logging(self, make_report, mock_storage, test_session):
        """Test dat purge job audit logs schrijft."""
        
        from app.queue.jobs import purge_deleted_reports
        from app.models.report import ReportAuditLog
        from sqlalchemy import select, func
        
        # Create report deleted 8 days ago
        old_report = await make_report(
            id="purge-audit-1",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/purge-audit-1/output.pdf",
            deleted_at=datetime.now(timezone.utc) - timedelta(days=8),
            filename="purge_audit_test.pdf"
        )
        
        mock_storage.objects["tenants/test/reports/purge-audit-1/output.pdf"] = b"pdf content"
        
        # Count audit logs before
        before_count = await test_session.execute(
            select(func.count(ReportAuditLog.id))
        )
        before_count = before_count.scalar()
        
        # Run purge job
        await purge_deleted_reports()
        
        # Count audit logs after
        after_count = await test_session.execute(
            select(func.count(ReportAuditLog.id))
        )
        after_count = after_count.scalar()
        
        # Should have one more audit log for purge action
        assert after_count == before_count + 1
        
        # Check audit log content
        audit_log = await test_session.execute(
            select(ReportAuditLog)
            .where(ReportAuditLog.report_id == old_report.id)
            .where(ReportAuditLog.action == AuditAction.REPORT_PURGE)
            .order_by(ReportAuditLog.created_at.desc())
        )
        audit_log = audit_log.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.action == AuditAction.REPORT_PURGE

    @pytest.mark.asyncio
    async def test_purge_job_handles_storage_errors(self, make_report, mock_storage, test_session):
        """Test dat purge job storage errors correct afhandelt."""
        
        from app.queue.jobs import purge_deleted_reports
        
        # Create report deleted 8 days ago
        old_report = await make_report(
            id="purge-error-1",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/purge-error-1/output.pdf",
            deleted_at=datetime.now(timezone.utc) - timedelta(days=8),
            filename="purge_error_test.pdf"
        )
        
        # Mock storage to raise error
        mock_storage.delete_object.side_effect = Exception("Storage error")
        
        # Run purge job - should not crash
        await purge_deleted_reports()
        
        # Verify report is still in database (not purged due to error)
        from app.models.report import Report
        from sqlalchemy import select
        
        db_report = await test_session.execute(
            select(Report).where(Report.id == old_report.id)
        )
        assert db_report.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_soft_delete_cross_tenant_denied(self, client, make_report, other_tenant, other_user):
        """Test dat cross-tenant soft delete wordt geweigerd."""
        
        # Create report for other tenant
        other_report = await make_report(
            id="cross-del-1",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            filename="cross_tenant_delete_test.pdf"
        )
        
        # Try to soft delete with current user (different tenant)
        response = client.delete(f"/reports/{other_report.id}")
        
        # Should return 404 to mask existence
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"]
        
        # Verify report is not deleted
        from app.models.report import Report
        from sqlalchemy import select
        
        db_report = await test_session.execute(
            select(Report).where(Report.id == other_report.id)
        )
        db_report = db_report.scalar_one()
        assert db_report.deleted_at is None
