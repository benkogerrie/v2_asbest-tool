"""
Tests for reports API endpoints.
"""
import pytest
import uuid
from io import BytesIO
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.models.report import ReportStatus, AuditAction
from app.models.user import UserRole


class TestReportUpload:
    """Test report upload functionality."""
    
    def test_upload_report_tenant_admin_success(self, client):
        """Test successful upload by tenant admin."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create test PDF file
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        # Mock storage operations
        with patch('app.services.storage.storage.ensure_bucket', return_value=True), \
             patch('app.services.storage.storage.upload_fileobj', return_value=True):
            
            response = client.post(
                "/reports/",
                files={"file": ("test_report.pdf", test_file, "application/pdf")},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test_report.pdf"
        assert data["status"] == ReportStatus.PROCESSING
        assert data["finding_count"] == 0
        assert data["score"] is None
        assert "id" in data
        assert "uploaded_at" in data
    
    def test_upload_report_system_owner_with_tenant_id(self, client):
        """Test successful upload by system owner with tenant_id."""
        # Login as system owner
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get a tenant ID first
        tenants_response = client.get(
            "/tenants/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert tenants_response.status_code == 200
        tenant_id = tenants_response.json()[0]["id"]
        
        # Create test DOCX file
        test_file = BytesIO(b"PK\x03\x04\x14\x00\x00\x00\x08\x00")  # Fake DOCX header
        test_file.name = "test_report.docx"
        
        # Mock storage operations
        with patch('app.services.storage.storage.ensure_bucket', return_value=True), \
             patch('app.services.storage.storage.upload_fileobj', return_value=True):
            
            response = client.post(
                f"/reports/?tenant_id={tenant_id}",
                files={"file": ("test_report.docx", test_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test_report.docx"
        assert data["status"] == ReportStatus.PROCESSING
    
    def test_upload_report_system_owner_missing_tenant_id(self, client):
        """Test system owner upload without tenant_id fails."""
        # Login as system owner
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create test file
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        response = client.post(
            "/reports/",
            files={"file": ("test_report.pdf", test_file, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "tenant_id" in response.json()["error"]["message"]
    
    def test_upload_report_tenant_admin_with_tenant_id_fails(self, client):
        """Test tenant admin cannot specify tenant_id."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create test file
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        response = client.post(
            "/reports/?tenant_id=some-tenant-id",
            files={"file": ("test_report.pdf", test_file, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Cannot specify tenant_id" in response.json()["error"]["message"]
    
    def test_upload_report_unsupported_file_type(self, client):
        """Test upload with unsupported file type fails."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create test file with unsupported extension
        test_file = BytesIO(b"Test content")
        test_file.name = "test_report.txt"
        
        response = client.post(
            "/reports/",
            files={"file": ("test_report.txt", test_file, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 415
        assert "Unsupported file type" in response.json()["error"]["message"]
    
    def test_upload_report_missing_file(self, client):
        """Test upload without file fails."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/reports/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    def test_upload_report_unauthorized(self, client):
        """Test upload without authentication fails."""
        # Create test file
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        response = client.post(
            "/reports/",
            files={"file": ("test_report.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 401
    
    def test_upload_report_storage_error(self, client):
        """Test upload when storage fails."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Create test file
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        # Mock storage failure
        with patch('app.services.storage.storage.ensure_bucket', return_value=False):
            response = client.post(
                "/reports/",
                files={"file": ("test_report.pdf", test_file, "application/pdf")},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 500
        assert "Storage error" in response.json()["error"]["message"]


class TestReportList:
    """Test report listing functionality."""
    
    def test_list_reports_system_owner(self, client):
        """Test system owner can see all reports."""
        # Login as system owner
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/reports/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        assert isinstance(reports, list)
    
    def test_list_reports_tenant_admin(self, client):
        """Test tenant admin can see only own tenant reports."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/reports/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        assert isinstance(reports, list)
        # All reports should belong to the same tenant
        for report in reports:
            assert report["tenant_id"] == reports[0]["tenant_id"]
    
    def test_list_reports_unauthorized(self, client):
        """Test list reports without authentication fails."""
        response = client.get("/reports/")
        assert response.status_code == 401


class TestReportDetail:
    """Test report detail functionality."""
    
    def test_get_report_system_owner(self, client):
        """Test system owner can get any report."""
        # Login as system owner
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # First upload a report
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        with patch('app.services.storage.storage.ensure_bucket', return_value=True), \
             patch('app.services.storage.storage.upload_fileobj', return_value=True):
            
            upload_response = client.post(
                "/reports/",
                files={"file": ("test_report.pdf", test_file, "application/pdf")},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        report_id = upload_response.json()["id"]
        
        # Get the report
        response = client.get(
            f"/reports/{report_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
        assert data["filename"] == "test_report.pdf"
    
    def test_get_report_tenant_admin_own_tenant(self, client):
        """Test tenant admin can get report from own tenant."""
        # Login as tenant admin
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "admin@bedrijfy.nl",
                "password": "Admin123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # First upload a report
        test_file = BytesIO(b"%PDF-1.4\n%Test PDF content")
        test_file.name = "test_report.pdf"
        
        with patch('app.services.storage.storage.ensure_bucket', return_value=True), \
             patch('app.services.storage.storage.upload_fileobj', return_value=True):
            
            upload_response = client.post(
                "/reports/",
                files={"file": ("test_report.pdf", test_file, "application/pdf")},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        report_id = upload_response.json()["id"]
        
        # Get the report
        response = client.get(
            f"/reports/{report_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
    
    def test_get_report_not_found(self, client):
        """Test getting non-existent report fails."""
        # Login as system owner
        login_response = client.post(
            "/auth/jwt/login",
            data={
                "username": "system@asbest-tool.nl",
                "password": "SystemOwner123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        fake_report_id = str(uuid.uuid4())
        response = client.get(
            f"/reports/{fake_report_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Report not found" in response.json()["error"]["message"]
    
    def test_get_report_unauthorized(self, client):
        """Test get report without authentication fails."""
        fake_report_id = str(uuid.uuid4())
        response = client.get(f"/reports/{fake_report_id}")
        assert response.status_code == 401
