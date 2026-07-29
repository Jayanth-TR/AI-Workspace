import json
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(self):
        self.client = None
        if getattr(settings, "OPENAI_API_KEY", None):
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client in LLMService: {e}")

    def generate_response(self, conversation: list) -> str:
        if not self.client or not getattr(settings, "OPENAI_API_KEY", None):
            return "OpenAI API key is missing. Please configure OPENAI_API_KEY in your environment variables."

        formatted_messages = []
        for msg in conversation:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            elif hasattr(msg, "role") and hasattr(msg, "content"):
                formatted_messages.append({"role": getattr(msg, "role"), "content": getattr(msg, "content")})

        if not formatted_messages:
            formatted_messages = [{"role": "user", "content": "Hello"}]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=formatted_messages
            )
            return response.choices[0].message.content or "No response returned from model."
        except Exception as e:
            logger.error(f"OpenAI API call in generate_response failed: {e}")
            return f"I experienced an issue processing your request: {e}"

    def detect_request_type(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        file_action_keywords = [
            "generate file", "create file", "download file", "make a file",
            "generate pdf", "create pdf", "download pdf", "make a pdf", "export pdf",
            "generate docx", "create docx", "generate word", "create word",
            "generate excel", "create excel", "generate xlsx", "export to excel",
            "create spreadsheet", "export excel", "export docx"
        ]

        if any(keyword in prompt_lower for keyword in file_action_keywords):
            return {"type": "file"}

        if not self.client:
            return {"type": "chat"}

        instruction = f"""
        Determine whether the user is explicitly requesting to CREATE or GENERATE a new downloadable document/file (such as creating a new PDF, Word, or Excel file), OR simply asking a question/having a conversation.

        Return ONLY JSON:
        {{"type": "file"}} if they want to generate/create a downloadable file.
        {{"type": "chat"}} if they are asking a question, analyzing data, or having a chat.

        User Request:
        {prompt}
        """

        try:
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}],
                response_format={"type": "json_object"}
            )
            output = res.choices[0].message.content.strip()
            parsed = json.loads(output)
            if isinstance(parsed, dict) and "type" in parsed:
                return parsed
        except Exception as e:
            logger.warning(f"detect_request_type LLM call failed: {e}")

        return {"type": "chat"}

    def detect_file_type(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["excel", "xlsx", "csv", "spreadsheet", "table", "sheet"]):
            return {"file_type": "xlsx"}
        if any(w in prompt_lower for w in ["word", "docx", "doc"]):
            return {"file_type": "docx"}
        if any(w in prompt_lower for w in ["pdf", "report"]):
            return {"file_type": "pdf"}

        if not self.client:
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
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}],
                response_format={"type": "json_object"}
            )
            out = res.choices[0].message.content.strip()
            parsed = json.loads(out)
            if isinstance(parsed, dict) and "file_type" in parsed:
                return parsed
        except Exception as e:
            logger.warning(f"detect_file_type LLM call failed: {e}")

        return {"file_type": "pdf"}

    def generate_document_content(self, prompt: str) -> str:
        if not self.client:
            return f"[TITLE] Generated Document\n[TEXT] Content generated for: {prompt}"

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
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"generate_document_content LLM call failed: {e}")
            return f"[TITLE] Document\n[TEXT] Content for: {prompt}"

    def generate_excel_data(self, prompt: str) -> list:
        if not self.client:
            return [{"Category": "General", "Details": prompt}]

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
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}],
                response_format={"type": "json_object"}
            )
            out = res.choices[0].message.content.strip()
            parsed = json.loads(out)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
        except Exception as e:
            logger.error(f"generate_excel_data LLM call failed: {e}")

        return [{"Category": "General", "Details": prompt}]

    def generate_file_summary(self, prompt: str) -> dict:
        if not self.client:
            return {
                "message": "File generated successfully.",
                "summary": "Document created based on prompt."
            }

        instruction = f"Summarize the file generation request for prompt: {prompt}"
        try:
            res = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": instruction}]
            )
            return {
                "message": "File generated successfully.",
                "summary": res.choices[0].message.content.strip()
            }
        except Exception as e:
            logger.error(f"generate_file_summary LLM call failed: {e}")
            return {
                "message": "File generated successfully.",
                "summary": "Document created based on prompt."
            }