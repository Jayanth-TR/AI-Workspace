# pyrefly: ignore [missing-import]
from supabase import create_client, Client
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Initializes and returns the Supabase client.
    Returns None if URL or Key is missing.
    """
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_SERVICE_KEY
    if not url or not key:
        logger.warning("Supabase URL and Key are not provided. Storage operations will fail.")
        return None
    return create_client(url, key)

supabase_client: Client = get_supabase_client()

def upload_file_to_supabase(bucket_name: str, file_path: str, file_bytes: bytes, content_type: str = "application/octet-stream") -> str:
    """
    Uploads a file to Supabase storage and returns the path.
    """
    if not supabase_client:
        raise ValueError("Supabase client is not initialized.")
    res = supabase_client.storage.from_(bucket_name).upload(
        file_path, 
        file_bytes, 
        {"content-type": content_type}
    )
    return file_path

def delete_file_from_supabase(bucket_name: str, file_path: str):
    """
    Deletes a file from Supabase storage.
    """
    if not supabase_client:
        raise ValueError("Supabase client is not initialized.")
    res = supabase_client.storage.from_(bucket_name).remove([file_path])
    return res

def get_public_url(bucket_name: str, file_path: str) -> str:
    """
    Gets the public URL for a file in Supabase storage.
    """
    if not supabase_client:
        raise ValueError("Supabase client is not initialized.")
    res = supabase_client.storage.from_(bucket_name).get_public_url(file_path)
    return res

def download_file_from_supabase(bucket_name: str, file_path: str) -> bytes:
    """
    Downloads a file from Supabase storage as bytes.
    """
    if not supabase_client:
        raise ValueError("Supabase client is not initialized.")
    res = supabase_client.storage.from_(bucket_name).download(file_path)
    return res
