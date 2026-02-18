"""
transcript_scraper.py
---------------------
Parses a UCSB unofficial transcript PDF into structured JSON using:
  1. pymupdf4llm  — converts the PDF to Markdown
  2. Gemini (gemini-1.5-flash by default) — extracts structured data from the Markdown

Output JSON schema
------------------
{
  "student_name":          str,
  "student_id":            str,
  "major":                 str,
  "courses": [
    {
      "quarter":       str,   # e.g. "Fall 2023"
      "course_code":   str,   # e.g. "CMPSC 16"
      "course_title":  str,
      "units":         int,
      "grade":         str,   # e.g. "A", "B+", "P", "NP", "W", "IP"
      "grade_points":  float | null
    }
  ],
  "cumulative_gpa":        float | null,
  "total_units_attempted": int   | null,
  "total_units_passed":    int   | null
}

Usage
-----
  from backend.src.scrapers.transcript_scraper import parse_transcript

  with open("transcript.pdf", "rb") as f:
      result = parse_transcript(f.read())

Environment variables
---------------------
  GEMINI_MODEL_NAME  — Gemini model to use (default: gemini-1.5-flash)
  GOOGLE_API_KEY     — required by langchain-google-genai
"""

import json
import os
import tempfile

import pymupdf4llm
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(dotenv_path=".env", override=True)
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")


def parse_transcript(pdf_bytes: bytes) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        markdown_text = pymupdf4llm.to_markdown(tmp_path)
    finally:
        os.unlink(tmp_path)

    llm = ChatGoogleGenerativeAI(
        model=DEFAULT_GEMINI_MODEL,
        temperature=0,
    )

    system_prompt = SystemMessage(content="""
You are a transcript parser. Extract all academic information from the provided UCSB unofficial transcript text and return ONLY valid JSON with no markdown fences, no explanation, and no extra text.

The JSON must follow this exact schema:
{
  "student_name": "string",
  "student_id": "string",
  "major": "string",
  "courses": [
    {
      "quarter": "string (e.g. Fall 2023)",
      "course_code": "string (e.g. CMPSC 16)",
      "course_title": "string",
      "units": number,
      "grade": "string (e.g. A, B+, P, NP, W, IP)",
      "grade_points": number or null
    }
  ],
  "cumulative_gpa": number or null,
  "total_units_attempted": number or null,
  "total_units_passed": number or null
}

Rules:
- Include every course listed, including transfer credits, in-progress (IP), and withdrawals (W).
- If a field cannot be determined, use null.
- Return ONLY the JSON object.
""".strip())

    user_message = HumanMessage(content=f"Parse this UCSB transcript:\n\n{markdown_text}")

    response = llm.invoke([system_prompt, user_message])
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
