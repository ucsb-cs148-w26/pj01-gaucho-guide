import asyncio
import base64
import os
import json
import random
from collections import defaultdict

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
from src.services.transcript_advisor import build_transcript_advising_context

from src.services.prereq_graph import normalize_course_code, _clean_prereq_label

from src.services.prereq_graph import DATA_PATH

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
def generate_future_route_graph(current_courses: List[str]) -> str:
    """
    Generates a visual graph of possible future course routes based on a list of current CMPSC courses.

    Args:
        current_courses: A list of current course codes (e.g., ["CMPSC 8", "MATH 3A", "PSTAT 120A"]).
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Error: Prerequisite data file is missing on the server."

    postreqs = defaultdict(list)
    for course, details in data.items():
        course_norm = normalize_course_code(course)

        if not course_norm.startswith("CMPSC"):
            continue

        for prereq in details.get("prereq_courses", []):
            if not isinstance(prereq, str):
                continue
            clean_prereq = normalize_course_code(_clean_prereq_label(prereq))

            if clean_prereq.startswith("CMPSC"):
                postreqs[clean_prereq].append(course_norm)

    valid_courses = [
        normalize_course_code(c) for c in current_courses
        if normalize_course_code(c).startswith("CMPSC")
    ]

    if not valid_courses:
        return "No valid CMPSC courses were found in your current list to generate a future route."

    generated_urls = []

    for start_course in valid_courses:
        edges = set()
        queue = [(start_course, 0)]
        visited = {start_course: 0}

        while queue:
            current, depth = queue.pop(0)

            if depth < 4:
                for nxt in postreqs.get(current, []):
                    edges.add((current, nxt))
                    if nxt not in visited or visited[nxt] > depth + 1:
                        visited[nxt] = depth + 1
                        queue.append((nxt, depth + 1))

        mermaid_markup = ["graph TD"]

        for src, dst in edges:
            mermaid_markup.append(f'    {_node_id(src)}["{src}"] --> {_node_id(dst)}["{dst}"]')

        if not edges:
            mermaid_markup.append(f'    {_node_id(start_course)}["{start_course}"]')

        markup_str = "\n".join(mermaid_markup)
        encoded = base64.urlsafe_b64encode(markup_str.encode("utf-8")).decode("ascii")
        generated_urls.append(f"https://mermaid.ink/img/{encoded}")

    selected_url = random.choice(generated_urls)

    return f"Here is a possible future route you could take based on your current coursework:\n\n![Future Route Graph]({selected_url})"


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


ENABLE_REVERSE_SEARCH = env_bool("ENABLE_REVERSE_SEARCH", False)
REDDIT_CLASS_NAMESPACE = os.getenv("REDDIT_CLASS_NAMESPACE", "reddit_class_data")
UCSB_CATALOG_NAMESPACE = os.getenv("UCSB_CATALOG_NAMESPACE", "catalog_class_data")
TRANSCRIPT_DETERMINISTIC_ADVICE = env_bool("TRANSCRIPT_DETERMINISTIC_ADVICE", True)


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


def _is_transcript_planning_query(user_text: str) -> bool:
    q = user_text.lower()
    key_phrases = [
        "based on my transcript",
        "what can i take",
        "what should i take",
        "what classes can i take",
        "what courses can i take",
        "what courses should i take",
        "next classes",
        "next courses",
        "courses ive taken",
        "courses i've taken",
        "analyze my transcript",
        "analyze my courses",
        "course plan",
        "degree progress",
    ]
    return any(p in q for p in key_phrases)


def _list_preview(items: list[str], limit: int = 12) -> str:
    if not items:
        return "None"
    preview = items[:limit]
    suffix = f" (+{len(items) - limit} more)" if len(items) > limit else ""
    return ", ".join(preview) + suffix


def _build_transcript_constraint_block(transcript_context: dict) -> str:
    completed = transcript_context.get("completed_courses", [])
    in_progress = transcript_context.get("in_progress_courses", [])
    eligible = transcript_context.get("eligible_next_courses", [])
    not_passed = transcript_context.get("not_passed_courses", [])
    gpa = transcript_context.get("cumulative_gpa")
    major = transcript_context.get("major")
    parser_strategy = transcript_context.get("parser_strategy_used")

    return (
        "TRANSCRIPT DERIVED FACTS (deterministic, highest priority):\n"
        f"- Major: {major}\n"
        f"- Cumulative GPA: {gpa}\n"
        f"- Parser strategy used: {parser_strategy}\n"
        f"- Completed courses: {_list_preview(completed)}\n"
        f"- In-progress/planned courses: {_list_preview(in_progress)}\n"
        f"- Not-passed courses: {_list_preview(not_passed)}\n"
        f"- Eligible next courses (based on completed prereqs): {_list_preview(eligible)}\n"
        "HARD CONSTRAINTS:\n"
        "1) Never claim an in-progress/planned course is completed.\n"
        "2) Never recommend a completed course as a next course.\n"
        "3) Never recommend an in-progress/planned course as a new next course.\n"
        "4) For recommendations, prioritize courses from the eligible-next list above.\n"
        "5) When stating GPA or progress, use the deterministic transcript facts above."
    )


def _build_deterministic_transcript_advice(transcript_context: dict) -> str:
    major = transcript_context.get("major") or "Unknown"
    gpa = transcript_context.get("cumulative_gpa")
    completed_cs = transcript_context.get("completed_cs_courses", [])
    in_progress_cs = transcript_context.get("in_progress_cs_courses", [])
    eligible_cs = transcript_context.get("eligible_next_cs_courses", [])
    parser_strategy = transcript_context.get("parser_strategy_used")

    gpa_text = f"{gpa:.2f}" if isinstance(gpa, (int, float)) else "Unavailable"
    completed_text = _list_preview(completed_cs, limit=14)
    progress_text = _list_preview(in_progress_cs, limit=10)
    eligible_text = _list_preview(eligible_cs, limit=12)

    return (
        "**Transcript-Based CS Plan**\n"
        f"- Major: {major}\n"
        f"- Cumulative GPA: {gpa_text}\n"
        f"- Completed CMPSC: {completed_text}\n"
        f"- In progress/planned CMPSC: {progress_text}\n"
        f"- Recommended next CMPSC (eligible now): {eligible_text}\n\n"
        "**How this was generated**\n"
        "- Recommendations are constrained by your parsed transcript and prerequisite rules.\n"
        "- Completed or currently in-progress courses are excluded from new-course recommendations.\n"
        f"- Parser strategy used: {parser_strategy}."
    )


@router.post("/response", response_model=ChatResponseDTO)
async def get_chat_response(request: ChatRequestDTO, http_request: Request):
    model_name = request.model_name or DEFAULT_GEMINI_MODEL

    try:
        # Initialize base LLM
        base_llm = GroundedChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
        )

        tools = [generate_future_route_graph]

        agent_executor = create_agent(base_llm, tools)

        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
        firebase_history = FirebaseChatHistoryManager()

        user_text = request.message
        user_email = get_user_email_from_request(http_request)
        chat_session_id = str(request.chat_session_id)

        transcript_data = session_manager.load_transcript(chat_session_id)
        transcript_context = (
            build_transcript_advising_context(transcript_data) if transcript_data else None
        )

        if (
            transcript_context
            and TRANSCRIPT_DETERMINISTIC_ADVICE
            and _is_transcript_planning_query(user_text)
        ):
            deterministic_response = _build_deterministic_transcript_advice(transcript_context)
            user_text_saved = to_text(user_text)
            ai_text_saved = to_text(deterministic_response)

            session_manager.save_message(chat_session_id, "human", user_text_saved)
            session_manager.save_message(chat_session_id, "ai", ai_text_saved)

            if user_email:
                firebase_history.save_message(user_email, chat_session_id, "human", user_text_saved)
                firebase_history.save_message(user_email, chat_session_id, "ai", ai_text_saved)

            return ChatResponseDTO(
                response=deterministic_response,
                model_name="deterministic-transcript-advisor",
            )

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

        transcript_section = ""
        if transcript_data:
            transcript_section = f"\nSTUDENT TRANSCRIPT:\n{json.dumps(transcript_data, indent=2)}\n"
            transcript_section += "\nTRANSCRIPT FACTS:\n" + _build_transcript_constraint_block(transcript_context) + "\n"

        system_prompt = SystemMessage(content=f"""
        You are GauchoGuider, an academic-focused UCSB advising assistant.

        RULES:
        1. Prioritize educational outcomes: course planning, prerequisites, degree progress, GPA strategy, study tactics, and graduation readiness.
        2. Use the student transcript (if provided) to personalize advice.
           - Never mark in-progress courses as completed.
           - Never recommend completed or in-progress/planned courses as new next courses.
           - For "what should I take next" questions, prioritize the deterministic eligible-next list.
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
        10. Absolutely DO NOT IN ANY CIRCUMSTANCE explicitly say the information is from the context.
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
