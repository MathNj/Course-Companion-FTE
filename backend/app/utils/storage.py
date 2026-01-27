"""
Cloudflare R2 Storage Utilities

S3-compatible storage client for course content and assets.
"""

import logging
from typing import Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)


class R2StorageClient:
    """
    Cloudflare R2 storage client using S3-compatible API.

    Handles uploading, downloading, and managing course content stored in R2.
    """

    def __init__(self):
        """Initialize R2 client with credentials from settings."""
        self.client = None
        self.bucket_name = settings.r2_bucket_name

        # Only initialize if R2 credentials are configured
        if all([
            settings.r2_account_id,
            settings.r2_access_key_id,
            settings.r2_secret_access_key,
            settings.r2_endpoint
        ]):
            self.client = boto3.client(
                's3',
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                region_name='auto',  # Cloudflare R2 uses 'auto'
            )
            logger.info("R2 storage client initialized successfully")
        else:
            logger.warning("R2 credentials not configured - storage features disabled")

    def is_configured(self) -> bool:
        """Check if R2 storage is properly configured."""
        return self.client is not None

    def upload_file(
        self,
        file_obj: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Upload a file to R2 storage.

        Args:
            file_obj: File-like object to upload
            object_key: Object key/path in R2 (e.g., 'chapters/chapter-1/video.mp4')
            content_type: MIME type of the file
            metadata: Optional metadata dictionary

        Returns:
            True if upload successful, False otherwise
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return False

        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata

            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )

            logger.info(f"Successfully uploaded {object_key} to R2")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload {object_key} to R2: {e}")
            return False

    def download_file(self, object_key: str, file_obj: BinaryIO) -> bool:
        """
        Download a file from R2 storage.

        Args:
            object_key: Object key/path in R2
            file_obj: File-like object to write downloaded content

        Returns:
            True if download successful, False otherwise
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return False

        try:
            self.client.download_fileobj(
                self.bucket_name,
                object_key,
                file_obj
            )

            logger.info(f"Successfully downloaded {object_key} from R2")
            return True

        except ClientError as e:
            logger.error(f"Failed to download {object_key} from R2: {e}")
            return False

    def get_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
        http_method: str = "get_object"
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to an object.

        Args:
            object_key: Object key/path in R2
            expiration: URL expiration time in seconds (default 1 hour)
            http_method: HTTP method ('get_object' or 'put_object')

        Returns:
            Presigned URL string if successful, None otherwise
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return None

        try:
            url = self.client.generate_presigned_url(
                http_method,
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )

            logger.info(f"Generated presigned URL for {object_key}")
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {object_key}: {e}")
            return None

    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from R2 storage.

        Args:
            object_key: Object key/path in R2

        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return False

        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )

            logger.info(f"Successfully deleted {object_key} from R2")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete {object_key} from R2: {e}")
            return False

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        List objects in R2 storage with optional prefix filter.

        Args:
            prefix: Prefix to filter objects (e.g., 'chapters/')
            max_keys: Maximum number of objects to return

        Returns:
            List of object metadata dictionaries
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return []

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = response.get('Contents', [])
            logger.info(f"Listed {len(objects)} objects with prefix '{prefix}'")

            return objects

        except ClientError as e:
            logger.error(f"Failed to list objects with prefix '{prefix}': {e}")
            return []

    def get_markdown_file(self, object_key: str) -> Optional[str]:
        """
        Fetch a markdown file from R2 and return its content as string.

        Args:
            object_key: Object key/path in R2 (e.g., 'Generative AI Fundamentals/Chapter 1 — The Age of Synthesis_ An Introduction to Generative AI.md')

        Returns:
            Markdown content as string, or None if not found
        """
        if not self.is_configured():
            logger.error("R2 storage not configured")
            return None

        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )

            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully fetched markdown file: {object_key}")

            return content

        except self.client.exceptions.NoSuchKey:
            logger.warning(f"Markdown file not found: {object_key}")
            return None
        except ClientError as e:
            logger.error(f"Failed to fetch markdown file {object_key}: {e}")
            return None

    def list_chapters(self, prefix: str = "Generative AI Fundamentals/") -> list[dict]:
        """
        List all chapter files in the R2 bucket.

        Args:
            prefix: Directory prefix for chapters (default: 'Generative AI Fundamentals/')

        Returns:
            List of chapter metadata dictionaries with name, size, and key
        """
        objects = self.list_objects(prefix=prefix)

        chapters = []
        for obj in objects:
            key = obj['Key']
            if key.endswith('.md'):
                # Extract chapter name from key
                name = key.replace(prefix, '').replace('.md', '')
                chapters.append({
                    'name': name,
                    'key': key,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })

        logger.info(f"Found {len(chapters)} chapter files")
        return chapters


# Global R2 client instance
r2_client = R2StorageClient()
