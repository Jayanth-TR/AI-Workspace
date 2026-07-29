import logging
import os
import json
from typing import Optional, List, Dict, Any
from tavily import TavilyClient
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an AI search assistant.

Using the web search results, generate a structured JSON response.

Return ONLY valid JSON in the following format:

{
  "title": "",
  "summary": "",
  "keyFacts": [
    {
      "label": "",
      "value": ""
    }
  ],
  "details": "",
  "sources": [
    {
      "title": "",
      "url": ""
    }
  ]
}

Rules:
- Keep the summary under 120 words.
- Extract 3–6 key facts when applicable.
- Include all source URLs.
- Do not return Markdown.
- Do not wrap the JSON in code fences.
"""


class WebSearchService:
    """Service for performing web searches via Tavily API and generating structured JSON responses using OpenAI."""

    def __init__(self, tavily_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key or getattr(settings, "TAVILY_API_KEY", "") or os.environ.get("TAVILY_API_KEY", "")
        self.openai_api_key = openai_api_key or getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
        
        self.tavily_client: Optional[TavilyClient] = None
        if self._is_valid_key(self.tavily_api_key):
            try:
                self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize TavilyClient: {e}")

        self.openai_client: Optional[OpenAI] = None
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key or key.strip() == "" or "YOUR_TAVILY_API_KEY" in key or key.startswith("tvly-YOUR_"):
            return False
        return True

    def process_query(self, query: str) -> str:
        """Process web search query and return raw structured JSON as required."""
        clean_query = query.strip() if query else ""
        if not clean_query:
            return json.dumps({
                "title": "Invalid Query",
                "summary": "Please provide a valid query to search the web.",
                "keyFacts": [],
                "details": "",
                "sources": []
            })

        # Check API key configuration
        if not self._is_valid_key(self.tavily_api_key) or not self.tavily_client:
            logger.warning("WebSearchService invoked without a valid Tavily API key.")
            return json.dumps({
                "title": "Web Search Unavailable",
                "summary": "Tavily API key is missing or invalid. Please configure TAVILY_API_KEY in backend/.env.",
                "keyFacts": [],
                "details": "",
                "sources": []
            })

        # Execute Web Search via Tavily
        search_results: List[Dict[str, Any]] = []
        try:
            response = self.tavily_client.search(
                query=clean_query,
                search_depth="basic",
                max_results=5,
                include_answer=False
            )
            search_results = response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily Search API request failed for query '{clean_query}': {e}", exc_info=True)
            return json.dumps({
                "title": "Search Error",
                "summary": f"Unable to fetch search results from Tavily API: {str(e)}",
                "keyFacts": [],
                "details": "",
                "sources": []
            })

        if not search_results:
            return json.dumps({
                "title": "No Results Found",
                "summary": f"No relevant web search results found for query: '{clean_query}'.",
                "keyFacts": [],
                "details": "",
                "sources": []
            })

        # Format Search Results
        context_snippets: List[str] = []
        sources: List[Dict[str, str]] = []

        for idx, result in enumerate(search_results[:5], 1):
            title = result.get("title", f"Source {idx}")
            url = result.get("url", "")
            content = result.get("content", "")
            
            context_snippets.append(f"Source [{idx}]: {title}\nURL: {url}\nContent: {content}")
            if url:
                sources.append({"title": title, "url": url})

        formatted_context = "\n\n".join(context_snippets)

        # Synthesize Structured JSON using OpenAI
        if not self.openai_client:
            return json.dumps({
                "title": f"Search Results for: {clean_query}",
                "summary": "Search results retrieved, but OpenAI client is unavailable for synthesis.",
                "keyFacts": [],
                "details": formatted_context[:500],
                "sources": sources
            })

        try:
            user_prompt = f"User Query: {clean_query}\n\nWeb Search Results:\n{formatted_context}"

            try:
                ai_res = self.openai_client.responses.create(
                    model="gpt-4.1-mini",
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                raw_json = getattr(ai_res, "output_text", None) or str(ai_res)
            except Exception:
                ai_res = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                raw_json = ai_res.choices[0].message.content

            clean_json = raw_json.strip()
            # Remove any accidental markdown wrapping if present
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            
            return clean_json.strip()

        except Exception as e:
            logger.error(f"OpenAI synthesis failed for query '{clean_query}': {e}", exc_info=True)
            return json.dumps({
                "title": f"Search Results for: {clean_query}",
                "summary": f"Retrieved web search results, but failed to format JSON via LLM: {str(e)}",
                "keyFacts": [],
                "details": formatted_context[:500],
                "sources": sources
            })
