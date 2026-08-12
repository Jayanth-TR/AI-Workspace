# pyrefly: ignore [missing-import]
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Initializes and returns the AWS S3 client using boto3.
    Returns None if AWS_S3_BUCKET is not configured.
    """
    if not settings.AWS_S3_BUCKET:
        logger.warning("AWS_S3_BUCKET is not provided. S3 storage operations will fall back to local disk.")
        return None

    kwargs = {}
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    if settings.AWS_REGION:
        kwargs["region_name"] = settings.AWS_REGION

    try:
        return boto3.client("s3", **kwargs)
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return None


def upload_file_to_s3(bucket_name: str, file_path: str, file_bytes: bytes, content_type: str = "application/octet-stream") -> str:
    """
    Uploads a file to AWS S3 bucket and returns the object key/path.
    """
    client = get_s3_client()
    if not client:
        raise ValueError("S3 client is not initialized.")
    bucket = bucket_name or settings.AWS_S3_BUCKET
    client.put_object(
        Bucket=bucket,
        Key=file_path,
        Body=file_bytes,
        ContentType=content_type
    )
    return file_path


def delete_file_from_s3(bucket_name: str, file_path: str):
    """
    Deletes a file from AWS S3 bucket.
    """
    client = get_s3_client()
    if not client:
        raise ValueError("S3 client is not initialized.")
    bucket = bucket_name or settings.AWS_S3_BUCKET
    client.delete_object(Bucket=bucket, Key=file_path)


def get_public_url(bucket_name: str, file_path: str) -> str:
    """
    Gets the public HTTPS URL for a file in AWS S3 storage.
    """
    bucket = bucket_name or settings.AWS_S3_BUCKET
    region = settings.AWS_REGION or "us-east-1"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{file_path}"


def download_file_from_s3(bucket_name: str, file_path: str) -> bytes:
    """
    Downloads a file from AWS S3 storage as bytes.
    """
    client = get_s3_client()
    if not client:
        raise ValueError("S3 client is not initialized.")
    bucket = bucket_name or settings.AWS_S3_BUCKET
    response = client.get_object(Bucket=bucket, Key=file_path)
    return response["Body"].read()
