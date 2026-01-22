import concurrent.futures
import os

from dotenv import load_dotenv
from fastapi import APIRouter

from backend.src.managers.vector_manager import VectorManager
from backend.src.scrapers.rmp_scraper import get_school_reviews, get_school_professors
from backend.src.models.rag_response_dto import RagResponseDTO

router = APIRouter(prefix="/rag", tags=["rag", "Internal"])

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
UCSB_SCHOOL_ID = os.getenv("UCSB_SCHOOL_ID")


@router.post("/update", response_model=RagResponseDTO)
def update_llm_knowledge():
    vector_manager = VectorManager(PINECONE_API_KEY)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_reviews = executor.submit(get_school_reviews, UCSB_SCHOOL_ID)
        future_profs = executor.submit(get_school_professors, UCSB_SCHOOL_ID)
        try:
            school_reviews = future_reviews.result()
        except Exception as e:
            school_reviews = None

        try:
            professors = future_profs.result()
        except Exception as e:
            professors = None
    if school_reviews:
        vector_manager.ingest_data(school_reviews, "school_reviews")
    if professors:
        vector_manager.ingest_data(professors, "professor_data")
    return {
        "message": "Successfully updated knowledge base.",
        "model_name": MODEL_NAME
    }
