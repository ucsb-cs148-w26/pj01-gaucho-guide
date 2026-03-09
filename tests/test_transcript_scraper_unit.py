from backend.src.scrapers import transcript_scraper as ts


def test_major_parsing_ignores_table_headers_artifacts():
    raw = """
    Name: DOE, JANE
    Perm Number: 1234567
    ENGR / BS / CMPSC Course GradeEnrlCd Att Unit Comp Unit Gpa Unitpoints
    Fall 2023
    CMPSC 16 - PROBLEM SOLVING I **A** 12345 4.0 4.0 4.0 16.0
    """

    parsed = ts._parse_markdown(raw)
    assert parsed["major"] == "Computer Science"


def test_parse_markdown_extracts_wrapped_rows():
    raw = """
    Unofficial Transcript
    Name: DOE, JANE
    Perm Number: 1234567
    Major: Computer Science

    Fall 2023
    CMPSC 16 - PROBLEM SOLVING I **A** 12345 4.0 4.0 4.0 16.0
    MATH 4A - LINEAR ALGEBRA **B+** 22345 4.0 4.0 4.0 13.2

    Winter 2024
    CMPSC 24 - PROBLEM
    SOLVING II **A-** 32345 4.0 4.0 4.0 14.8

    Cumulative Total **GPA 3.70** 12.0 12.0 12.0 44.0
    """

    parsed = ts._parse_markdown(raw)

    assert parsed["student_id"] == "1234567"
    assert parsed["major"] == "Computer Science"
    assert parsed["cumulative_gpa"] == 3.70
    assert parsed["total_units_attempted"] == 12.0
    assert parsed["total_units_passed"] == 12.0
    assert len(parsed["courses"]) >= 3

    course_codes = {c["course_code"] for c in parsed["courses"]}
    assert "CMPSC 16" in course_codes
    assert "MATH 4A" in course_codes
    assert "CMPSC 24" in course_codes

    cmpsc24 = next(c for c in parsed["courses"] if c["course_code"] == "CMPSC 24")
    assert cmpsc24["quarter"] == "Winter 2024"
    assert "Problem" in cmpsc24["course_title"]


def test_parse_transcript_prefers_gemini_when_local_is_low_confidence(monkeypatch):
    local = {
        "student_name": None,
        "student_id": None,
        "major": None,
        "courses": [],
        "cumulative_gpa": None,
        "total_units_attempted": None,
        "total_units_passed": None,
    }
    llm = {
        "student_name": "Jane Doe",
        "student_id": "1234567",
        "major": "Computer Science",
        "courses": [
            {
                "quarter": "Fall 2023",
                "course_code": "CMPSC 16",
                "course_title": "Problem Solving I",
                "units": 4.0,
                "grade": "A",
                "grade_points": 16.0,
            }
        ],
        "cumulative_gpa": 4.0,
        "total_units_attempted": 4.0,
        "total_units_passed": 4.0,
    }

    monkeypatch.setenv("TRANSCRIPT_USE_GEMINI_FALLBACK", "1")
    monkeypatch.setattr(ts, "_pdf_to_markdown", lambda _: "raw transcript text")
    monkeypatch.setattr(ts, "_parse_markdown", lambda _: local)
    monkeypatch.setattr(ts, "_parse_with_gemini", lambda _: llm)

    parsed = ts.parse_transcript(b"%PDF-1.4 fake")
    assert parsed["student_id"] == "1234567"
    assert len(parsed["courses"]) == 1


def test_parse_transcript_skips_gemini_when_local_is_good(monkeypatch):
    local = {
        "student_name": "Jane Doe",
        "student_id": "1234567",
        "major": "Computer Science",
        "courses": [
            {
                "quarter": "Fall 2023",
                "course_code": "CMPSC 16",
                "course_title": "Problem Solving I",
                "units": 4.0,
                "grade": "A",
                "grade_points": 16.0,
            },
            {
                "quarter": "Winter 2024",
                "course_code": "CMPSC 24",
                "course_title": "Problem Solving II",
                "units": 4.0,
                "grade": "A-",
                "grade_points": 14.8,
            },
            {
                "quarter": "Winter 2024",
                "course_code": "MATH 4A",
                "course_title": "Linear Algebra",
                "units": 4.0,
                "grade": "B+",
                "grade_points": 13.2,
            },
        ],
        "cumulative_gpa": 3.7,
        "total_units_attempted": 12.0,
        "total_units_passed": 12.0,
    }

    monkeypatch.setenv("TRANSCRIPT_USE_GEMINI_FALLBACK", "1")
    monkeypatch.setattr(ts, "_pdf_to_markdown", lambda _: "raw transcript text")
    monkeypatch.setattr(ts, "_parse_markdown", lambda _: local)

    llm_called = {"value": False}

    def _fake_llm(_):
        llm_called["value"] = True
        return None

    monkeypatch.setattr(ts, "_parse_with_gemini", _fake_llm)

    parsed = ts.parse_transcript(b"%PDF-1.4 fake")
    assert parsed["student_id"] == "1234567"
    assert len(parsed["courses"]) == 3
    assert llm_called["value"] is False
