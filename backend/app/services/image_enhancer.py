import os
import io
import base64
import time
from typing import Optional
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
from app.core.config import settings

class ImageEnhancerService:
    """
    Service responsible for taking an uploaded event photograph and applying
    professional enhancements by sending it to a Gemini LLM.
    """

    def __init__(self):
        # We assume GEMINI_API_KEY is available in the environment 
        # (loaded via dotenv in main app config).
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-3.1-flash-image'

    def enhance_image(self, image_bytes: bytes) -> bytes:
        """
        Enhances the input image bytes by calling the Gemini model.
        """
        prompt = (
            "Transform the uploaded image into a high-quality professional version while preserving the original subject, composition, and overall scene."
            "Enhance sharpness, clarity, resolution, lighting, colors, contrast, dynamic range, and fine details. Reduce noise, remove compression artifacts, improve white balance, and apply natural color grading."
            "Keep the image realistic and visually appealing. Do not add, remove, or alter people, objects, text, logos, or the background unless explicitly requested."
            "Generate a clean, premium-quality image suitable for presentations, websites, marketing materials, social media, and print.."
        )

        current_model = self.model_name
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Prepare the image part for the Gemini request
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg'
                )
    
                # Request generation
                # Based on user's instruction, gemini-3.1-flash can perform image-to-image.
                # It may return the modified image as a Part with mime_type image/jpeg,
                # or as base64 text if configured that way. We'll handle both.
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=[image_part, prompt],
                    config=types.GenerateContentConfig(response_modalities=["IMAGE"])
                )
                
                # Check the response parts to see if it returned an image part directly
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        if part.inline_data.mime_type.startswith('image/'):
                            return part.inline_data.data
                            
                # If no inline_data image part is found, check if it returned base64 text
                if response.text:
                    # Basic check if it's base64 string
                    text = response.text.strip()
                    # Remove data URI scheme if present
                    if "base64," in text:
                        text = text.split("base64,")[1]
                    
                    try:
                        return base64.b64decode(text)
                    except Exception:
                        pass
    
                raise ValueError("Could not extract image from Gemini response. Ensure the prompt explicitly requests image output or check model compatibility.")
    
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt
                        print(f"Attempt {attempt + 1} with {current_model} failed with {error_msg}. Switching to Gemini 3 Pro Image and retrying in {sleep_time} seconds...")
                        current_model = 'gemini-3-pro-image'
                        time.sleep(sleep_time)
                        continue
                print(f"Error calling Gemini to enhance image after {attempt + 1} attempts: {e}")
                raise e
