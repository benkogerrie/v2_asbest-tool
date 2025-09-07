"""
Test download endpoint functionality voor Slice 6.
"""
import pytest
from http import HTTPStatus
from unittest.mock import patch

from app.models.report import ReportStatus


class TestDownloadEndpoint:
    """Test download endpoint functionality."""
    
    @pytest.mark.asyncio
    async def test_download_only_for_done_reports(self, client, auth_headers, make_report, mock_storage):
        """Test dat alleen DONE reports gedownload kunnen worden."""
        
        # Test 1: PROCESSING report → 404
        processing_report = await make_report(
            id="r1",
            status=ReportStatus.PROCESSING,
            filename="processing.pdf"
        )
        
        response = client.get(f"/reports/{processing_report.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not ready for download" in response.json()["detail"]
        assert "PROCESSING" in response.json()["detail"]
        
        # Test 2: FAILED report → 404
        failed_report = await make_report(
            id="r2",
            status=ReportStatus.FAILED,
            filename="failed.pdf"
        )
        
        response = client.get(f"/reports/{failed_report.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not ready for download" in response.json()["detail"]
        assert "FAILED" in response.json()["detail"]
        
        # Test 3: DONE zonder storage_key → 404
        done_no_storage = await make_report(
            id="r3",
            status=ReportStatus.DONE,
            storage_key=None,
            filename="done_no_storage.pdf"
        )
        
        response = client.get(f"/reports/{done_no_storage.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found in storage" in response.json()["detail"]
        
        # Test 4: DONE + storage_key → 200 + url + expires_in
        done_with_storage = await make_report(
            id="r4",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/r4/output.pdf",
            filename="done_with_storage.pdf"
        )
        
        # Mock storage to return presigned URL
        mock_storage.objects["tenants/test/reports/r4/output.pdf"] = b"fake pdf content"
        
        response = client.get(f"/reports/{done_with_storage.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert "url" in data
        assert "expires_in" in data
        assert data["url"].startswith("https://presigned.test/")
        assert data["expires_in"] == 120  # From test settings
        
        # Verify storage was called correctly
        assert mock_storage.presigned_get_url.called
        call_args = mock_storage.presigned_get_url.call_args
        assert call_args[0][0] == "tenants/test/reports/r4/output.pdf"
        assert call_args[0][1] == 120

    @pytest.mark.asyncio
    async def test_download_deleted_report_404(self, client, auth_headers, make_report):
        """Test dat deleted reports niet gedownload kunnen worden."""
        
        # Create report with deleted_at set
        deleted_report = await make_report(
            id="r5",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/r5/output.pdf",
            deleted_at=datetime.now(timezone.utc),
            filename="deleted.pdf"
        )
        
        response = client.get(f"/reports/{deleted_report.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "deleted" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_download_storage_error_500(self, client, auth_headers, make_report, mock_storage):
        """Test dat storage errors correct afgehandeld worden."""
        
        done_report = await make_report(
            id="r6",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/r6/output.pdf",
            filename="storage_error.pdf"
        )
        
        # Mock storage to raise error
        mock_storage.presigned_get_url.side_effect = FileNotFoundError("Object not found")
        
        response = client.get(f"/reports/{done_report.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert "storage error" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_download_audit_logging(self, client, auth_headers, make_report, mock_storage, test_session):
        """Test dat download acties gelogd worden in audit trail."""
        
        done_report = await make_report(
            id="r7",
            status=ReportStatus.DONE,
            storage_key="tenants/test/reports/r7/output.pdf",
            filename="audit_test.pdf"
        )
        
        mock_storage.objects["tenants/test/reports/r7/output.pdf"] = b"fake pdf content"
        
        # Count audit logs before
        from app.models.report import ReportAuditLog
        from sqlalchemy import select, func
        
        before_count = await test_session.execute(
            select(func.count(ReportAuditLog.id))
        )
        before_count = before_count.scalar()
        
        # Make download request
        response = client.get(f"/reports/{done_report.id}/download", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        
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
            .where(ReportAuditLog.report_id == done_report.id)
            .where(ReportAuditLog.action == AuditAction.REPORT_DOWNLOAD)
            .order_by(ReportAuditLog.created_at.desc())
        )
        audit_log = audit_log.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.action == AuditAction.REPORT_DOWNLOAD
        assert audit_log.user_id == auth_headers["X-Test-User"]
