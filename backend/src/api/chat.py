import os

from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from backend.src.managers.session_manager import SessionManager
from backend.src.managers.vector_manager import VectorManager
from backend.src.models.chat_request_dto import ChatRequestDTO
from backend.src.models.chat_response_dto import ChatResponseDTO

router = APIRouter(prefix="/chat", tags=["chat", "Public"])

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
UCSB_SCHOOL_ID = os.getenv("UCSB_SCHOOL_ID")


@router.get("/response", response_model=ChatResponseDTO)
def get_chat_response(request: ChatRequestDTO):
    try:
        llm = ChatOllama(model=request.model_name, temperature=0)  # Keep temperature low to avoid hallucinations
        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
    except Exception as e:
        return {
            "message": "Internal error",
            "model_name": request.model_name
        }

    system_prompt = SystemMessage(content="""
        You are GauchoGuider. A guide for ucsb students navigating through college life.

        RULES:
        1. STRICTLY talk about UCSB, Isla Vista, or college life at Santa Barbara. 
        2. If the user asks about unrelated topics (like generic coding, world news, or other universities), 
        politely steer them back to UCSB or say you only know about UCSB.
        3. Use the provided Context (reviews and stats) to answer questions accurately.
        4. When mentioning names, always use the provided Context and the Context only. DO NOT ADD EXTRA INFORMATION.
        5. Be casual, use slang like "IV" (Isla Vista), "The Loop", "Arroyo", etc., if appropriate.
        """)

    docs = vector_manager.search(request.chat_history[-1].content, k=4)
    context_text = "\n\n".join([d.page_content for d in docs])

    rag_prompt = f"""
                CONTEXT FROM RMP REVIEWS:
                {context_text}

                USER QUESTION:
                {request.chat_history[-1]}
                """

    messages = [system_prompt] + request.chat_history[:-1] + [HumanMessage(content=rag_prompt)]
    response = llm.invoke(messages)
    response_content = response.content

    session_manager.save_message(str(request.chat_session_id), "human", request.chat_history[-1].content)
    session_manager.save_message(str(request.chat_session_id), "ai", response_content)

    response = llm.invoke(request.chat_history)
    return {
        "response": response.content,
        "model_name": request.model_name
    }
