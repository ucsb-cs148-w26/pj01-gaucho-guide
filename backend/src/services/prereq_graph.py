import json
import os
import re
from pathlib import Path
from typing import Iterable

try:
    import requests
except Exception:  # pragma: no cover - optional dependency guard
    requests = None


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cmpsc_prereqs.json"
DEFAULT_FLOWCHART_IMAGE_MODEL = "gemini-2.5-flash-image"
FLOWCHART_MODEL_ALIASES = {
    "gemini-2.5-flash-image-preview": "gemini-2.5-flash-image",
    "nano-banana": "gemini-2.5-flash-image",
    "nano banana": "gemini-2.5-flash-image",
}

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

        row_status = row.get("status")
        if isinstance(row_status, str) and row_status.strip().lower() == "completed":
            completed.add(normalize_course_code(raw_code))
            continue

        comp_units = row.get("comp_units")
        try:
            comp_units_f = float(comp_units) if comp_units is not None else None
        except Exception:
            comp_units_f = None
        if comp_units_f is not None:
            if comp_units_f <= 0:
                continue
        else:
            raw_grade = row.get("grade")
            grade = str(raw_grade).strip().upper() if raw_grade is not None else ""
            if grade in INCOMPLETE_OR_FAILING_GRADES:
                continue

        completed.add(normalize_course_code(raw_code))

    return sorted(completed)


def _clean_prereq_label(prereq: str) -> str:
    cleaned = prereq.strip()
    cleaned = re.sub(r"^(OR|AND)\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def build_remaining_graph_spec(
    completed_courses: Iterable[str] | None = None,
) -> tuple[list[str], list[tuple[str, str]]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    completed = {
        normalize_course_code(code)
        for code in (completed_courses or [])
        if isinstance(code, str) and code.strip()
    }

    nodes: list[str] = []
    seen_nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()

    def add_node(label: str):
        if label in seen_nodes:
            return
        seen_nodes.add(label)
        nodes.append(label)

    for course, details in data.items():
        course_norm = normalize_course_code(course)

        if course_norm in completed:
            continue

        add_node(course)

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

            add_node(clean_prereq)
            edge = (clean_prereq, course)
            if edge not in seen_edges:
                seen_edges.add(edge)
                edges.append(edge)

    return nodes, edges


def build_flowchart_image_prompt(nodes: list[str], edges: list[tuple[str, str]]) -> str:
    graph_payload = {
        "nodes": nodes,
        "edges": [{"from": src, "to": dst} for src, dst in edges],
    }
    return (
        "Create a clean, readable prerequisite flowchart image for UCSB Computer Science.\n"
        "Requirements:\n"
        "- White background.\n"
        "- Top-to-bottom flow.\n"
        "- Rounded rectangles for course nodes.\n"
        "- Directed arrows from prerequisite to dependent course.\n"
        "- Use every node and edge exactly as provided.\n"
        "- Do not add, remove, or rename courses.\n"
        "- Keep all text legible.\n"
        "- Title: Remaining UCSB CS Prerequisite Flowchart.\n\n"
        "Graph data (JSON):\n"
        f"{json.dumps(graph_payload, indent=2)}"
    )


def _extract_image_from_gemini_response(payload: dict) -> str | None:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return None

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content", {})
        if not isinstance(content, dict):
            continue
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue

            inline_data = part.get("inlineData") or part.get("inline_data")
            if isinstance(inline_data, dict):
                b64_data = inline_data.get("data")
                mime = inline_data.get("mimeType") or inline_data.get("mime_type") or "image/png"
                if isinstance(b64_data, str) and b64_data:
                    return f"data:{mime};base64,{b64_data}"

            file_data = part.get("fileData") or part.get("file_data")
            if isinstance(file_data, dict):
                uri = file_data.get("fileUri") or file_data.get("file_uri") or file_data.get("uri")
                if isinstance(uri, str) and uri.startswith("http"):
                    return uri

    return None


def generate_flowchart_image_with_gemini(prompt: str) -> str:
    if requests is None:
        raise RuntimeError("The requests dependency is not available.")

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY or GEMINI_API_KEY for Gemini image generation.")

    model = os.getenv("FLOWCHART_GEMINI_IMAGE_MODEL", DEFAULT_FLOWCHART_IMAGE_MODEL).strip()
    if model.startswith("models/"):
        model = model.split("models/", 1)[1]
    model = FLOWCHART_MODEL_ALIASES.get(model.lower(), model)
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    req_payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseModalities": ["TEXT", "IMAGE"],
        },
    }

    try:
        res = requests.post(endpoint, json=req_payload, timeout=90)
    except Exception as e:
        raise RuntimeError(f"Gemini flowchart request failed: {e}") from e

    if res.status_code >= 300:
        detail = ""
        try:
            body = res.json()
            detail = json.dumps(body)
        except Exception:
            detail = res.text
        raise RuntimeError(
            f"Gemini flowchart request failed with status {res.status_code}: {detail[:500]}"
        )

    try:
        body = res.json()
    except Exception as e:
        raise RuntimeError("Gemini returned a non-JSON response for flowchart generation.") from e

    image_url = _extract_image_from_gemini_response(body)
    if image_url:
        return image_url

    raise RuntimeError("Gemini did not return an image for flowchart generation.")


def generate_remaining_path_image(
    completed_courses: Iterable[str] | None = None,
) -> tuple[str | None, str]:
    """
    Returns (image_url, message).
    image_url is None when no remaining courses exist.
    """
    nodes, edges = build_remaining_graph_spec(completed_courses)
    if not nodes:
        return None, "The student has completed all courses in the prerequisite database."

    prompt = build_flowchart_image_prompt(nodes, edges)
    return generate_flowchart_image_with_gemini(prompt), "Flowchart generated successfully."
