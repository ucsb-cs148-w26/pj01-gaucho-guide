import os

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.managers.session_manager import SessionManager
from src.scrapers.transcript_scraper import parse_transcript

router = APIRouter(prefix="/transcript", tags=["transcript"])

load_dotenv(dotenv_path=".env", override=True)


class TranscriptResponse(BaseModel):
    message: str
    data: dict


class ClearTranscriptResponse(BaseModel):
    message: str


@router.post("/parse", response_model=TranscriptResponse)
async def upload_and_parse_transcript(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed = parse_transcript(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse transcript: {str(e)}")

    session_manager = SessionManager()
    session_manager.save_transcript(session_id, parsed)

    return TranscriptResponse(
        message="Transcript parsed and stored for this session.",
        data=parsed,
    )


@router.delete("/clear", response_model=ClearTranscriptResponse)
async def clear_transcript(session_id: str):
    session_manager = SessionManager()
    session_manager.clear_transcript(session_id)
    return ClearTranscriptResponse(message="Transcript cleared for this session.")
