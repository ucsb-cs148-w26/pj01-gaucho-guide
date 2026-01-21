import concurrent.futures
import os

from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_ollama import ChatOllama

from backend.src.managers.session_manager import SessionManager
from backend.src.managers.vector_manager import VectorManager
from backend.src.scrapers.rmp_scraper import get_school_reviews, get_school_professors
from backend.src.models.rag_response_dto import RagResponseDTO

app = APIRouter(prefix="/chat", tags=["chat", "Public"])

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
UCSB_SCHOOL_ID = os.getenv("UCSB_SCHOOL_ID")


# TODO
@app.get("/response", response_model=RagResponseDTO)
def getChatResponse():
    try:
        llm = ChatOllama(model=MODEL_NAME, temperature=0)  # Keep temperature low to avoid hallucinations
        vector_manager = VectorManager(PINECONE_API_KEY)
        session_manager = SessionManager()
    except Exception as e:
        return
