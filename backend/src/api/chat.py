import os
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.managers.session_manager import SessionManager
from src.managers.vector_manager import VectorManager
from src.models.chat_request_dto import ChatRequestDTO
from langchain_core.output_parsers import StrOutputParser
from src.models.chat_response_dto import ChatResponseDTO
import json


router = APIRouter(prefix="/chat", tags=["chat", "Public"])

load_dotenv(dotenv_path=".env", override=True)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-3-flash-preview")

def to_text(x):
    return x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)

def history_to_messages(history):
    if not history:
        return []
    out = []
    for item in history:
        if isinstance(item, (HumanMessage, AIMessage, SystemMessage)):
            out.append(item)
            continue
        if isinstance(item, tuple) and len(item) >= 2:
            role, content = item[0], item[1]
        elif isinstance(item, dict):
            role, content = item.get("role"), item.get("content")
        else:
            continue
        if role in ("human", "user"):
            out.append(HumanMessage(content=str(content)))
        else:
            out.append(AIMessage(content=str(content)))
    return out


@router.post("/response", response_model=ChatResponseDTO)
async def get_chat_response(request: ChatRequestDTO):
    model_name = request.model_name or DEFAULT_GEMINI_MODEL

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
        )

        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()

        user_text = request.message

        docs = vector_manager.std_search(user_text, k=4)
        context_text = "\n\n".join([d.page_content for d in docs])

        transcript_data = session_manager.load_transcript(str(request.chat_session_id))
        transcript_section = ""
        if transcript_data:
            transcript_section = f"""

STUDENT TRANSCRIPT (use this to personalize recommendations — do NOT recommend courses the student has already passed):
{json.dumps(transcript_data, indent=2)}
"""

        system_prompt = SystemMessage(content=f"""
You are GauchoGuider. A guide for ucsb students navigating through college life.

RULES:
1. STRICTLY talk about UCSB, Isla Vista, or college life at Santa Barbara.
2. If the user asks about unrelated topics (like generic coding, world news, or other universities),
politely steer them back to UCSB or say you only know about UCSB.
3. Use the provided Context (reviews and stats) to answer questions accurately.
4. When mentioning names, always use the provided Context and the Context only. You can utilize reverse search to gain required info to answer, however.
5. Be casual, use slang like "IV" (Isla Vista), "The Loop", "Arroyo", etc., if appropriate.
6. If a student transcript is provided, use it to give personalized course recommendations.{transcript_section}
""".strip())

        rag_prompt = f"""
CONTEXT FROM RMP REVIEWS:
{context_text}

USER QUESTION:
{user_text}
""".strip()

        history_raw = session_manager.load_history(str(request.chat_session_id))
        history_msgs = history_to_messages(history_raw)

        messages = [system_prompt] + history_msgs + [HumanMessage(content=rag_prompt)]

        
        response = await llm.ainvoke(messages)

        session_manager.save_message(str(request.chat_session_id), "human", to_text(user_text))
        session_manager.save_message(str(request.chat_session_id), "ai", to_text(response.content))

        return ChatResponseDTO(
            response=response.content,
            model_name=model_name,
        )

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return ChatResponseDTO(
            response="Sorry, I'm having trouble accessing my brain (database) right now.",
            model_name=model_name,
        )