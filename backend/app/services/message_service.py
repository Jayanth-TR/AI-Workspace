from fastapi import HTTPException

# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate
from app.services.llm_service import LLMService
from app.services.file_service import FileService
from app.services.web_search_service import WebSearchService
from app.services.rag_service import RAGService
from app.services.agent_router import AgentRouterService


llm_service = LLMService()
file_service = FileService()
web_search_service = WebSearchService()
rag_service = RAGService()
agent_router = AgentRouterService()


class MessageService:
    """Service acting as an autonomous router for incoming chat requests based on mode or AI Agent tool selection."""

    def _route_request(
        self,
        db: Session,
        chat: Chat,
        prompt_text: str,
        mode: str,
        current_user: User
    ):
        """Route request to the designated service based on selected mode or AI Agent tool decision.
        
        Supported modes:
        - auto / agent: AI Agent dynamically chooses tool (chat, web_search, knowledge_base)
        - chat: AI Chat flow via LLMService
        - web_search: Web Search flow via WebSearchService
        - rag / knowledge_base: Knowledge Base flow via RAGService
        """
        selected_mode = (mode or "auto").strip().lower()
        agent_decision = None

        # 1. Autonomous AI Agent Router Step
        if selected_mode in ["auto", "agent", "default", ""]:
            agent_decision = agent_router.select_tool(prompt_text)
            tool = agent_decision["selected_tool"]
        else:
            tool = selected_mode
            if tool == "rag":
                tool = "knowledge_base"

        logger_prefix = f"🤖 [AI Agent Routing] Selected Tool: {tool}"
        print(logger_prefix)

        # 2. Tool Execution Switchboard
        
        # Tool: Web Search
        if tool == "web_search":
            response_content = web_search_service.process_query(prompt_text)
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "chat",
                "mode": "web_search",
                "response": response_content,
                "agent_decision": agent_decision or {"selected_tool": "web_search", "display_name": "🌐 Web Search", "reasoning": "Executed Web Search Tool"}
            }

        # Tool: Knowledge Base (RAG)
        if tool in ["knowledge_base", "rag"]:
            response_content = rag_service.process_query(query=prompt_text, db=db, current_user=current_user)
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "chat",
                "mode": "knowledge_base",
                "response": response_content,
                "agent_decision": agent_decision or {"selected_tool": "knowledge_base", "display_name": "📚 Knowledge Base RAG", "reasoning": "Executed Knowledge Base RAG Tool"}
            }

        # Tool: Invoice Generator
        if tool == "invoice":
            file_result = file_service.generate_invoice_doc(prompt_text)
            response_content = (
                f"📄 **Invoice Generated Successfully!**\n\n"
                f"Your professional Invoice document has been created.\n"
                f"sandbox:/{file_result['filename']}"
            )
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "file",
                "mode": "invoice",
                "response": response_content,
                "file": file_result,
                "agent_decision": agent_decision or {"selected_tool": "invoice", "display_name": "📄 Invoice Generator", "reasoning": "Generated Invoice Document"}
            }

        # Tool: Expense Sheet Generator
        if tool == "expense_sheet":
            file_result = file_service.generate_expense_sheet_doc(prompt_text)
            response_content = (
                f"📊 **Expense Sheet Generated Successfully!**\n\n"
                f"Your itemized Expense Tracker spreadsheet (.xlsx) has been generated.\n"
                f"sandbox:/{file_result['filename']}"
            )
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "file",
                "mode": "expense_sheet",
                "response": response_content,
                "file": file_result,
                "agent_decision": agent_decision or {"selected_tool": "expense_sheet", "display_name": "📊 Expense Sheet Generator", "reasoning": "Generated Expense Tracker Spreadsheet"}
            }

        # Tool: Estimate Generator
        if tool == "estimate":
            from app.services.estimate_service import EstimateService
            from app.schemas.estimate import EstimateGenerateRequest
            est_service = EstimateService()
            req = EstimateGenerateRequest(prompt=prompt_text)
            estimate_data = est_service.generate_estimate_data(req, db=db, current_user=current_user)
            file_result = file_service.create_estimate_pdf(estimate_data)
            
            response_content = (
                f"📝 **Estimate Generated Successfully!**\n\n"
                f"Your professional Estimate document has been created.\n"
                f"sandbox:/{file_result['filename']}"
            )
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "file",
                "mode": "estimate",
                "response": response_content,
                "file": file_result,
                "agent_decision": agent_decision or {"selected_tool": "estimate", "display_name": "📝 Estimate Generator", "reasoning": "Generated Estimate Document"}
            }


        # Tool: Standard Chat Assistant (or file fallback check)
        request_type = llm_service.detect_request_type(prompt_text)
        if request_type["type"] == "file":
            file_result = file_service.process_prompt(prompt_text)
            summary = llm_service.generate_file_summary(prompt_text)
            response_content = f"{summary['message']}\nsandbox:/{file_result['filename']}"
            assistant_message = Message(chat_id=chat.id, role="assistant", content=response_content)
            db.add(assistant_message)
            db.commit()
            return {
                "type": "file",
                "mode": "chat",
                "response": response_content,
                "summary": summary["summary"],
                "file": file_result,
                "agent_decision": agent_decision or {"selected_tool": "chat", "display_name": "💬 AI Chat Assistant", "reasoning": "Executed Document Generation in Chat"}
            }

        # Conversational Chat via LLM
        statement = (
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(Message.created_at.asc())
        )
        messages = db.execute(statement).scalars().all()
        conversation = [{"role": msg.role, "content": msg.content} for msg in messages]

        ai_response = llm_service.generate_response(conversation)
        assistant_message = Message(chat_id=chat.id, role="assistant", content=ai_response)
        db.add(assistant_message)
        db.commit()

        return {
            "type": "chat",
            "mode": "chat",
            "response": ai_response,
            "agent_decision": agent_decision or {"selected_tool": "chat", "display_name": "💬 AI Chat Assistant", "reasoning": "Executed AI Chat Assistant"}
        }

    def send_message(
        self,
        db: Session,
        chat_id: int,
        message_data: MessageCreate,
        current_user: User
    ):
        prompt_text = message_data.text

        # 1. Find chat
        chat = db.get(Chat, chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

        # 2. Check ownership
        if chat.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You cannot access this chat")

        # 3. Save user message
        user_message = Message(chat_id=chat.id, role="user", content=prompt_text)
        db.add(user_message)
        db.commit()

        # 4. Route request based on mode
        return self._route_request(
            db=db,
            chat=chat,
            prompt_text=prompt_text,
            mode=message_data.mode,
            current_user=current_user
        )

    def start_chat(
        self,
        db: Session,
        message_data: MessageCreate,
        current_user: User
    ):
        prompt_text = message_data.text

        # 1. Create chat
        chat = Chat(title=prompt_text[:50] or "New Chat", user_id=current_user.id)
        db.add(chat)
        db.commit()
        db.refresh(chat)

        # 2. Save user message
        user_message = Message(chat_id=chat.id, role="user", content=prompt_text)
        db.add(user_message)
        db.commit()

        # 3. Route request based on mode
        result = self._route_request(
            db=db,
            chat=chat,
            prompt_text=prompt_text,
            mode=message_data.mode,
            current_user=current_user
        )
        result["chat_id"] = chat.id
        return result

    def get_messages(
        self,
        db: Session,
        chat_id: int,
        current_user: User
    ):
        chat = db.get(Chat, chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        if chat.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You cannot access this chat")

        statement = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        return db.execute(statement).scalars().all()