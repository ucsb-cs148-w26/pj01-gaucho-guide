import base64
import json
import re
from pathlib import Path
from typing import Iterable


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cmpsc_prereqs.json"

INCOMPLETE_OR_FAILING_GRADES = {
    "",
    "F",
    "NP",
    "W",
    "I",
    "IP",
    "IF",
    "WF",
    "WU",
    "U",
    "D",
    "D+",
    "D-",
}


def normalize_course_code(course_code: str) -> str:
    """
    Normalizes course codes into a consistent format for matching.
    Examples:
      - CS130A -> CMPSC 130A
      - cs 16  -> CMPSC 16
    """
    code = re.sub(r"\s+", " ", course_code.upper()).strip()
    code = re.sub(r"^([A-Z]+)\s*([0-9].*)$", r"\1 \2", code)

    if code.startswith("CS "):
        code = code.replace("CS ", "CMPSC ", 1)

    return code


def extract_completed_courses_from_transcript(transcript_data: dict) -> list[str]:
    completed: set[str] = set()

    for row in transcript_data.get("courses", []):
        if not isinstance(row, dict):
            continue

        raw_code = row.get("course_code")
        if not isinstance(raw_code, str) or not raw_code.strip():
            continue

        raw_grade = row.get("grade")
        grade = str(raw_grade).strip().upper() if raw_grade is not None else ""
        if grade in INCOMPLETE_OR_FAILING_GRADES:
            continue

        completed.add(normalize_course_code(raw_code))

    return sorted(completed)


def _node_id(label: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", label.strip())
    safe = safe.strip("_")
    if not safe:
        safe = "node"
    if safe[0].isdigit():
        safe = f"node_{safe}"
    return safe


def _clean_prereq_label(prereq: str) -> str:
    cleaned = prereq.strip()
    cleaned = re.sub(r"^(OR|AND)\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def build_mermaid_markup(completed_courses: Iterable[str] | None = None) -> str:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    completed = {
        normalize_course_code(code)
        for code in (completed_courses or [])
        if isinstance(code, str) and code.strip()
    }

    mermaid_markup = ["graph TD"]
    nodes_added = 0
    external_nodes: set[str] = set()

    for course, details in data.items():
        course_norm = normalize_course_code(course)

        if course_norm in completed:
            continue

        target = _node_id(course)
        mermaid_markup.append(f'    {target}["{course}"]')
        nodes_added += 1

        prereqs = details.get("prereq_courses", [])
        for prereq in prereqs:
            if not isinstance(prereq, str):
                continue

            clean_prereq = _clean_prereq_label(prereq)
            if not clean_prereq:
                continue

            clean_prereq_norm = normalize_course_code(clean_prereq)
            if clean_prereq_norm in completed:
                continue

            source = _node_id(clean_prereq)

            if clean_prereq not in data and source not in external_nodes:
                mermaid_markup.append(f'    {source}["{clean_prereq}"]')
                external_nodes.add(source)

            mermaid_markup.append(f"    {source} --> {target}")

    if nodes_added == 0:
        return ""

    return "\n".join(mermaid_markup) + "\n"


def mermaid_image_url(mermaid_markup: str) -> str:
    graph_bytes = mermaid_markup.encode("utf-8")
    encoded = base64.urlsafe_b64encode(graph_bytes).decode("ascii")
    return f"https://mermaid.ink/img/{encoded}"


def generate_remaining_path_image(
    completed_courses: Iterable[str] | None = None,
) -> tuple[str | None, str]:
    """
    Returns (image_url, message).
    image_url is None when no remaining courses exist.
    """
    markup = build_mermaid_markup(completed_courses)
    if not markup:
        return None, "The student has completed all courses in the prerequisite database."
    return mermaid_image_url(markup), "Flowchart generated successfully."
