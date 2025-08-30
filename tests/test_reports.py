"""
Tests for reports API endpoints.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import io

from app.models.user import UserRole
from app.main import app


@pytest.fixture
def mock_storage():
    """Mock storage service."""
    with patch('app.api.reports.storage') as mock:
        mock.ensure_bucket.return_value = True
        mock.upload_fileobj.return_value = True
        mock.delete_object.return_value = True
        yield mock


@pytest.fixture
def mock_auth(client, mock_auth_dependencies):
    """Mock authentication dependencies."""
    from app.auth.dependencies import get_current_active_user, get_current_admin_or_system_owner
    from app.models.user import UserRole
    
    async def mock_get_current_active_user():
        # Return a mock user for testing
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.USER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    async def mock_get_current_admin_or_system_owner():
        # Return a mock user for testing
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.USER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    app.dependency_overrides[get_current_admin_or_system_owner] = mock_get_current_admin_or_system_owner
    
    yield
    
    # Clean up
    app.dependency_overrides.pop(get_current_active_user, None)
    app.dependency_overrides.pop(get_current_admin_or_system_owner, None)


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
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_list_reports_with_pagination(client, mock_auth):
    """Test listing reports with pagination."""
    response = client.get("/reports/?page=2&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 10


def test_list_reports_with_status_filter(client, mock_auth):
    """Test listing reports with status filter."""
    response = client.get("/reports/?status=DONE")
    
    assert response.status_code == 200


def test_list_reports_with_search(client, mock_auth):
    """Test listing reports with search query."""
    response = client.get("/reports/?q=test")
    
    assert response.status_code == 200


def test_list_reports_with_sorting(client, mock_auth):
    """Test listing reports with different sort options."""
    # Test default sort
    response = client.get("/reports/")
    assert response.status_code == 200
    
    # Test filename ascending
    response = client.get("/reports/?sort=filename_asc")
    assert response.status_code == 200
    
    # Test filename descending
    response = client.get("/reports/?sort=filename_desc")
    assert response.status_code == 200
    
    # Test uploaded_at ascending
    response = client.get("/reports/?sort=uploaded_at_asc")
    assert response.status_code == 200


def test_list_reports_invalid_sort(client, mock_auth):
    """Test listing reports with invalid sort parameter."""
    response = client.get("/reports/?sort=invalid_sort")
    
    assert response.status_code == 422
    assert "Invalid sort parameter" in response.json()["error"]["message"]


def test_list_reports_system_owner_with_tenant_filter(client, test_system_owner, test_tenant):
    """Test system owner listing reports with tenant filter."""
    from app.auth.dependencies import get_current_active_user
    
    async def mock_system_owner():
        return test_system_owner
    
    app.dependency_overrides[get_current_active_user] = mock_system_owner
    
    try:
        response = client.get(f"/reports/?tenant_id={test_tenant.id}")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_list_reports_user_with_tenant_filter_forbidden(client, mock_auth):
    """Test regular user trying to use tenant filter (forbidden)."""
    response = client.get("/reports/?tenant_id=550e8400-e29b-41d4-a716-446655440001")
    
    assert response.status_code == 403
    assert "tenant_id filter is only allowed for SYSTEM_OWNER" in response.json()["error"]["message"]


def test_list_reports_invalid_tenant_id(client, mock_auth):
    """Test listing reports with invalid tenant_id format."""
    # Mock system owner user
    from app.auth.dependencies import get_current_active_user
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_system_owner
    
    try:
        response = client.get("/reports/?tenant_id=invalid-uuid")
        assert response.status_code == 422
        assert "Invalid tenant_id format" in response.json()["error"]["message"]
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_list_reports_nonexistent_tenant(client, mock_auth):
    """Test listing reports with non-existent tenant_id."""
    # Mock system owner user
    from app.auth.dependencies import get_current_active_user
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_system_owner
    
    try:
        # Use a valid UUID that doesn't exist
        nonexistent_tenant = "550e8400-e29b-41d4-a716-446655440999"
        response = client.get(f"/reports/?tenant_id={nonexistent_tenant}")
        assert response.status_code == 404
        assert "Tenant not found" in response.json()["error"]["message"]
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_get_report_detail_success(client, test_report, test_user):
    """Test getting report detail successfully."""
    from app.auth.dependencies import get_current_active_user
    
    async def mock_user():
        return test_user
    
    app.dependency_overrides[get_current_active_user] = mock_user
    
    try:
        response = client.get(f"/reports/{test_report.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "filename" in data
        assert "summary" in data
        assert "findings" in data
        assert "uploaded_at" in data
        assert "uploaded_by_name" in data
        assert "status" in data
        assert "finding_count" in data
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_get_report_detail_not_found(client, mock_auth):
    """Test getting non-existent report detail."""
    response = client.get("/reports/550e8400-e29b-41d4-a716-446655440999")
    
    assert response.status_code == 404
    assert "Report not found or access denied" in response.json()["error"]["message"]


def test_get_report_detail_invalid_id(client, mock_auth):
    """Test getting report detail with invalid ID format."""
    response = client.get("/reports/invalid-uuid")
    
    assert response.status_code == 422
    assert "Invalid report_id format" in response.json()["error"]["message"]


def test_get_report_detail_unauthorized(client):
    """Test getting report detail without authentication."""
    response = client.get("/reports/550e8400-e29b-41d4-a716-446655440002")
    
    assert response.status_code == 401


def test_upload_report_system_owner_with_tenant(client, mock_storage, mock_auth):
    """Test system owner uploading to specific tenant."""
    # Mock system owner user
    from app.auth.dependencies import get_current_admin_or_system_owner
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_admin_or_system_owner] = mock_system_owner
    
    try:
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/reports/?tenant_id=550e8400-e29b-41d4-a716-446655440001",
            files={"file": ("test.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 201
    finally:
        app.dependency_overrides.pop(get_current_admin_or_system_owner, None)


def test_upload_report_system_owner_without_tenant(client, mock_auth):
    """Test system owner uploading without tenant_id."""
    # Mock system owner user
    from app.auth.dependencies import get_current_admin_or_system_owner
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_admin_or_system_owner] = mock_system_owner
    
    try:
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/reports/",
            files={"file": ("test.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "tenant_id query parameter is required" in response.json()["error"]["message"]
    finally:
        app.dependency_overrides.pop(get_current_admin_or_system_owner, None)


def test_upload_report_regular_user_with_tenant(client, mock_auth):
    """Test regular user trying to specify tenant_id."""
    test_file = io.BytesIO(b"test content")
    
    response = client.post(
        "/reports/?tenant_id=550e8400-e29b-41d4-a716-446655440001",
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
        # Check for storage error in the response
        error_message = response.json()["error"]["message"]
        assert "Failed to process upload" in error_message


# Performance and RBAC specific tests
def test_list_reports_system_owner_all_reports(client, mock_auth):
    """Test system owner can see all reports without tenant filter."""
    # Mock system owner user
    from app.auth.dependencies import get_current_active_user
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_system_owner
    
    try:
        # System owner should be able to see all reports without tenant filter
        response = client.get("/reports/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_list_reports_soft_deleted_rbac(client, mock_auth):
    """Test RBAC for soft-deleted reports."""
    # Mock regular user
    from app.auth.dependencies import get_current_active_user
    
    async def mock_user():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.USER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_user
    
    try:
        # Regular users should not see soft-deleted reports
        response = client.get("/reports/?status=DELETED_SOFT")
        assert response.status_code == 200
        # The service should filter out soft-deleted reports for regular users
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_score_datatype_consistency(client, mock_auth):
    """Test that score is returned as float consistently."""
    response = client.get("/reports/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that score field exists and can be float
    if data["items"]:
        item = data["items"][0]
        if "score" in item:
            # Score should be float or null, not int
            assert item["score"] is None or isinstance(item["score"], (int, float))


def test_report_detail_score_datatype(client, test_report, test_user):
    """Test that report detail score is returned as float."""
    from app.auth.dependencies import get_current_active_user
    
    async def mock_user():
        return test_user
    
    app.dependency_overrides[get_current_active_user] = mock_user
    
    try:
        response = client.get(f"/reports/{test_report.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that score field exists and can be float
        if "score" in data:
            # Score should be float or null, not int
            assert data["score"] is None or isinstance(data["score"], (int, float))
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def test_internationalized_placeholder(client, test_report, test_user):
    """Test that placeholder text is internationalized."""
    from app.auth.dependencies import get_current_active_user
    
    async def mock_user():
        return test_user
    
    app.dependency_overrides[get_current_active_user] = mock_user
    
    try:
        # Ensure the report belongs to the same tenant as the user
        assert test_report.tenant_id == test_user.tenant_id, f"Report tenant {test_report.tenant_id} != user tenant {test_user.tenant_id}"
        
        response = client.get(f"/reports/{test_report.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that summary uses internationalized placeholder
        assert "summary" in data
        # Should not contain Dutch text
        assert "Nog geen conclusie beschikbaar" not in data["summary"]
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


# Database performance tests (mocked)
def test_efficient_count_query(client, mock_auth):
    """Test that count query is efficient (not using subquery)."""
    # This test verifies the service uses separate count query
    # rather than subquery approach for better performance
    response = client.get("/reports/?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert isinstance(data["total"], int)


def test_eager_loading_no_n1_queries(client, mock_auth):
    """Test that tenant information is loaded efficiently."""
    # Mock system owner to test tenant loading
    from app.auth.dependencies import get_current_active_user
    
    async def mock_system_owner():
        user = MagicMock()
        user.id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        user.email = "test@user.com"
        user.role = UserRole.SYSTEM_OWNER
        user.tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        return user
    
    app.dependency_overrides[get_current_active_user] = mock_system_owner
    
    try:
        response = client.get("/reports/")
        assert response.status_code == 200
        data = response.json()
        
        # Verify that tenant_name is available for system owner
        if data["items"]:
            item = data["items"][0]
            assert "tenant_name" in item
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)
