import asyncio
import os
import json

from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException
from typing import List, Optional

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from src.managers.session_manager import SessionManager
from src.managers.firebase_chat_history_manager import FirebaseChatHistoryManager
from src.managers.vector_manager import VectorManager
from src.scrapers.reddit_scraper import extract_course_codes
from src.auth.firebase_token import verify_firebase_id_token, firebase_admin_ready
from src.models.chat_request_dto import ChatRequestDTO
from src.models.chat_response_dto import ChatResponseDTO
from src.services.prereq_graph import generate_remaining_path_image

router = APIRouter(prefix="/chat", tags=["chat", "Public"])

load_dotenv(dotenv_path=".env", override=True)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-3-flash-preview")


class GroundedChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """
    Custom wrapper to inject Gemini's native Google Search grounding
    without crashing LangGraph's ToolNode.
    """

    def bind_tools(self, tools, **kwargs):
        tools_list = list(tools)

        if ENABLE_REVERSE_SEARCH:
            tools_list.append({"google_search": {}})

        return super().bind_tools(tools_list, **kwargs)


@tool
def generate_course_prereqs_graph(completed_courses: Optional[List[str]] = None) -> str:
    """
    Generates a visual graph of the Computer Science course prerequisites.

    Args:
        completed_courses: A list of course codes the student has already finished,
                           extracted from their transcript or chat history.
                           Example: ["CMPSC 8", "CMPSC 16", "MATH 3A"]
    """

    try:
        image_url, message = generate_remaining_path_image(completed_courses)
    except FileNotFoundError:
        return "Error: Prerequisite data file is missing on the server."
    except Exception:
        return "Error: Failed to generate the prerequisite graph."

    if not image_url:
        return message

    return f"Here is the remaining prerequisite path based on your completed courses:\n\n![CMPSC Prerequisites Graph]({image_url})"


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_REVERSE_SEARCH = env_bool("ENABLE_REVERSE_SEARCH", False)
REDDIT_CLASS_NAMESPACE = os.getenv("REDDIT_CLASS_NAMESPACE", "reddit_class_data")
UCSB_CATALOG_NAMESPACE = os.getenv("UCSB_CATALOG_NAMESPACE", "catalog_class_data")


