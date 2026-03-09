from backend.src.services.transcript_advisor import build_transcript_advising_context


def test_advising_context_respects_completion_and_in_progress():
    transcript = {
        "major": "Computer Science",
        "cumulative_gpa": 3.32,
        "parser_strategy_used": "gemini",
        "courses": [
            {"quarter": "Fall 2023", "course_code": "CMPSC 8", "course_title": "Intro", "att_units": 4.0, "comp_units": 4.0, "grade": "A"},
            {"quarter": "Winter 2024", "course_code": "CMPSC 16", "course_title": "Problem Solving I", "att_units": 4.0, "comp_units": 4.0, "grade": "B"},
            {"quarter": "Spring 2024", "course_code": "CMPSC 24", "course_title": "Problem Solving II", "att_units": 4.0, "comp_units": 4.0, "grade": "A-"},
            {"quarter": "Fall 2024", "course_code": "CMPSC 32", "course_title": "OOD", "att_units": 4.0, "comp_units": 4.0, "grade": "B"},
            {"quarter": "Fall 2024", "course_code": "CMPSC 40", "course_title": "Foundations", "att_units": 5.0, "comp_units": 5.0, "grade": "B+"},
            {"quarter": "Winter 2025", "course_code": "CMPSC 64", "course_title": "Comp Org", "att_units": 4.0, "comp_units": 4.0, "grade": "B-"},
            {"quarter": "Winter 2025", "course_code": "CMPSC 130A", "course_title": "DSA", "att_units": 4.0, "comp_units": 4.0, "grade": "A-"},
            {"quarter": "Spring 2025", "course_code": "CMPSC 154", "course_title": "Architecture", "att_units": 4.0, "comp_units": 4.0, "grade": "A"},
            {"quarter": "Winter 2026", "course_code": "CMPSC 130B", "course_title": "DSA II", "att_units": 4.0, "comp_units": 0.0, "grade": None},
            {"quarter": "Winter 2026", "course_code": "CMPSC 148", "course_title": "Project", "att_units": 4.0, "comp_units": 0.0, "grade": None},
        ],
    }

    ctx = build_transcript_advising_context(transcript)

    assert ctx["major"] == "Computer Science"
    assert ctx["cumulative_gpa"] == 3.32
    assert "CMPSC 130A" in ctx["completed_courses"]
    assert "CMPSC 154" in ctx["completed_courses"]
    assert "CMPSC 130B" in ctx["in_progress_courses"]
    assert "CMPSC 148" in ctx["in_progress_courses"]

    # Already completed/in-progress courses should not appear as next recommendations.
    assert "CMPSC 130A" not in ctx["eligible_next_courses"]
    assert "CMPSC 130B" not in ctx["eligible_next_courses"]
    assert "CMPSC 148" not in ctx["eligible_next_courses"]


def test_advising_context_understands_explicit_status_field():
    transcript = {
        "major": "Computer Science",
        "courses": [
            {
                "quarter": "Winter 2026",
                "course_code": "CMPSC 170",
                "course_title": "Operating Systems",
                "status": "in_progress",
            },
            {
                "quarter": "Fall 2025",
                "course_code": "CMPSC 176A",
                "course_title": "Networks",
                "status": "completed",
            },
        ],
    }

    ctx = build_transcript_advising_context(transcript)

    assert "CMPSC 170" in ctx["in_progress_courses"]
    assert "CMPSC 176A" in ctx["completed_courses"]

