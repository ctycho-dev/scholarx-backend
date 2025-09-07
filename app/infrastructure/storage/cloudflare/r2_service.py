# r2_service.py
import boto3
from botocore.client import Config
from botocore.exceptions import (
    ConnectionError,
    EndpointConnectionError,
    ReadTimeoutError,
)
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger()


class CloudflareR2Service:
    def __init__(self):
        self.s3_client = None
        self.endpoint = settings.R2_ENDPOINT
        self._access_key = settings.R2_ACCESS_KEY
        self._secret_key = settings.R2_SECRET_KEY

        self.connect()

    def connect(self):
        """Create or recreate the S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                config=Config(
                    signature_version='s3v4',
                    s3={'addressing_style': 'virtual'},
                    retries={'max_attempts': 3},
                    connect_timeout=10,
                    read_timeout=30
                )
            )
            logger.info("Connected to Cloudflare R2")
        except Exception as e:
            logger.error('Failed to connect to Cloudflare R2: %s', e)
            raise e
    
    def disconnect(self):
        """
        Close the underlying S3 client connections gracefully.
        This releases HTTP connections and avoids resource leaks.
        """
        if self.s3_client is not None:
            try:
                self.s3_client.close()
                logger.info("Cloudflare R2 client connection closed.")
            except Exception as e:
                logger.warning("Error closing R2 client: %s", e)
            finally:
                self.s3_client = None
        else:
            logger.debug("No R2 client to disconnect.")

    def _ensure_connection(self):
        if self.s3_client is None:
            logger.warning("R2 client not initialized. Reconnecting...")
            self.connect()

    def _call_with_reconnect(self, func, *args, **kwargs):
        self._ensure_connection()
        try:
            return func(*args, **kwargs)
        except (ConnectionError, EndpointConnectionError, ReadTimeoutError) as e:
            logger.warning("R2 connection failed: %s. Reconnecting...", e)
            self.connect()
            try:
                return func(*args, **kwargs)
            except Exception as retry_error:
                logger.error("R2 request failed after reconnect: %s", retry_error)
                raise Exception("Temporary upload service unavailable") from retry_error
        except Exception as e:
            logger.error("R2 request failed: %s", e)
            raise

    def make_public_url(self, bucket: str, key: str) -> str:
        """
        Generate public URL using: https://{bucket}.mypinx.store/{key}
        """
        # Sanitize bucket name if needed
        safe_bucket = bucket.lower().strip()
        return f"https://{safe_bucket}.mypinx.store/{key.lstrip('/')}"

    def make_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        expires_in: int = 300
    ) -> str:
        """
        Generate presigned URL for direct frontend upload.
        Bucket is passed at call time.
        """
        def _action():
            return self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
        return self._call_with_reconnect(_action)

    def delete_file(self, bucket: str, key: str):
        """
        Delete file from specific bucket.
        """
        def _action():
            return self.s3_client.delete_object(Bucket=bucket, Key=key)
        return self._call_with_reconnect(_action)

    def upload_fileobj(self, file_obj, bucket: str, key: str, content_type: str):
        """
        Upload file-like object to R2
        """
        def _action():
            return self.s3_client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs={'ContentType': content_type}
            )
        return self._call_with_reconnect(_action)