def to_text(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        text_chunks = []
        for item in x:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    text_chunks.append(text)
            elif isinstance(item, str):
                text_chunks.append(item)
        joined = "\n".join(chunk for chunk in text_chunks if chunk).strip()
        if joined:
            return joined
    return json.dumps(x, ensure_ascii=False)


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


def get_user_email_from_request(http_request: Request) -> str | None:
    auth_header = http_request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    decoded = verify_firebase_id_token(token)
    if not decoded:
        return None
    email = decoded.get("email")
    if isinstance(email, str):
        return email
    return None


@router.post("/response", response_model=ChatResponseDTO)
async def get_chat_response(request: ChatRequestDTO, http_request: Request):
    model_name = request.model_name or DEFAULT_GEMINI_MODEL

    try:
        # Initialize base LLM
        base_llm = GroundedChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
        )

        tools = [generate_course_prereqs_graph]

        agent_executor = create_agent(base_llm, tools)

        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
        firebase_history = FirebaseChatHistoryManager()

        user_text = request.message
        user_email = get_user_email_from_request(http_request)

        course_codes = extract_course_codes(user_text)
        inserted_docs = 0

        docs = vector_manager.std_search(user_text, k=4)
        reddit_docs = []
        catalog_docs = []

        if course_codes:
            try:
                loop = asyncio.get_event_loop()
                reddit_docs, catalog_docs = await asyncio.gather(
                    loop.run_in_executor(None, vector_manager.vector_store.similarity_search, user_text, 3, None,
                                         REDDIT_CLASS_NAMESPACE),
                    loop.run_in_executor(None, vector_manager.vector_store.similarity_search, user_text, 3, None,
                                         UCSB_CATALOG_NAMESPACE),
                )
            except Exception:
                reddit_docs = []
                catalog_docs = []

        context_sections = []
        if docs:
            context_sections.append(
                "PRIMARY RAG CONTEXT (RMP/UCSB DATA):\n" + "\n\n".join([d.page_content for d in docs]))
        if reddit_docs:
            context_sections.append("REDDIT CLASS CONTEXT:\n" + "\n\n".join([d.page_content for d in reddit_docs]))
        if catalog_docs:
            context_sections.append("UCSB CLASS ROSTER CONTEXT FOR CURRENT QUARTER: \n" + "\n\n".join(
                [d.page_content for d in catalog_docs]))
        context_text = "\n\n".join(context_sections)

        transcript_data = session_manager.load_transcript(str(request.chat_session_id))
        transcript_section = ""
        if transcript_data:
            transcript_section = f"\nSTUDENT TRANSCRIPT:\n{json.dumps(transcript_data, indent=2)}\n"

        system_prompt = SystemMessage(content=f"""
        You are GauchoGuider, an academic-focused UCSB advising assistant.

        RULES:
        1. Prioritize educational outcomes: course planning, prerequisites, degree progress, GPA strategy, study tactics, and graduation readiness.
        2. Use the student transcript (if provided) to personalize advice and avoid recommending courses the student already completed.
        3. Use the provided RAG context first. If Reddit class context is present, use it as supplemental student-sentiment evidence, not as official policy.
        4. If details are missing or uncertain, use reverse search to verify facts.
        5. Do NOT suggest hangout spots, nightlife, restaurants, or Santa Barbara activities unless the user explicitly asks for lifestyle recommendations.
        6. Keep answers practical and specific:
           - Recommend concrete next steps.
           - Call out constraints (prereqs, workload, sequence risk).
           - When useful, suggest checking official UCSB sources (department pages, catalog, GOLD) for final confirmation.
        7. If the user asks about unrelated non-UCSB topics, briefly redirect back to UCSB academics.
        8. Tone: concise, supportive, and direct. Avoid filler and slang unless the user asks for a casual style.{transcript_section}
        9. COURSE GRAPHS: If the user asks for a visual diagram or graph of course prerequisites, check if their transcript is available (either provided below or in previous chat history). 
           - IF YES: Call the generate_course_prereqs_graph tool and pass their completed courses into the tool so it removes them from the visual path.
           - IF NO: Do not call the tool. Politely ask them to upload their transcript or list their completed courses first so you can generate an accurate map.
        """.strip())

        rag_prompt = f"""
        CONTEXT FROM RMP REVIEWS:
        {context_text}

        USER QUESTION:
        {user_text}

        REDDIT INGEST INFO:
        - class_codes_detected: {course_codes}
        - new_reddit_docs_inserted_this_request: {inserted_docs}
        """.strip()

        history_raw = session_manager.load_history(str(request.chat_session_id))
        history_msgs = history_to_messages(history_raw)

        messages = [system_prompt] + history_msgs + [HumanMessage(content=rag_prompt)]

        response_state = await agent_executor.ainvoke({"messages": messages})

        final_message = response_state["messages"][-1].content

        chat_session_id = str(request.chat_session_id)
        user_text_saved = to_text(user_text)
        ai_text_saved = to_text(final_message)

        session_manager.save_message(chat_session_id, "human", user_text_saved)
        session_manager.save_message(chat_session_id, "ai", ai_text_saved)

        if user_email:
            firebase_history.save_message(user_email, chat_session_id, "human", user_text_saved)
            firebase_history.save_message(user_email, chat_session_id, "ai", ai_text_saved)

        return ChatResponseDTO(
            response=final_message,
            model_name=model_name,
        )

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return ChatResponseDTO(
            response="Sorry, I'm having trouble accessing my database right now.",
            model_name=model_name,
        )


@router.get("/sessions")
async def list_chat_sessions(http_request: Request):
    if not firebase_admin_ready():
        raise HTTPException(
            status_code=503,
            detail="Backend Firebase Admin is not configured. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH.",
        )
    user_email = get_user_email_from_request(http_request)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    firebase_history = FirebaseChatHistoryManager()
    sessions = firebase_history.list_sessions(user_email)
    return {"sessions": sessions}


@router.get("/sessions/{chat_session_id}")
async def get_chat_session_messages(chat_session_id: str, http_request: Request):
    if not firebase_admin_ready():
        raise HTTPException(
            status_code=503,
            detail="Backend Firebase Admin is not configured. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH.",
        )
    user_email = get_user_email_from_request(http_request)
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    firebase_history = FirebaseChatHistoryManager()
    messages = firebase_history.get_messages(user_email, chat_session_id)
    return {"chat_session_id": chat_session_id, "messages": messages}
