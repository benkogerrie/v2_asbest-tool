"""
Object storage service for S3/MinIO compatibility.
"""
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import BinaryIO, Optional
import logging

from app.config import settings
from app.exceptions import StorageError

logger = logging.getLogger(__name__)


class ObjectStorage:
    """Object storage adapter for S3/MinIO."""
    
    def __init__(
        self,
        endpoint: str,
        region: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        use_path_style: bool = True,
        secure: bool = False
    ):
        """Initialize the storage client."""
        self.endpoint = endpoint
        self.region = region
        self.bucket = bucket
        self.use_path_style = use_path_style
        self.secure = secure
        
        # Create S3 client
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(
                s3={'addressing_style': 'path' if use_path_style else 'auto'}
            ),
            use_ssl=secure,
            verify=False  # For self-signed certificates in development
        )
        
        logger.info(f"Initialized ObjectStorage for bucket: {bucket}")
    
    def ensure_bucket(self) -> bool:
        """Ensure the bucket exists, create if it doesn't."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"Bucket {self.bucket} already exists")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it only in development
                if settings.debug:
                    try:
                        self.client.create_bucket(
                            Bucket=self.bucket,
                            CreateBucketConfiguration={
                                'LocationConstraint': self.region
                            } if self.region != 'us-east-1' else {}
                        )
                        logger.info(f"Created bucket: {self.bucket}")
                        return True
                    except ClientError as create_error:
                        logger.error(f"Failed to create bucket {self.bucket}: {create_error}")
                        return False
                else:
                    logger.error(f"Bucket {self.bucket} does not exist and auto-creation is disabled in production")
                    raise StorageError(f"Storage bucket '{self.bucket}' does not exist. Please create it manually in production.")
            else:
                logger.error(f"Error checking bucket {self.bucket}: {e}")
                raise StorageError(f"Storage error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error ensuring bucket {self.bucket}: {e}")
            raise StorageError(f"Storage error: {e}")
    
    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        object_key: str,
        content_type: str
    ) -> bool:
        """Upload a file object to storage."""
        try:
            self.client.upload_fileobj(
                fileobj,
                self.bucket,
                object_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'private'
                }
            )
            logger.info(f"Successfully uploaded {object_key} to {self.bucket}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {object_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading {object_key}: {e}")
            return False
    
    def download_fileobj(self, object_key: str) -> Optional[BinaryIO]:
        """Download a file object from storage."""
        try:
            from io import BytesIO
            fileobj = BytesIO()
            self.client.download_fileobj(
                self.bucket,
                object_key,
                fileobj
            )
            fileobj.seek(0)  # Reset to beginning
            logger.info(f"Successfully downloaded {object_key} from {self.bucket}")
            return fileobj
        except ClientError as e:
            logger.error(f"Failed to download {object_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading {object_key}: {e}")
            return None
    
    def presigned_get_url(self, object_key: str, expires: int = 3600) -> Optional[str]:
        """Generate a presigned URL for downloading an object."""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_key
                },
                ExpiresIn=expires
            )
            logger.info(f"Generated presigned URL for {object_key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {object_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL for {object_key}: {e}")
            return None
    
    def delete_object(self, object_key: str) -> bool:
        """Delete an object from storage."""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_key
            )
            logger.info(f"Successfully deleted {object_key} from {self.bucket}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {object_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting {object_key}: {e}")
            return False


# Global storage instance
storage = ObjectStorage(
    endpoint=settings.s3_endpoint,
    region=settings.s3_region,
    access_key=settings.s3_access_key_id,
    secret_key=settings.s3_secret_access_key,
    bucket=settings.s3_bucket,
    use_path_style=settings.s3_use_path_style,
    secure=settings.s3_secure
)
