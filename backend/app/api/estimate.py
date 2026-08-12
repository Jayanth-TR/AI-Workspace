from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from app.storage.s3_client import upload_file_to_s3, get_s3_client
from app.core.config import settings

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.estimate import EstimateGenerateRequest, EstimateExportRequest, EstimateRefineRequest
from app.services.estimate_service import EstimateService


router = APIRouter(
    prefix="/estimate",
    tags=["Estimate Generator"]
)

estimate_service = EstimateService()


@router.post("/generate")
def generate_estimate(
    request: EstimateGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = estimate_service.generate_estimate_data(
            request=request,
            db=db,
            current_user=current_user
        )
        return {
            "success": True,
            "estimate": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Estimate generation failed: {str(e)}"
        )


@router.post("/export")
def export_estimate(
    request: EstimateExportRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = estimate_service.export_estimate(request)
        
        if get_s3_client() and "file_path" in result and result.get("filename"):
            file_path = result["file_path"]
            filename = result["filename"]
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                ext = filename.split('.')[-1]
                content_type = "application/octet-stream"
                if ext == "pdf": content_type = "application/pdf"
                elif ext == "docx": content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                
                s3_path = f"generated_files/{filename}"
                upload_file_to_s3(settings.AWS_S3_BUCKET, s3_path, file_bytes, content_type)
                os.remove(file_path)
                result["file_path"] = s3_path
                
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Estimate export failed: {str(e)}"
        )


@router.post("/refine")
def refine_estimate(
    request: EstimateRefineRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = estimate_service.refine_estimate_conversation(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Estimate refinement failed: {str(e)}"
        )
