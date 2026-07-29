from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os

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
    return file_service.generate_file(
        request
    )

@router.get("/download/{filename}")
def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
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