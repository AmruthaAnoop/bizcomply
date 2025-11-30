"""Chat endpoint for BizComply AI (v1).

This endpoint exposes `/chat` for the Streamlit UI.  It:
1. Accepts a chat request with a conversation_id (optional) and user query.
2. Retrieves/creates a Conversation in the database.
3. Loads the saved BusinessProfile from the ComplianceEngine (SQLite).
4. Builds a prompt = system prompt + business profile + last 10 messages + user query.
5. Calls `LLMProvider.get_llm().invoke(prompt)`.
6. Saves messages to the database and returns JSON with answer + conversation_id.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from models.llm import LLMProvider
from models.compliance_engine import ComplianceEngine
from models.chat import ChatRepository, Message, Conversation
import uuid

router = APIRouter()
chat_repo = ChatRepository()
compliance_engine = ComplianceEngine()

SYSTEM_PROMPT = (
    "You are BizComply AI, an expert compliance assistant. "
    "Always tailor answers using the supplied business profile and jurisdiction. "
    "If information is missing, ask a concise follow-up question."
)

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    query: str
    mode: str = "concise"  # or "detailed"
    business_id: Optional[str] = None  # Add business_id to associate with a business

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    timestamp: float

# Helper to build conversation history
def _get_conversation_history(conversation_id: str) -> str:
    """Get formatted conversation history from the database."""
    messages = chat_repo.get_messages(conversation_id, limit=10)  # Get last 10 messages
    history = []
    for msg in messages:
        sender = "User" if msg['sender_type'] == 'user' else 'Assistant'
        history.append(f"{sender}: {msg['content']}")
    return "\n".join(history)

# Helper to build prompt
def _build_prompt(conversation_id: str, business_profile: Optional[Dict[str, Any]], user_query: str) -> str:
    """Build the prompt for the LLM."""
    profile_block = ""
    if business_profile:
        profile_block = (
            f"Business Name: {business_profile.get('name', 'Not specified')}\n"
            f"Business Type: {business_profile.get('business_type', 'Not specified')}\n"
            f"Jurisdiction: {business_profile.get('jurisdiction', 'Not specified')}\n"
            f"Registration Number: {business_profile.get('registration_number', 'Not specified')}\n"
        )

    history = _get_conversation_history(conversation_id)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"BUSINESS PROFILE:\n{profile_block}\n"
        f"CONVERSATION HISTORY:\n{history}\n"
        f"User: {user_query}\nAssistant:"
    )
    return prompt

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(req: ChatRequest):
    """Handle chat requests with conversation persistence."""
    # Get or create conversation
    if req.conversation_id:
        conversation = chat_repo.get_conversation(req.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create a new conversation
        conversation = Conversation(
            business_id=req.business_id,
            title=f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        chat_repo.create_conversation(conversation)
        req.conversation_id = conversation.id
    
    # Add user message to database
    user_message = Message(
        conversation_id=req.conversation_id,
        sender_type="user",
        content=req.query
    )
    chat_repo.add_message(user_message)

    # Load business profile (first one found for now, or use the one from request)
    business_profile = None
    if req.business_id:
        profile = compliance_engine.get_business_profile(req.business_id)
        if profile:
            business_profile = profile.to_dict()
    else:
        business_profiles = compliance_engine.list_business_profiles()
        if business_profiles:
            business_profile = business_profiles[0].to_dict()

    # Build prompt and get response from LLM
    try:
        prompt = _build_prompt(req.conversation_id, business_profile, req.query)
        llm = LLMProvider.get_llm()
        answer = llm.invoke(prompt)
        if not isinstance(answer, str) and hasattr(answer, "content"):
            answer = answer.content
    except Exception as e:
        # Provide a helpful fallback response when LLM is not available
        answer = (
            "I'm currently unable to connect to the language model. "
            "Here's some general guidance for your question:\n\n"
            f"Regarding: {req.query}\n\n"
            "For specific compliance advice, please:\n"
            "1. Consult with a legal professional\n"
            "2. Check relevant regulatory websites\n"
            "3. Review industry-specific compliance guidelines\n\n"
            f"Technical error: {str(e)[:100]}..."
        )

    # Add assistant message to database
    assistant_message = Message(
        conversation_id=req.conversation_id,
        sender_type="assistant",
        content=answer
    )
    chat_repo.add_message(assistant_message)

    # Update conversation title if it's the first message
    messages = chat_repo.get_messages(req.conversation_id, limit=1)
    if len(messages) == 2:  # User message + assistant response
        first_message = messages[0]['content'][:50]  # First 50 chars of first message
        chat_repo.update_conversation(
            req.conversation_id,
            {"title": first_message + ("..." if len(first_message) == 50 else "")}
        )

    return ChatResponse(
        conversation_id=req.conversation_id,
        answer=answer,
        timestamp=datetime.utcnow().timestamp(),
    )
