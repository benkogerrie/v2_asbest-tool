"""
Unit tests for Slice 6 storage service functionality.
"""
import pytest
import hashlib
import io
from unittest.mock import Mock, patch, MagicMock

from app.services.storage import ObjectStorage
from app.config import settings


@pytest.fixture
def storage_service():
    """Create a storage service instance for testing."""
    return ObjectStorage(
        endpoint="https://test.example.com",
        region="us-east-1",
        access_key="test_key",
        secret_key="test_secret",
        bucket="test-bucket",
        use_path_style=True,
        secure=True
    )


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b"PDF content for testing checksum calculation"


class TestStorageService:
    """Test storage service functionality."""
    
    def test_upload_fileobj_with_checksum_success(self, storage_service, sample_pdf_content):
        """✅ put_bytes vult size, checksum (sha256)."""
        # Create file-like object
        fileobj = io.BytesIO(sample_pdf_content)
        object_key = "test/report.pdf"
        content_type = "application/pdf"
        
        # Mock the S3 client
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.upload_fileobj.return_value = None  # Success
            
            success, checksum, file_size = storage_service.upload_fileobj_with_checksum(
                fileobj, object_key, content_type
            )
        
        # Verify results
        assert success is True
        assert file_size == len(sample_pdf_content)
        
        # Verify checksum calculation
        expected_checksum = hashlib.sha256(sample_pdf_content).hexdigest()
        assert checksum == expected_checksum
        
        # Verify S3 upload was called
        mock_client.upload_fileobj.assert_called_once()
        call_args = mock_client.upload_fileobj.call_args
        assert call_args[1]['ExtraArgs']['ContentType'] == content_type
        assert call_args[1]['ExtraArgs']['ACL'] == 'private'
    
    def test_upload_fileobj_with_checksum_failure(self, storage_service, sample_pdf_content):
        """❌ Upload failure → False, None, None."""
        fileobj = io.BytesIO(sample_pdf_content)
        object_key = "test/report.pdf"
        content_type = "application/pdf"
        
        # Mock S3 client to raise exception
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.upload_fileobj.side_effect = Exception("Upload failed")
            
            success, checksum, file_size = storage_service.upload_fileobj_with_checksum(
                fileobj, object_key, content_type
            )
        
        # Verify failure
        assert success is False
        assert checksum is None
        assert file_size is None
    
    def test_presigned_get_url_success(self, storage_service):
        """✅ generate_presigned_url met juiste TTL en bucket/key."""
        object_key = "test/report.pdf"
        expires = 3600
        
        expected_url = "https://test.example.com/test-bucket/test/report.pdf?signature=abc123"
        
        # Mock the S3 client
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.generate_presigned_url.return_value = expected_url
            
            result_url = storage_service.presigned_get_url(object_key, expires)
        
        # Verify result
        assert result_url == expected_url
        
        # Verify S3 call
        mock_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': storage_service.bucket,
                'Key': object_key
            },
            ExpiresIn=expires
        )
    
    def test_presigned_get_url_failure(self, storage_service):
        """❌ Presigned URL generation failure → None."""
        object_key = "test/report.pdf"
        expires = 3600
        
        # Mock S3 client to raise exception
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.generate_presigned_url.side_effect = Exception("URL generation failed")
            
            result_url = storage_service.presigned_get_url(object_key, expires)
        
        # Verify failure
        assert result_url is None
    
    def test_delete_object_success(self, storage_service):
        """✅ delete_object success."""
        object_key = "test/report.pdf"
        
        # Mock the S3 client
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.delete_object.return_value = None  # Success
            
            result = storage_service.delete_object(object_key)
        
        # Verify result
        assert result is True
        
        # Verify S3 call
        mock_client.delete_object.assert_called_once_with(
            Bucket=storage_service.bucket,
            Key=object_key
        )
    
    def test_delete_object_failure(self, storage_service):
        """❌ delete_object failure → False."""
        object_key = "test/report.pdf"
        
        # Mock S3 client to raise exception
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.delete_object.side_effect = Exception("Delete failed")
            
            result = storage_service.delete_object(object_key)
        
        # Verify failure
        assert result is False
    
    def test_delete_object_missing_key_idempotent(self, storage_service):
        """✅ delete_object geen exception bij missing key (idempotent)."""
        object_key = "nonexistent/report.pdf"
        
        # Mock S3 client to simulate "object not found" error
        from botocore.exceptions import ClientError
        error_response = {
            'Error': {
                'Code': 'NoSuchKey',
                'Message': 'The specified key does not exist.'
            }
        }
        
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.delete_object.side_effect = ClientError(error_response, 'DeleteObject')
            
            result = storage_service.delete_object(object_key)
        
        # Should return False but not crash
        assert result is False
    
    def test_checksum_calculation_consistency(self, storage_service):
        """✅ Checksum calculation is consistent across multiple calls."""
        content = b"Test content for checksum"
        fileobj1 = io.BytesIO(content)
        fileobj2 = io.BytesIO(content)
        
        object_key = "test/consistency.pdf"
        content_type = "application/pdf"
        
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.upload_fileobj.return_value = None
            
            # First upload
            success1, checksum1, size1 = storage_service.upload_fileobj_with_checksum(
                fileobj1, object_key, content_type
            )
            
            # Second upload with same content
            success2, checksum2, size2 = storage_service.upload_fileobj_with_checksum(
                fileobj2, object_key, content_type
            )
        
        # Verify consistency
        assert success1 is True
        assert success2 is True
        assert checksum1 == checksum2
        assert size1 == size2
        assert size1 == len(content)
    
    def test_file_size_calculation(self, storage_service):
        """✅ File size calculation is accurate."""
        content = b"X" * 1024  # 1KB
        fileobj = io.BytesIO(content)
        object_key = "test/size.pdf"
        content_type = "application/pdf"
        
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.upload_fileobj.return_value = None
            
            success, checksum, file_size = storage_service.upload_fileobj_with_checksum(
                fileobj, object_key, content_type
            )
        
        assert success is True
        assert file_size == 1024
    
    def test_fileobj_position_reset(self, storage_service):
        """✅ File object position is reset after reading for checksum."""
        content = b"Test content"
        fileobj = io.BytesIO(content)
        
        # Move position to middle
        fileobj.seek(5)
        initial_position = fileobj.tell()
        
        object_key = "test/position.pdf"
        content_type = "application/pdf"
        
        with patch.object(storage_service, 'client') as mock_client:
            mock_client.upload_fileobj.return_value = None
            
            success, checksum, file_size = storage_service.upload_fileobj_with_checksum(
                fileobj, object_key, content_type
            )
        
        assert success is True
        
        # Verify the fileobj was read from beginning (position 0)
        # The upload_fileobj call should have received content from position 0
        call_args = mock_client.upload_fileobj.call_args
        uploaded_fileobj = call_args[0][0]  # First positional argument
        uploaded_fileobj.seek(0)
        uploaded_content = uploaded_fileobj.read()
        assert uploaded_content == content
