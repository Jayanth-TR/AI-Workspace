import json
import logging
from typing import Optional, Dict, Any, List
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.estimate import EstimateGenerateRequest, EstimateExportRequest, EstimateLineItem
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

llm_service = LLMService()
rag_service = RAGService()
file_service = FileService()


class EstimateService:
    """Service to handle Estimate generation and export for Beats Production Private Limited."""

    def generate_estimate_data(
        self,
        request: EstimateGenerateRequest,
        db: Optional[Session] = None,
        current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        # If line items are provided explicitly, format and return them directly
        if request.line_items and len(request.line_items) > 0:
            formatted_items = []
            for idx, item in enumerate(request.line_items, 1):
                qty = float(item.qty or 1)
                rate = float(item.rate or 0)
                amount = qty * rate if item.amount is None else float(item.amount)
                formatted_items.append({
                    "sl": idx,
                    "description": item.description,
                    "qty": qty,
                    "rate": rate,
                    "amount": amount
                })

            subtotal = sum(i["amount"] for i in formatted_items)
            tax_rate = float(request.tax_rate or 18.0)
            tax_amount = round(subtotal * (tax_rate / 100.0), 2)
            total = round(subtotal + tax_amount, 2)

            return {
                "quote_no": request.quote_no or "BLR-2025-26-109",
                "quote_date": request.quote_date or "12 May, 2026",
                "event_date": request.event_date or "09-05-2026",
                "company_name": request.company_name or "Artiligent Solutions Private Limited",
                "address": request.address or "101, Dev-Virat, Ashok Nagar Cr Rd 2, Kandivali East, Mumbai 400101, Maharashtra",
                "gst_no": request.gst_no or "27AAQCA6935R1ZN",
                "line_items": formatted_items,
                "tax_type": request.tax_type or "IGST",
                "tax_rate": tax_rate,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total": total
            }

        # Otherwise use LLM to parse natural language prompt into structured estimate items
        prompt = request.prompt or "Estimate for event technical services including robot rental and transportation"
        
        system_instruction = """
You are an AI Estimate Assistant for Beats Production Private Limited.
Analyze the user prompt and extract/generate line items for an official commercial Estimate.
Return ONLY valid JSON in the exact schema below (no markdown block wrapper):
{
  "quote_no": "BLR-2025-26-109",
  "quote_date": "12 May, 2026",
  "event_date": "09-05-2026",
  "company_name": "Artiligent Solutions Private Limited",
  "address": "101, Dev-Virat, Ashok Nagar Cr Rd 2, Kandivali East, Mumbai 400101, Maharashtra",
  "gst_no": "27AAQCA6935R1ZN",
  "tax_type": "IGST",
  "tax_rate": 18,
  "line_items": [
    {"sl": 1, "description": "Temi Robot", "qty": 1, "rate": 25000},
    {"sl": 2, "description": "Transportation", "qty": 1, "rate": 3500}
  ]
}
"""

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Prompt details: {prompt}"}
        ]

        llm_resp = llm_service.generate_response(messages)
        llm_resp = llm_resp.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(llm_resp)
        except Exception as e:
            logger.warning(f"Failed to parse LLM estimate response as JSON, falling back to default structure: {e}")
            parsed = {
                "quote_no": request.quote_no or "BLR-2025-26-109",
                "quote_date": request.quote_date or "12 May, 2026",
                "event_date": request.event_date or "09-05-2026",
                "company_name": request.company_name or "Artiligent Solutions Private Limited",
                "address": request.address or "101, Dev-Virat, Ashok Nagar Cr Rd 2, Kandivali East, Mumbai",
                "gst_no": request.gst_no or "27AAQCA6935R1ZN",
                "tax_type": "IGST",
                "tax_rate": 18,
                "line_items": [
                    {"sl": 1, "description": "Temi Robot", "qty": 1, "rate": 25000},
                    {"sl": 2, "description": "Transportation", "qty": 1, "rate": 3500}
                ]
            }

        line_items = []
        for idx, item in enumerate(parsed.get("line_items", []), 1):
            q = float(item.get("qty", 1))
            r = float(item.get("rate", 0))
            line_items.append({
                "sl": idx,
                "description": item.get("description", "Service"),
                "qty": q,
                "rate": r,
                "amount": round(q * r, 2)
            })

        subtotal = sum(i["amount"] for i in line_items)
        tax_rate = float(parsed.get("tax_rate", 18))
        tax_amount = round(subtotal * (tax_rate / 100.0), 2)
        total = round(subtotal + tax_amount, 2)

        return {
            "quote_no": parsed.get("quote_no", "BLR-2025-26-109"),
            "quote_date": parsed.get("quote_date", "12 May, 2026"),
            "event_date": parsed.get("event_date", "09-05-2026"),
            "company_name": parsed.get("company_name", request.company_name or "Artiligent Solutions Private Limited"),
            "address": parsed.get("address", request.address or "101, Dev-Virat, Ashok Nagar Cr Rd 2, Kandivali East, Mumbai"),
            "gst_no": parsed.get("gst_no", request.gst_no or "27AAQCA6935R1ZN"),
            "line_items": line_items,
            "tax_type": parsed.get("tax_type", "IGST"),
            "tax_rate": tax_rate,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total": total
        }

    def export_estimate(self, request: EstimateExportRequest) -> dict:
        formatted_items = []
        for idx, item in enumerate(request.line_items, 1):
            q = float(item.qty or 1)
            r = float(item.rate or 0)
            amt = q * r if item.amount is None else float(item.amount)
            formatted_items.append({
                "sl": idx,
                "description": item.description,
                "qty": q,
                "rate": r,
                "amount": amt
            })

        subtotal = sum(i["amount"] for i in formatted_items)
        tax_rate = float(request.tax_rate or 18.0)
        tax_amount = round(subtotal * (tax_rate / 100.0), 2)
        total = round(subtotal + tax_amount, 2)

        estimate_data = {
            "title": request.title or "ESTIMATE",
            "quote_no": request.quote_no or "BLR-2025-26-109",
            "quote_date": request.quote_date or "12 May, 2026",
            "event_date": request.event_date or "09-05-2026",
            "client_name": request.client_name or "",
            "company_name": request.company_name or "Artiligent Solutions Private Limited",
            "address": request.address or "101, Dev-Virat, Ashok Nagar Cr Rd 2, Kandivali East, Mumbai 400101, Maharashtra",
            "gst_no": request.gst_no or "27AAQCA6935R1ZN",
            "line_items": formatted_items,
            "tax_type": request.tax_type or "IGST",
            "tax_rate": tax_rate,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total": total
        }

        if request.format.lower() == "docx":
            return file_service.create_estimate_word(estimate_data)
        return file_service.create_estimate_pdf(estimate_data)

    def refine_estimate_conversation(
        self,
        request: Any, # EstimateRefineRequest schema
    ) -> Dict[str, Any]:
        system_instruction = """
You are an AI Estimate Assistant for Beats Production Private Limited.
Your goal is to gather the necessary details to generate a professional commercial Estimate.
The necessary details we need to collect from the user are:
1. Company Name (e.g., EY Company)
2. Client Name (the contact person at that company)
3. Event Date (the date of the event/project)
4. Line Items (the list of specific technical/production services, with their quantities and unit rates/prices)

RULES:
- Read the initial prompt and the subsequent conversation history carefully.
- If ANY of these key details are missing, you MUST ask the user for them ONE BY ONE. Do not ask for multiple missing details in a single message. Keep the tone helpful, clear, and professional.
- When asking a question, return a JSON object in this format:
  {
    "status": "needs_info",
    "question": "<Your next question asking for exactly one missing detail>",
    "missing_field": "<the field name, e.g. client_name, event_date, or line_items>"
  }
- If all necessary details are present, compile them and return a JSON object in this format:
  {
    "status": "completed",
    "estimate": {
      "quote_no": "<quote number, generate a default like 'BP/EST/26-27/001' if not specified>",
      "quote_date": "<current date or specified date>",
      "event_date": "<event date>",
      "company_name": "<company name>",
      "client_name": "<client name>",
      "address": "<address, generate a realistic default or leave empty if not known>",
      "gst_no": "<GST number, leave blank or default if not known>",
      "tax_type": "IGST",
      "tax_rate": 18,
      "line_items": [
        {"sl": 1, "description": "<description of item>", "qty": <quantity>, "rate": <unit rate>}
      ]
    }
  }

Return ONLY valid JSON. Do not include markdown blocks or any extra text.
"""
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Initial Prompt: {request.prompt}"}
        ]

        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        llm_resp = "{}"
        if llm_service.client:
            try:
                response = llm_service.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                llm_resp = response.choices[0].message.content or "{}"
            except Exception as e:
                logger.error(f"OpenAI call in refine_estimate_conversation failed: {e}")

        try:
            parsed = json.loads(llm_resp)
            return parsed
        except Exception as e:
            logger.warning(f"Failed to parse LLM refinement response: {e}. Raw response: {llm_resp}")
            # Fallback to asking for event date if parser failed
            return {
                "status": "needs_info",
                "question": "Could you please specify the event date for this estimate?",
                "missing_field": "event_date"
            }
