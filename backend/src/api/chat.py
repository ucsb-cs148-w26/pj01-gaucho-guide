import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from src.managers.session_manager import SessionManager
from src.managers.firebase_chat_history_manager import FirebaseChatHistoryManager
from src.managers.vector_manager import VectorManager
from src.scrapers.reddit_scraper import extract_course_codes
from src.auth.firebase_token import verify_firebase_id_token, firebase_admin_ready
from src.models.chat_request_dto import ChatRequestDTO
from src.models.chat_response_dto import ChatResponseDTO
from src.agents.mermaid_agent import generate_mermaid_diagram
from src.agents.mermaid_agent import GauchoState
import json

router = APIRouter(prefix="/chat", tags=["chat", "Public"])

load_dotenv(dotenv_path=".env", override=True)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-3-flash-preview")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_REVERSE_SEARCH = env_bool("ENABLE_REVERSE_SEARCH", False)
REDDIT_CLASS_NAMESPACE = os.getenv("REDDIT_CLASS_NAMESPACE", "reddit_class_data")


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
        base_llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
        )
        llm = base_llm

        local_tools = [generate_mermaid_diagram]
        model_tools = [generate_mermaid_diagram]

        if ENABLE_REVERSE_SEARCH:
            # Add Gemini's native search grounding ONLY to the model_tools
            model_tools.append({"google_search": {}})

        llm_with_tools = llm.bind_tools(model_tools)

        async def call_model(state: MessagesState):
            resp = await llm_with_tools.ainvoke(state["messages"])
            return {"messages": [resp]}

        workflow = StateGraph(MessagesState)

        workflow.add_node("agent", call_model)
        # FIX 1 (cont): Only pass the local Python tools to the ToolNode!
        workflow.add_node("tools", ToolNode(local_tools))

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")

        gaucho_guide = workflow.compile()

        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
        firebase_history = FirebaseChatHistoryManager()

        user_text = request.message
        user_email = get_user_email_from_request(http_request)

        course_codes = extract_course_codes(user_text)
        inserted_docs = 0

        docs = vector_manager.std_search(user_text, k=4)
        reddit_docs = []
        if course_codes:
            try:
                reddit_docs = vector_manager.vector_store.similarity_search(
                    query=user_text,
                    k=3,
                    namespace=REDDIT_CLASS_NAMESPACE,
                )
            except Exception:
                reddit_docs = []

        context_sections = []
        if docs:
            context_sections.append(
                "PRIMARY RAG CONTEXT (RMP/UCSB DATA):\n" + "\n\n".join([d.page_content for d in docs])
            )
        if reddit_docs:
            context_sections.append(
                "REDDIT CLASS CONTEXT:\n" + "\n\n".join([d.page_content for d in reddit_docs])
            )
        context_text = "\n\n".join(context_sections)

        transcript_data = session_manager.load_transcript(str(request.chat_session_id))
        transcript_section = ""
        if transcript_data:
            transcript_section = f"""

STUDENT TRANSCRIPT (use this to personalize recommendations — do NOT recommend courses the student has already passed):
{json.dumps(transcript_data, indent=2)}
"""

        system_prompt = SystemMessage(content=f"""
You are GauchoGuider, an academic-focused UCSB advising assistant.
# ... [rest of your prompt] ...
8. Tone: concise, supportive, and direct. Avoid filler and slang unless the user asks for a casual style.{transcript_section}
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

        final_state = await gaucho_guide.ainvoke({"messages": messages})

        final_response_content = final_state["messages"][-1].content

        chat_session_id = str(request.chat_session_id)
        user_text_saved = to_text(user_text)
        ai_text_saved = to_text(final_response_content)
        session_manager.save_message(chat_session_id, "human", user_text_saved)
        session_manager.save_message(chat_session_id, "ai", ai_text_saved)

        if user_email:
            firebase_history.save_message(user_email, chat_session_id, "human", user_text_saved)
            firebase_history.save_message(user_email, chat_session_id, "ai", ai_text_saved)

        return ChatResponseDTO(
            response=final_response_content,  # Return the extracted text
            model_name=model_name,
        )

    except Exception as e:
        print(f"Error processing chat request: {e}")
        return ChatResponseDTO(
            response="Sorry, I'm having trouble accessing my brain (database) right now.",
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
