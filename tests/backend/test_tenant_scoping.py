"""
Test tenant scoping en data isolation voor Slice 6.
"""
import pytest
import uuid
from http import HTTPStatus
from datetime import datetime, timezone

from app.models.report import ReportStatus
from app.models.user import UserRole


class TestTenantScoping:
    """Test tenant isolation en data scoping."""
    
    @pytest.fixture
    async def other_tenant(self, test_session):
        """Create another tenant for cross-tenant testing."""
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Other Tenant Beta",
            kvk="87654321",
            contact_email="other@tenant.com",
            is_active=True
        )
        test_session.add(tenant)
        await test_session.commit()
        await test_session.refresh(tenant)
        return tenant
    
    @pytest.fixture
    async def other_user(self, test_session, other_tenant):
        """Create user in other tenant."""
        user = User(
            id=uuid.uuid4(),
            email="other@example.com",
            tenant_id=other_tenant.id,
            first_name="Other",
            last_name="User",
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
            hashed_password="hashed_password_for_testing"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        return user

    @pytest.mark.asyncio
    async def test_cross_tenant_download_denied(self, client, make_report, other_tenant, other_user, mock_storage):
        """Test dat cross-tenant download access wordt geweigerd."""
        
        # Create report for other tenant
        other_report = await make_report(
            id="cross-1",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            storage_key="tenants/other/reports/cross-1/output.pdf",
            filename="other_tenant_report.pdf"
        )
        
        # Mock storage for other tenant's report
        mock_storage.objects["tenants/other/reports/cross-1/output.pdf"] = b"other tenant pdf content"
        
        # Try to download with current user (different tenant)
        # Note: auth_headers contains current user from conftest
        response = client.get(f"/reports/{other_report.id}/download")
        
        # Should return 404 to mask existence (no data leakage)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_cross_tenant_list_access_denied(self, client, make_report, other_tenant, other_user):
        """Test dat cross-tenant reports niet zichtbaar zijn in lijst."""
        
        # Create report for other tenant
        other_report = await make_report(
            id="cross-2",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            filename="other_tenant_secret.pdf"
        )
        
        # Create report for current tenant
        current_report = await make_report(
            id="current-1",
            status=ReportStatus.DONE,
            filename="current_tenant_report.pdf"
        )
        
        # Get reports list
        response = client.get("/reports/")
        assert response.status_code == HTTPStatus.OK
        
        reports = response.json()
        report_ids = [report["id"] for report in reports]
        
        # Should only see current tenant's reports
        assert str(current_report.id) in report_ids
        assert str(other_report.id) not in report_ids

    @pytest.mark.asyncio
    async def test_cross_tenant_soft_delete_denied(self, client, make_report, other_tenant, other_user):
        """Test dat cross-tenant soft delete wordt geweigerd."""
        
        # Create report for other tenant
        other_report = await make_report(
            id="cross-3",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            filename="other_tenant_delete_test.pdf"
        )
        
        # Try to soft delete with current user (different tenant)
        response = client.delete(f"/reports/{other_report.id}")
        
        # Should return 404 to mask existence
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_cross_tenant_sse_stream_isolation(self, client, make_report, other_tenant, other_user):
        """Test dat SSE stream alleen updates voor eigen tenant toont."""
        
        # Create reports for both tenants
        current_report = await make_report(
            id="sse-current-1",
            status=ReportStatus.PROCESSING,
            filename="current_tenant_processing.pdf"
        )
        
        other_report = await make_report(
            id="sse-other-1",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.PROCESSING,
            filename="other_tenant_processing.pdf"
        )
        
        # Start SSE stream
        with client.stream("GET", "/reports/stream") as stream:
            assert stream.status_code == HTTPStatus.OK
            assert stream.headers["content-type"].startswith("text/event-stream")
            
            # Read initial data
            lines = []
            for line in stream.iter_lines():
                if line:
                    lines.append(line.decode("utf-8"))
                    if len(lines) >= 5:  # Read a few lines
                        break
            
            # Check that we only see current tenant's data
            stream_content = "\n".join(lines)
            assert str(current_report.id) in stream_content
            assert str(other_report.id) not in stream_content

    @pytest.mark.asyncio
    async def test_tenant_isolation_in_report_service(self, test_session, make_report, other_tenant, other_user):
        """Test dat ReportService tenant isolation respecteert."""
        
        from app.services.reports import ReportService
        
        # Create reports for both tenants
        current_report = await make_report(
            id="service-current-1",
            status=ReportStatus.DONE,
            filename="current_service_test.pdf"
        )
        
        other_report = await make_report(
            id="service-other-1",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            filename="other_service_test.pdf"
        )
        
        # Create service with current user context
        service = ReportService(test_session)
        
        # Mock current user (from conftest)
        from app.models.user import User
        current_user = await test_session.get(User, current_report.uploaded_by)
        
        # Test get_report_for_download with current user
        result = await service.get_report_for_download(current_report.id, current_user)
        assert result is not None
        assert result.id == current_report.id
        
        # Test get_report_for_download with other tenant's report
        result = await service.get_report_for_download(other_report.id, current_user)
        assert result is None  # Should not find other tenant's report

    @pytest.mark.asyncio
    async def test_audit_logs_tenant_scoped(self, client, make_report, other_tenant, other_user, test_session):
        """Test dat audit logs tenant-scoped zijn."""
        
        from app.models.report import ReportAuditLog
        from sqlalchemy import select
        
        # Create report for other tenant
        other_report = await make_report(
            id="audit-cross-1",
            tenant_id=other_tenant.id,
            uploaded_by=other_user.id,
            status=ReportStatus.DONE,
            filename="other_audit_test.pdf"
        )
        
        # Try to access other tenant's report (should fail)
        response = client.get(f"/reports/{other_report.id}/download")
        assert response.status_code == HTTPStatus.NOT_FOUND
        
        # Check that no audit log was created for other tenant's report
        audit_logs = await test_session.execute(
            select(ReportAuditLog)
            .where(ReportAuditLog.report_id == other_report.id)
        )
        audit_logs = audit_logs.scalars().all()
        
        # Should be empty - no audit log for cross-tenant access
        assert len(audit_logs) == 0
