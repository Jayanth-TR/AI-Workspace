# pyrefly: ignore [missing-import]
from openai import OpenAI
import json
from app.core.config import settings


class LLMService:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def generate_response(
        self,
        conversation: list
    ) -> str:
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=conversation
        )
        return response.output_text

    def detect_request_type(
        self,
        prompt: str
    ):
        prompt_lower = prompt.lower()

        file_action_keywords = [
            "generate file",
            "create file",
            "download file",
            "make a file",
            "generate pdf",
            "create pdf",
            "download pdf",
            "make a pdf",
            "export pdf",
            "generate docx",
            "create docx",
            "generate word",
            "create word",
            "generate excel",
            "create excel",
            "generate xlsx",
            "export to excel",
            "create spreadsheet",
            "export excel",
            "export docx"
        ]

        if any(keyword in prompt_lower for keyword in file_action_keywords):
            return {
                "type": "file"
            }

        instruction = f"""
        Determine whether the user is explicitly requesting to CREATE or GENERATE a new downloadable document/file (such as creating a new PDF, Word, or Excel file), OR simply asking a question/having a conversation.

        Return ONLY JSON:
        {{"type": "file"}} if they want to generate/create a downloadable file.
        {{"type": "chat"}} if they are asking a question, analyzing data, or having a chat.

        User Request:
        {prompt}
        """

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=instruction
            )
            output = response.output_text.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(output)
            if isinstance(parsed, dict) and "type" in parsed:
                return parsed
        except Exception:
            pass

        return {"type": "chat"}

    def detect_file_type(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["excel", "xlsx", "csv", "spreadsheet", "table", "sheet"]):
            return {"file_type": "xlsx"}
        if any(w in prompt_lower for w in ["word", "docx", "doc"]):
            return {"file_type": "docx"}
        if any(w in prompt_lower for w in ["pdf", "report"]):
            return {"file_type": "pdf"}

        instruction = f"""
        Classify which file format best fits the user's request:
        - pdf
        - docx
        - xlsx

        Return ONLY JSON:
        {{"file_type": "pdf"}} or {{"file_type": "docx"}} or {{"file_type": "xlsx"}}

        User Prompt:
        {prompt}
        """
        try:
            res = self.client.responses.create(
                model="gpt-4.1-mini",
                input=instruction
            )
            out = res.output_text.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(out)
            if isinstance(parsed, dict) and "file_type" in parsed:
                return parsed
        except Exception:
            pass

        return {"file_type": "pdf"}

    def generate_document_content(self, prompt: str) -> str:
        instruction = f"""
        Generate structured document text content based on the following request:
        {prompt}

        Format using tags:
        [TITLE] Main Title
        [HEADING] Section Heading
        [SUBHEADING] Subsection
        [BULLET] Bullet Point Item
        [TEXT] Regular paragraph text
        """
        try:
            res = self.client.responses.create(
                model="gpt-4.1-mini",
                input=instruction
            )
            return res.output_text.strip()
        except Exception:
            return f"[TITLE] Document\n[TEXT] Content for: {prompt}"

    def generate_excel_data(self, prompt: str) -> list:
        instruction = f"""
        Generate tabular JSON data for an Excel spreadsheet based on this request:
        {prompt}

        Return ONLY a JSON array of objects representing rows. Example:
        [
          {{"Solution Category": "Surveillance", "Features": "UAV 3D Mapping", "Use Cases": "Property Survey", "Notes": "High precision"}},
          {{"Solution Category": "Robotics", "Features": "3D Prototyping", "Use Cases": "New Inventions", "Notes": "R&D support"}}
        ]
        """
        try:
            res = self.client.responses.create(
                model="gpt-4.1-mini",
                input=instruction
            )
            out = res.output_text.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(out)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        return [{"Category": "General", "Details": prompt}]

    def generate_file_summary(self, prompt: str):
        instruction = f"Summarize the file generation request for prompt: {prompt}"
        try:
            res = self.client.responses.create(
                model="gpt-4.1-mini",
                input=instruction
            )
            return {
                "message": "File generated successfully.",
                "summary": res.output_text
            }
        except Exception:
            return {
                "message": "File generated successfully.",
                "summary": "Document created based on prompt."
            }