from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import os
import io

from app.storage.supabase_client import upload_file_to_supabase, download_file_from_supabase, delete_file_from_supabase, supabase_client
from app.core.config import settings

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.file import FileGenerateRequest
from app.services.file_service import FileService


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

file_service = FileService()


@router.post("/generate")
def generate_file(
    request: FileGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    result = file_service.generate_file(request)
    
    if supabase_client and "file_path" in result and result.get("filename"):
        file_path = result["file_path"]
        filename = result["filename"]
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            ext = filename.split('.')[-1]
            content_type = "application/octet-stream"
            if ext == "pdf": content_type = "application/pdf"
            elif ext == "docx": content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == "xlsx": content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            supabase_path = f"generated_files/{filename}"
            upload_file_to_supabase(settings.SUPABASE_BUCKET, supabase_path, file_bytes, content_type)
            os.remove(file_path)
            result["file_path"] = supabase_path
            
    return result

@router.get("/download/{filename}")
def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    if supabase_client:
        try:
            file_bytes = download_file_from_supabase(settings.SUPABASE_BUCKET, f"generated_files/{filename}")
            return StreamingResponse(
                io.BytesIO(file_bytes),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except Exception:
            raise HTTPException(status_code=404, detail="File not found in Supabase")
            
    file_path = os.path.join("generated_files", filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )

@router.delete("/{filename}")
def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    if supabase_client:
        try:
            delete_file_from_supabase(settings.SUPABASE_BUCKET, f"generated_files/{filename}")
            return {"message": "File deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from Supabase: {str(e)}"
            )

    file_path = os.path.join("generated_files", filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {"message": "File deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )