"""
Tests for reports API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
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


def test_upload_report_success(client, test_user, mock_storage):
    """Test successful report upload."""
    # Create test file
    test_file = io.BytesIO(b"test file content")
    test_file.name = "test.pdf"
    
    # Mock file upload
    with patch('fastapi.UploadFile') as mock_upload_file:
        mock_upload_file.return_value.filename = "test.pdf"
        mock_upload_file.return_value.content_type = "application/pdf"
        mock_upload_file.return_value.size = 1024
        mock_upload_file.return_value.file = test_file
        
        response = client.post(
            "/reports/",
            files={"file": ("test.pdf", test_file, "application/pdf")},
            headers={"Authorization": f"Bearer {test_user.id}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "PROCESSING"


def test_upload_report_unsupported_file_type(client, test_user):
    """Test upload with unsupported file type."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/",
        files={"file": ("test.txt", test_file, "text/plain")},
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_report_file_too_large(client, test_user):
    """Test upload with file too large."""
    # Create a large file (51MB)
    large_content = b"x" * (51 * 1024 * 1024)
    test_file = io.BytesIO(large_content)
    
    response = client.post(
        "/reports/",
        files={"file": ("large.pdf", test_file, "application/pdf")},
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


def test_list_reports_user(client, test_user):
    """Test listing reports for regular user."""
    response = client.get(
        "/reports/",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_report_not_found(client, test_user):
    """Test getting non-existent report."""
    response = client.get(
        "/reports/non-existent-id",
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]


def test_upload_report_system_owner_with_tenant(client, test_user):
    """Test system owner uploading to specific tenant."""
    # Mock system owner user
    test_user.role = UserRole.SYSTEM_OWNER
    
    test_file = io.BytesIO(b"test content")
    
    with patch('app.api.reports.storage') as mock_storage:
        mock_storage.ensure_bucket.return_value = True
        mock_storage.upload_fileobj.return_value = True
        
        response = client.post(
            "/reports/?tenant_id=test-tenant-id",
            files={"file": ("test.pdf", test_file, "application/pdf")},
            headers={"Authorization": f"Bearer {test_user.id}"}
        )
    
    assert response.status_code == 201


def test_upload_report_system_owner_without_tenant(client, test_user):
    """Test system owner uploading without tenant_id."""
    # Mock system owner user
    test_user.role = UserRole.SYSTEM_OWNER
    
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/",
        files={"file": ("test.pdf", test_file, "application/pdf")},
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 400
    assert "tenant_id query parameter is required" in response.json()["detail"]


def test_upload_report_regular_user_with_tenant(client, test_user):
    """Test regular user trying to specify tenant_id."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/?tenant_id=test-tenant-id",
        files={"file": ("test.pdf", test_file, "application/pdf")},
        headers={"Authorization": f"Bearer {test_user.id}"}
    )
    
    assert response.status_code == 403
    assert "Cannot specify tenant_id" in response.json()["detail"]
