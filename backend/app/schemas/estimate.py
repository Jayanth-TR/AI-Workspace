from typing import List, Optional
from pydantic import BaseModel


class EstimateLineItem(BaseModel):
    sl: Optional[int] = 1
    description: str
    qty: float = 1.0
    rate: float = 0.0
    amount: Optional[float] = None


class EstimateGenerateRequest(BaseModel):
    prompt: Optional[str] = ""
    quote_no: Optional[str] = ""
    quote_date: Optional[str] = ""
    event_date: Optional[str] = ""
    client_name: Optional[str] = ""
    company_name: Optional[str] = ""
    address: Optional[str] = ""
    gst_no: Optional[str] = ""
    tax_type: Optional[str] = "IGST"  # IGST or CGST_SGST
    tax_rate: Optional[float] = 18.0
    line_items: Optional[List[EstimateLineItem]] = []
    company_knowledge_override: Optional[str] = ""


class EstimateExportRequest(BaseModel):
    title: Optional[str] = "ESTIMATE"
    quote_no: Optional[str] = "BLR-2025-26-109"
    quote_date: Optional[str] = ""
    event_date: Optional[str] = ""
    client_name: Optional[str] = ""
    company_name: Optional[str] = ""
    address: Optional[str] = ""
    gst_no: Optional[str] = ""
    line_items: List[EstimateLineItem] = []
    tax_type: Optional[str] = "IGST"
    tax_rate: Optional[float] = 18.0
    format: str = "pdf"  # pdf or docx


class EstimateChatRefineMessage(BaseModel):
    role: str
    content: str


class EstimateRefineRequest(BaseModel):
    prompt: str
    history: List[EstimateChatRefineMessage] = []
