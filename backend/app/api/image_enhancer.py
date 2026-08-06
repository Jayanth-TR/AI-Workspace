from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import Response
import logging

from app.services.image_enhancer import ImageEnhancerService
# pyrefly: ignore [missing-import]
from app.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize service
enhancer_service = ImageEnhancerService()

@router.post("/enhance")
async def enhance_event_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Enhance an uploaded event photograph for premium corporate presentations.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        # Read the uploaded image bytes
        image_bytes = await file.read()
        
        # Pass to the service for enhancement using Gemini
        enhanced_bytes = enhancer_service.enhance_image(image_bytes)
        
        # Return the enhanced image
        return Response(content=enhanced_bytes, media_type="image/jpeg")

    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enhance image.")
