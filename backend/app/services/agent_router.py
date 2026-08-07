import json
import logging
from typing import Dict, Any, Optional
# pyrefly: ignore [missing-import]
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


TOOL_CLASSIFICATION_PROMPT = """You are an intelligent AI Agent Router. Your job is to analyze the user prompt and decide which tool to execute.

Available Tools:
1. "chat": General conversation, answering questions, writing text, math, coding, brainstorming, summarizing without specialized tools.
2. "web_search": Requests for latest real-time news, current events, live information, weather, stock prices, or searching the external internet.
3. "knowledge_base": Questions referencing "my documents", "knowledge base", "uploaded files", internal company guidelines, or document RAG retrieval.

Instructions:
Return ONLY a valid JSON object with the following structure (no markdown formatting, no code fences):
{
  "selected_tool": "<one of: chat, web_search, knowledge_base>",
  "reasoning": "<short 1-sentence explanation of why this tool was selected>",
  "display_name": "<Human readable tool name: e.g. Chat Assistant, Web Search, Knowledge Base>"
}
"""

TOOL_METADATA = {
    "chat": {"display_name": "💬 AI Chat Assistant", "icon": "Forum"},
    "web_search": {"display_name": "🌐 Web Search", "icon": "Language"},
    "knowledge_base": {"display_name": "📚 Knowledge Base RAG", "icon": "MenuBook"},
}


class AgentRouterService:
    """Service for classifying user prompt intent and selecting the appropriate AI tool."""

    def __init__(self):
        self.client: Optional[OpenAI] = None
        if getattr(settings, "OPENAI_API_KEY", None):
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client in AgentRouterService: {e}")

    def select_tool(self, prompt: str) -> Dict[str, Any]:
        """Analyzes prompt and returns selected_tool, reasoning, and display_name."""
        clean_prompt = prompt.strip().lower()

        # Fast rule-based heuristics for clear keyword triggers
        if any(kw in clean_prompt for kw in ["search web", "latest news", "search online", "current weather", "real-time info", "google search"]):
            return {
                "selected_tool": "web_search",
                "reasoning": "Detected real-time web search request.",
                "display_name": TOOL_METADATA["web_search"]["display_name"]
            }

        if any(kw in clean_prompt for kw in ["my docs", "my documents", "knowledge base", "uploaded files", "search kb", "rag", "company policy", "company documents", "company info", "company", "internal guidelines"]):
            return {
                "selected_tool": "knowledge_base",
                "reasoning": "Detected internal Knowledge Base retrieval query.",
                "display_name": TOOL_METADATA["knowledge_base"]["display_name"]
            }

        # Fallback to LLM Classification if client is available
        if self.client:
            try:
                res = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": TOOL_CLASSIFICATION_PROMPT},
                        {"role": "user", "content": f"User Prompt: {prompt}"}
                    ],
                    response_format={"type": "json_object"}
                )
                raw_output = res.choices[0].message.content

                clean_json = raw_output.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)
                selected = parsed.get("selected_tool", "chat").lower()

                if selected in TOOL_METADATA:
                    return {
                        "selected_tool": selected,
                        "reasoning": parsed.get("reasoning", "Selected via AI Intent Agent."),
                        "display_name": TOOL_METADATA[selected]["display_name"]
                    }
            except Exception as e:
                logger.error(f"LLM Tool classification failed: {e}")

        # Default fallback
        return {
            "selected_tool": "chat",
            "reasoning": "Defaulted to standard AI Chat Assistant.",
            "display_name": TOOL_METADATA["chat"]["display_name"]
        }
