"""
Tests for reports API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import io

from app.models.user import UserRole


@pytest.fixture
def mock_storage():
    """Mock storage service."""
    with patch('app.api.reports.storage') as mock:
        mock.ensure_bucket.return_value = True
        mock.upload_fileobj.return_value = True
        mock.delete_object.return_value = True
        yield mock


@pytest.fixture
def mock_auth():
    """Mock authentication dependencies."""
    from app.auth.dependencies import get_current_active_user, get_current_admin_or_system_owner
    
    async def mock_get_current_active_user():
        # Return a mock user for testing
        user = MagicMock()
        user.id = "test-user-id"
        user.email = "test@user.com"
        user.role = UserRole.USER
        user.tenant_id = "test-tenant-id"
        return user
    
    async def mock_get_current_admin_or_system_owner():
        # Return a mock user for testing
        user = MagicMock()
        user.id = "test-user-id"
        user.email = "test@user.com"
        user.role = UserRole.USER
        user.tenant_id = "test-tenant-id"
        return user
    
    with patch('app.auth.dependencies.get_current_active_user', mock_get_current_active_user), \
         patch('app.auth.dependencies.get_current_admin_or_system_owner', mock_get_current_admin_or_system_owner):
        yield


def test_upload_report_success(client, mock_storage, mock_auth):
    """Test successful report upload."""
    # Create test file
    test_file = io.BytesIO(b"test file content")
    
    response = client.post(
        "/reports/",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "PROCESSING"


def test_upload_report_unsupported_file_type(client, mock_auth):
    """Test upload with unsupported file type."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["error"]["message"]


def test_upload_report_file_too_large(client, mock_auth):
    """Test upload with file too large."""
    # Create a large file (51MB)
    large_content = b"x" * (51 * 1024 * 1024)
    test_file = io.BytesIO(large_content)
    
    response = client.post(
        "/reports/",
        files={"file": ("large.pdf", test_file, "application/pdf")}
    )
    
    assert response.status_code == 413
    assert "File too large" in response.json()["error"]["message"]


def test_list_reports_user(client, mock_auth):
    """Test listing reports for regular user."""
    response = client.get("/reports/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_report_not_found(client, mock_auth):
    """Test getting non-existent report."""
    response = client.get("/reports/non-existent-id")
    
    assert response.status_code == 404
    assert "Report not found" in response.json()["error"]["message"]


def test_upload_report_system_owner_with_tenant(client, mock_storage, mock_auth):
    """Test system owner uploading to specific tenant."""
    # Mock system owner user
    from app.auth.dependencies import get_current_admin_or_system_owner
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = "test-user-id"
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = "test-tenant-id"
        return user
    
    with patch('app.auth.dependencies.get_current_admin_or_system_owner', mock_system_owner):
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/reports/?tenant_id=test-tenant-id",
            files={"file": ("test.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 201


def test_upload_report_system_owner_without_tenant(client, mock_auth):
    """Test system owner uploading without tenant_id."""
    # Mock system owner user
    from app.auth.dependencies import get_current_admin_or_system_owner
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = "test-user-id"
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = "test-tenant-id"
        return user
    
    with patch('app.auth.dependencies.get_current_admin_or_system_owner', mock_system_owner):
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/reports/",
            files={"file": ("test.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "tenant_id query parameter is required" in response.json()["error"]["message"]


def test_upload_report_regular_user_with_tenant(client, mock_auth):
    """Test regular user trying to specify tenant_id."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/?tenant_id=test-tenant-id",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    assert response.status_code == 403
    assert "Cannot specify tenant_id" in response.json()["error"]["message"]


def test_upload_report_unauthorized(client):
    """Test upload without authentication."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    assert response.status_code == 401


def test_upload_report_storage_error(client, mock_auth):
    """Test upload when storage fails."""
    with patch('app.api.reports.storage') as mock_storage:
        mock_storage.ensure_bucket.return_value = False
        
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/reports/",
            files={"file": ("test.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 500
        assert "Storage error" in response.json()["error"]["message"]
