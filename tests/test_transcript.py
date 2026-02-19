"""
test_transcript.py
------------------
Tests for the transcript scraper pipeline and its FastAPI endpoints.

Endpoints tested
----------------
  POST   /transcript/parse
      Accepts multipart/form-data with:
        - session_id  (str)  — active chat session
        - file        (PDF)  — UCSB unofficial transcript
      Returns JSON: { "message": str, "data": <transcript dict> }

  DELETE /transcript/clear?session_id=<id>
      Wipes the stored transcript for the given session.

Test coverage
-------------
  test_parse_transcript_success            — PDF upload returns parsed JSON and saves to session
  test_parse_transcript_rejects_non_pdf    — Non-PDF files are rejected with HTTP 400
  test_parse_transcript_handles_parse_error — Parser failures return HTTP 422
  test_clear_transcript                    — DELETE endpoint wipes the session transcript
  test_session_manager_transcript_lifecycle — SQLite save → load → clear round-trip

Running the tests
-----------------
  python -m pytest tests/test_transcript.py -v
"""

import io
import json
import sqlite3
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_connection():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    with patch("backend.src.managers.session_manager.sqlite3.connect", return_value=conn):
        yield conn
    conn.close()


SAMPLE_TRANSCRIPT = {
    "student_name": "Gaucho Student",
    "student_id": "1234567",
    "major": "Computer Science",
    "courses": [
        {
            "quarter": "Fall 2023",
            "course_code": "CMPSC 16",
            "course_title": "Problem Solving I",
            "units": 4,
            "grade": "A",
            "grade_points": 16.0,
        }
    ],
    "cumulative_gpa": 4.0,
    "total_units_attempted": 4,
    "total_units_passed": 4,
}


def test_parse_transcript_success(client, mock_db_connection):
    with patch("backend.src.api.transcript.parse_transcript", return_value=SAMPLE_TRANSCRIPT), \
         patch("backend.src.api.transcript.SessionManager") as MockSM:
        sm_instance = MockSM.return_value

        fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")
        response = client.post(
            "/transcript/parse",
            data={"session_id": "test-session-123"},
            files={"file": ("transcript.pdf", fake_pdf, "application/pdf")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Transcript parsed and stored for this session."
        assert body["data"]["student_name"] == "Gaucho Student"
        assert len(body["data"]["courses"]) == 1
        sm_instance.save_transcript.assert_called_once_with("test-session-123", SAMPLE_TRANSCRIPT)


def test_parse_transcript_rejects_non_pdf(client):
    fake_txt = io.BytesIO(b"not a pdf")
    response = client.post(
        "/transcript/parse",
        data={"session_id": "test-session-123"},
        files={"file": ("transcript.txt", fake_txt, "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_parse_transcript_handles_parse_error(client):
    with patch("backend.src.api.transcript.parse_transcript", side_effect=Exception("bad pdf")):
        fake_pdf = io.BytesIO(b"%PDF-1.4 corrupt")
        response = client.post(
            "/transcript/parse",
            data={"session_id": "test-session-123"},
            files={"file": ("transcript.pdf", fake_pdf, "application/pdf")},
        )
        assert response.status_code == 422
        assert "Failed to parse transcript" in response.json()["detail"]


def test_clear_transcript(client):
    with patch("backend.src.api.transcript.SessionManager") as MockSM:
        sm_instance = MockSM.return_value

        response = client.delete("/transcript/clear", params={"session_id": "test-session-123"})

        assert response.status_code == 200
        assert "cleared" in response.json()["message"]
        sm_instance.clear_transcript.assert_called_once_with("test-session-123")


def test_session_manager_transcript_lifecycle():
    from backend.src.managers.session_manager import SessionManager

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    with patch("backend.src.managers.session_manager.sqlite3.connect", return_value=conn):
        sm = SessionManager()

        assert sm.load_transcript("session-abc") is None

        sm.save_transcript("session-abc", SAMPLE_TRANSCRIPT)
        loaded = sm.load_transcript("session-abc")
        assert loaded is not None
        assert loaded["student_name"] == "Gaucho Student"
        assert loaded["courses"][0]["course_code"] == "CMPSC 16"

        sm.clear_transcript("session-abc")
        assert sm.load_transcript("session-abc") is None
