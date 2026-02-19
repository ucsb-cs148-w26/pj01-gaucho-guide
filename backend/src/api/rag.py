import asyncio
import os

from dotenv import load_dotenv
from fastapi import APIRouter

from src.managers.vector_manager import VectorManager
from src.scrapers.rmp_scraper import get_school_reviews, get_school_professors
from src.scrapers.reddit_scraper import fetch_reddit_docs_for_cmpsc_catalog
from src.models.rag_response_dto import RagResponseDTO

router = APIRouter(prefix="/rag", tags=["rag", "Internal"])

load_dotenv()
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
UCSB_SCHOOL_ID = os.getenv("UCSB_SCHOOL_ID")
REDDIT_CLASS_NAMESPACE = os.getenv("REDDIT_CLASS_NAMESPACE", "reddit_class_data")


@router.post("/update", response_model=RagResponseDTO)
async def update_llm_knowledge():
    vector_manager = VectorManager(PINECONE_API_KEY)

    try:
        loop = asyncio.get_event_loop()
        school_reviews, professors, reddit_result = await asyncio.gather(
            loop.run_in_executor(None, get_school_reviews, UCSB_SCHOOL_ID),
            loop.run_in_executor(None, get_school_professors, UCSB_SCHOOL_ID),
            loop.run_in_executor(None, fetch_reddit_docs_for_cmpsc_catalog),
        )
    except Exception as e:
        return {"message": f"Scraping failed: {str(e)}", "model_name": MODEL_NAME}

    if school_reviews:
        vector_manager.ingest_data(school_reviews, "school_reviews")
    if professors:
        vector_manager.ingest_data(professors, "professor_data")
    reddit_docs, discovered_codes = reddit_result
    if reddit_docs:
        vector_manager.ingest_data(reddit_docs, REDDIT_CLASS_NAMESPACE)

    return {
        "message": (
            "Successfully updated knowledge base. "
            f"Reddit docs ingested: {len(reddit_docs)} across {len(discovered_codes)} CMPSC course codes."
        ),
        "model_name": MODEL_NAME
    }
