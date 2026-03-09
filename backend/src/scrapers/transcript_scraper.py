"""
transcript_scraper.py
---------------------
Parses a UCSB unofficial transcript PDF into structured JSON.

Primary path:
  1) Extract text from PDF with pymupdf4llm (best layout) or pypdf fallback.
  2) Parse transcript fields and course rows with robust regex windows around
     enrollment codes across the full document (not line-fragile).

Default behavior:
  - Gemini-first (if API key is configured), then deterministic local parsing.
  - Final output is selected after deterministic normalization + quality checks.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from bisect import bisect_right
from typing import Any

try:
    import requests
except Exception:
    requests = None

try:
    import pymupdf4llm
except Exception:
    pymupdf4llm = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


QUARTER_RE = re.compile(r"\b(Fall|Winter|Spring|Summer)\s+((?:19|20)\d{2})\b", re.IGNORECASE)
ENRL_RE = re.compile(r"\b(\d{5})\b")
GRADE_RE = re.compile(r"\*\*(A[+\-]?|B[+\-]?|C[+\-]?|D[+\-]?|F|P|NP|W|IP|S|U|I)\*\*")
UNITS_RE = re.compile(
    r"(?P<att>\d+(?:\.\d+)?)\s+"
    r"(?P<comp>\d+(?:\.\d+)?)\s+"
    r"(?P<gpa_units>\d+(?:\.\d+)?)\s+"
    r"(?P<points>\d+(?:\.\d+)?)"
)

COURSE_CODE_RE_STR = (
    r"[A-Z]{1,5}(?:\s+[A-Z]{1,5})?\s*\d+[A-Z0-9]*(?:\s*-\s*\d+[A-Z]*)?"
)
COURSE_HEADER_RE = re.compile(
    rf"(?P<course_code>{COURSE_CODE_RE_STR})\s*-\s*(?P<course_title>[A-Z][A-Z0-9/&,\.\'()\- ]{{2,}})"
)

PASSING_OR_IN_PROGRESS_GRADES = {"A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "P", "S", "IP", "I", "W"}
PASSING_GRADES = {"A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "P", "S"}
FAILING_GRADES = {"F", "NP", "U", "D", "D+", "D-"}
IN_PROGRESS_GRADES = {"IP", "I"}
MAJOR_STOP_MARKERS = (
    "COURSE",
    "GRADE",
    "ENRLCD",
    "ATT UNIT",
    "COMP UNIT",
    "GPA UNIT",
    "UNITPOINTS",
    "QUARTER TOTAL",
    "CUMULATIVE TOTAL",
)
MAJOR_ALIASES = {
    "CMPSC": "Computer Science",
    "CS": "Computer Science",
    "COMP SCI": "Computer Science",
    "COMPUTER SCIENCE": "Computer Science",
}


def _empty_result() -> dict:
    return {
        "student_name": None,
        "student_id": None,
        "major": None,
        "courses": [],
        "cumulative_gpa": None,
        "total_units_attempted": None,
        "total_units_passed": None,
        "parser_strategy_used": None,
    }


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


def _extract_with_pymupdf4llm(pdf_bytes: bytes) -> str | None:
    if pymupdf4llm is None:
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        tmp.write(pdf_bytes)
        tmp.close()
        text = pymupdf4llm.to_markdown(tmp.name) or ""
        return text.strip() or None
    except Exception:
        return None
    finally:
        _safe_unlink(tmp.name)


def _extract_with_pypdf(pdf_bytes: bytes) -> str | None:
    if PdfReader is None:
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        tmp.write(pdf_bytes)
        tmp.close()
        reader = PdfReader(tmp.name)
        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n\n".join(pages).strip()
        return text or None
    except Exception:
        return None
    finally:
        _safe_unlink(tmp.name)


def _pdf_to_markdown(pdf_bytes: bytes) -> str:
    """
    Attempts multiple extractors and returns the first non-empty text.
    """
    extracted = _extract_with_pymupdf4llm(pdf_bytes)
    if extracted:
        return extracted

    extracted = _extract_with_pypdf(pdf_bytes)
    if extracted:
        return extracted

    raise RuntimeError("No PDF parser available. Install pymupdf4llm or pypdf.")


def _normalize_text(raw_text: str) -> str:
    text = raw_text.replace("\x00", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_student_id(compact_text: str) -> str | None:
    patterns = [
        r"\bPerm(?:\s+Number)?[:#\s\-]+([A-Z0-9]{6,12})\b",
        r"\bStudent\s*ID[:#\s\-]+([A-Z0-9]{6,12})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, compact_text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _normalize_name(raw_name: str) -> str | None:
    cleaned = re.sub(r"[^A-Za-z,\-'\s]", " ", raw_name)
    cleaned = _compact_whitespace(cleaned)
    if not cleaned:
        return None
    return cleaned.title()


def _extract_student_name(compact_text: str, student_id: str | None) -> str | None:
    patterns = [
        r"\bName[:\s\-]+([A-Z][A-Z,\-'\s]{4,80})\b",
        r"\bStudent[:\s\-]+([A-Z][A-Z,\-'\s]{4,80})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, compact_text, re.IGNORECASE)
        if m:
            name = _normalize_name(m.group(1))
            if name:
                return name

    if student_id:
        m = re.search(
            rf"(.{{0,90}})\bPerm(?:\s+Number)?[:#\s\-]+{re.escape(student_id)}\b",
            compact_text,
            re.IGNORECASE,
        )
        if m:
            candidate = _normalize_name(m.group(1))
            if candidate:
                candidate = re.sub(r"(Unofficial Transcript|University Of California|Santa Barbara)$", "", candidate, flags=re.IGNORECASE).strip()
                return candidate or None
    return None


def _clean_major_candidate(raw_major: str) -> str | None:
    major = _compact_whitespace(raw_major)

    for marker in MAJOR_STOP_MARKERS:
        idx = major.upper().find(marker)
        if idx != -1:
            major = major[:idx].strip()

    major = re.split(
        r"\b(?:Fall|Winter|Spring|Summer)\s+(?:19|20)\d{2}\b",
        major,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    major = re.sub(r"\b(Department|Track|Option)\b.*$", "", major, flags=re.IGNORECASE).strip()
    major = re.split(r"\b(?:Cumulative|Quarter)\s+Total\b", major, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    major = re.sub(r"\b(Fall|Winter|Spring|Summer)\b.*$", "", major, flags=re.IGNORECASE).strip()
    major = re.sub(r"[^A-Za-z&/\-\s]", " ", major)
    major = _compact_whitespace(major)
    if not major:
        return None

    bad_tokens = {"COURSE", "GRADE", "ENRLCD", "ATT", "COMP", "UNIT", "UNITPOINTS"}
    tokens_upper = {t.upper() for t in major.split()}
    if tokens_upper & bad_tokens:
        return None

    if len(major) < 3:
        return None

    normalized_key = major.upper()
    if normalized_key in MAJOR_ALIASES:
        return MAJOR_ALIASES[normalized_key]
    return major.title()


def _extract_major(lines: list[str], compact_text: str) -> str | None:
    # Prefer line-based parsing to avoid accidental capture of table headers.
    for line in lines:
        m = re.search(r"\bMajor(?:\(s\))?[:\s\-]+(.+)$", line, re.IGNORECASE)
        if m:
            cleaned = _clean_major_candidate(m.group(1))
            if cleaned:
                return cleaned

    for line in lines:
        m = re.search(
            r"\b(?:ENGR|L&S|COE|CLAS|BREN|EDUC|MUS|FINE)\s*/\s*(?:BS|BA|MS|PHD|Minor)\s*/\s*(.+)$",
            line,
            re.IGNORECASE,
        )
        if m:
            cleaned = _clean_major_candidate(m.group(1))
            if cleaned:
                return cleaned

    # Fallback to compact text when line-based signals are missing.
    patterns = [
        r"\bMajor(?:\(s\))?[:\s\-]+([A-Za-z][A-Za-z/&,\-\s]{2,80})\b",
        r"\b(?:ENGR|L&S|COE|CLAS|BREN|EDUC|MUS|FINE)\s*/\s*(?:BS|BA|MS|PHD|Minor)\s*/\s*([A-Za-z][A-Za-z&\-\s]{2,60})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, compact_text, re.IGNORECASE)
        if m:
            cleaned = _clean_major_candidate(m.group(1))
            if cleaned:
                return cleaned
    return None


def _extract_cumulative(lines: list[str], compact_text: str) -> tuple[float | None, float | None, float | None]:
    cumulative_gpa = None
    total_units_attempted = None
    total_units_passed = None

    for line in lines:
        if "cumulative total" not in line.lower():
            continue

        gpa_m = re.search(r"\bGPA\s+\*{0,2}(\d+(?:\.\d+)?)\*{0,2}", line, re.IGNORECASE)
        if gpa_m:
            cumulative_gpa = float(gpa_m.group(1))

        units_matches = list(UNITS_RE.finditer(line))
        if units_matches:
            units_m = units_matches[-1]
            total_units_attempted = float(units_m.group("att"))
            total_units_passed = float(units_m.group("comp"))

    if cumulative_gpa is None or total_units_attempted is None:
        cm = re.search(r"\bCumulative\s+Total\b", compact_text, re.IGNORECASE)
        if cm:
            snippet = compact_text[cm.start(): cm.start() + 260]
            if cumulative_gpa is None:
                gpa_m = re.search(r"\bGPA\s+\*{0,2}(\d+(?:\.\d+)?)\*{0,2}", snippet, re.IGNORECASE)
                if gpa_m:
                    cumulative_gpa = float(gpa_m.group(1))
            units_m = UNITS_RE.search(snippet)
            if units_m:
                total_units_attempted = float(units_m.group("att"))
                total_units_passed = float(units_m.group("comp"))

    return cumulative_gpa, total_units_attempted, total_units_passed


def _quarter_markers(compact_text: str) -> tuple[list[int], list[str]]:
    positions: list[int] = []
    labels: list[str] = []
    for m in QUARTER_RE.finditer(compact_text):
        positions.append(m.start())
        labels.append(f"{m.group(1).title()} {m.group(2)}")
    return positions, labels


def _quarter_for_position(pos: int, quarter_positions: list[int], quarter_labels: list[str]) -> str | None:
    if not quarter_positions:
        return None
    idx = bisect_right(quarter_positions, pos) - 1
    if idx < 0:
        return None
    return quarter_labels[idx]


def _clean_course_title(raw_title: str) -> str:
    title = raw_title
    title = re.split(r"\s+\*\*(?:A[+\-]?|B[+\-]?|C[+\-]?|D[+\-]?|F|P|NP|W|IP|S|U|I)\*\*", title)[0]
    title = re.sub(r"\s+\d{5}\b.*$", "", title)
    title = _compact_whitespace(title)
    if not title:
        return title
    return title.title()


def _course_quality(course: dict) -> int:
    score = 0
    if course.get("quarter"):
        score += 2
    if course.get("course_code"):
        score += 2
    if course.get("course_title"):
        score += 2
    if course.get("units") is not None:
        score += 1
    if course.get("grade"):
        score += 1
    status = course.get("status")
    if status in {"completed", "in_progress", "planned", "completed_not_passed"}:
        score += 1
    return score


def _derive_status(grade: str | None, comp_units: float | None, att_units: float | None) -> str:
    g = grade.strip().upper() if isinstance(grade, str) else ""

    if comp_units is not None:
        if comp_units > 0:
            if g in FAILING_GRADES:
                return "completed_not_passed"
            return "completed"
        if comp_units == 0:
            if g in IN_PROGRESS_GRADES:
                return "in_progress"
            if att_units is not None and att_units > 0:
                return "in_progress"
            return "planned"

    if g in IN_PROGRESS_GRADES:
        return "in_progress"
    if g in FAILING_GRADES:
        return "completed_not_passed"
    if g in PASSING_GRADES:
        return "completed"
    return "in_progress" if (att_units is not None and att_units > 0) else "planned"


def _extract_courses_via_enrollment_windows(compact_text: str) -> list[dict]:
    quarter_positions, quarter_labels = _quarter_markers(compact_text)
    courses = []

    for enrl_m in ENRL_RE.finditer(compact_text):
        enrl_start, enrl_end = enrl_m.span()

        before = compact_text[max(0, enrl_start - 360):enrl_start]
        after = compact_text[enrl_end:min(len(compact_text), enrl_end + 220)]

        header_matches = list(COURSE_HEADER_RE.finditer(before))
        if not header_matches:
            continue
        header = header_matches[-1]

        course_code = _compact_whitespace(header.group("course_code")).upper()
        course_title = _clean_course_title(header.group("course_title"))
        if not course_title:
            continue

        grade = None
        grade_context = before[header.end():]
        for gm in GRADE_RE.finditer(grade_context):
            grade = gm.group(1)

        units = None
        att_units = None
        comp_units = None
        gpa_units = None
        grade_points = None
        unit_points = None
        units_m = UNITS_RE.search(after)
        if units_m:
            att_units = float(units_m.group("att"))
            comp_units = float(units_m.group("comp"))
            gpa_units = float(units_m.group("gpa_units"))
            unit_points = float(units_m.group("points"))
            units = att_units
            gp = unit_points
            grade_points = gp if gp > 0 else None

        quarter = _quarter_for_position(enrl_start, quarter_positions, quarter_labels)
        if not quarter:
            continue

        status = _derive_status(grade, comp_units, att_units)

        course = {
            "quarter": quarter,
            "course_code": course_code,
            "course_title": course_title,
            "units": units,
            "att_units": att_units,
            "comp_units": comp_units,
            "gpa_units": gpa_units,
            "unit_points": unit_points,
            "grade": grade,
            "grade_points": grade_points,
            "status": status,
            "_enrl": enrl_m.group(1),
            "_pos": enrl_start,
        }

        if _course_quality(course) >= 6:
            courses.append(course)

    # De-duplicate by enrollment code + quarter, keep the highest quality candidate.
    deduped: dict[tuple[str, str], dict] = {}
    for course in courses:
        key = (course.get("_enrl", ""), course["quarter"])
        existing = deduped.get(key)
        if existing is None or _course_quality(course) > _course_quality(existing):
            deduped[key] = course

    sorted_courses = sorted(deduped.values(), key=lambda c: c.get("_pos", 0))
    cleaned_courses = []
    for c in sorted_courses:
        c.pop("_enrl", None)
        c.pop("_pos", None)
        cleaned_courses.append(c)
    return cleaned_courses


def _score_parse(parsed: dict) -> int:
    score = 0
    if parsed.get("student_id"):
        score += 2
    if parsed.get("major"):
        score += 1
    if parsed.get("student_name"):
        score += 1

    courses = parsed.get("courses") or []
    score += min(len(courses), 12) * 2
    completed_count = sum(
        1 for c in courses if isinstance(c, dict) and c.get("status") == "completed"
    )
    if completed_count:
        score += min(completed_count, 10)

    if parsed.get("cumulative_gpa") is not None:
        score += 1
    if parsed.get("total_units_attempted") is not None:
        score += 1
    if parsed.get("total_units_passed") is not None:
        score += 1
    return score


def _needs_fallback(parsed: dict) -> bool:
    courses = parsed.get("courses") or []
    if len(courses) == 0:
        return True
    if len(courses) < 3 and not parsed.get("student_id"):
        return True
    major = parsed.get("major")
    if isinstance(major, str):
        major_upper = major.upper()
        if any(marker in major_upper for marker in MAJOR_STOP_MARKERS):
            return True
    return _score_parse(parsed) < 8


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _sanitize_llm_output(candidate: Any) -> dict | None:
    if not isinstance(candidate, dict):
        return None

    out = _empty_result()
    out["student_name"] = candidate.get("student_name")
    out["student_id"] = candidate.get("student_id")
    out["major"] = candidate.get("major")
    out["cumulative_gpa"] = _coerce_float(candidate.get("cumulative_gpa"))
    out["total_units_attempted"] = _coerce_float(candidate.get("total_units_attempted"))
    out["total_units_passed"] = _coerce_float(candidate.get("total_units_passed"))

    raw_courses = candidate.get("courses", [])
    parsed_courses = []
    if isinstance(raw_courses, list):
        for row in raw_courses:
            if not isinstance(row, dict):
                continue
            code = row.get("course_code")
            quarter = row.get("quarter")
            title = row.get("course_title")
            if not code or not quarter or not title:
                continue

            grade = row.get("grade")
            if isinstance(grade, str):
                grade = grade.strip().upper()
            else:
                grade = None

            att_units = _coerce_float(
                row.get("att_units", row.get("units"))
            )
            comp_units = _coerce_float(row.get("comp_units"))
            gpa_units = _coerce_float(row.get("gpa_units"))
            unit_points = _coerce_float(row.get("unit_points"))
            grade_points = _coerce_float(row.get("grade_points"))
            if grade_points is None and unit_points is not None and unit_points > 0:
                grade_points = unit_points

            status = row.get("status")
            if isinstance(status, str):
                status = status.strip().lower()
            if status not in {"completed", "in_progress", "planned", "completed_not_passed"}:
                status = _derive_status(grade, comp_units, att_units)

            parsed_courses.append(
                {
                    "quarter": str(quarter).strip(),
                    "course_code": _compact_whitespace(str(code).upper()),
                    "course_title": _compact_whitespace(str(title).title()),
                    "units": att_units,
                    "att_units": att_units,
                    "comp_units": comp_units,
                    "gpa_units": gpa_units,
                    "unit_points": unit_points,
                    "grade": grade,
                    "grade_points": grade_points,
                    "status": status,
                }
            )
    out["courses"] = parsed_courses
    return out


def _extract_json_from_llm_text(text: str) -> dict | None:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
    except Exception:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except Exception:
            return None
    return data if isinstance(data, dict) else None


def _parse_with_gemini(transcript_text: str) -> dict | None:
    if requests is None:
        return None

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("TRANSCRIPT_GEMINI_MODEL", "gemini-2.0-flash")
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )

    prompt = """
Extract this UCSB transcript text into strict JSON only.
Return exactly this schema and nothing else:
{
  "student_name": string|null,
  "student_id": string|null,
  "major": string|null,
  "courses": [
    {
      "quarter": string,
      "course_code": string,
      "course_title": string,
      "units": number|null,
      "att_units": number|null,
      "comp_units": number|null,
      "gpa_units": number|null,
      "unit_points": number|null,
      "grade": string|null,
      "grade_points": number|null,
      "status": "completed"|"in_progress"|"planned"|"completed_not_passed"|null
    }
  ],
  "cumulative_gpa": number|null,
  "total_units_attempted": number|null,
  "total_units_passed": number|null
}
""".strip()

    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\nTranscript text:\n{transcript_text[:70000]}"}]}],
        "generationConfig": {"temperature": 0},
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=30)
        if res.status_code >= 300:
            return None
        body = res.json()
        candidates = body.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text_part = None
        for part in parts:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text_part = part["text"]
                break
        if not text_part:
            return None
        parsed = _extract_json_from_llm_text(text_part)
        if not parsed:
            return None
        return _sanitize_llm_output(parsed)
    except Exception:
        return None


def _parse_markdown(raw_text: str) -> dict:
    normalized = _normalize_text(raw_text)
    compact_text = _compact_whitespace(normalized)
    lines = [_compact_whitespace(line) for line in normalized.splitlines() if _compact_whitespace(line)]

    out = _empty_result()
    out["student_id"] = _extract_student_id(compact_text)
    out["student_name"] = _extract_student_name(compact_text, out["student_id"])
    out["major"] = _extract_major(lines, compact_text)
    out["courses"] = _extract_courses_via_enrollment_windows(compact_text)

    gpa, attempted, passed = _extract_cumulative(lines, compact_text)
    out["cumulative_gpa"] = gpa
    out["total_units_attempted"] = attempted
    out["total_units_passed"] = passed
    return out


def _filter_invalid_courses(parsed: dict) -> dict:
    cleaned = dict(parsed)
    valid = []
    for course in parsed.get("courses", []):
        if not isinstance(course, dict):
            continue
        if not course.get("quarter") or not course.get("course_code") or not course.get("course_title"):
            continue
        grade = course.get("grade")
        if isinstance(grade, str):
            grade = grade.strip().upper()
            if grade and grade not in PASSING_OR_IN_PROGRESS_GRADES and not re.match(r"^[A-DF][+\-]?$", grade):
                grade = None

        att_units = _coerce_float(course.get("att_units", course.get("units")))
        comp_units = _coerce_float(course.get("comp_units"))
        gpa_units = _coerce_float(course.get("gpa_units"))
        unit_points = _coerce_float(course.get("unit_points"))
        grade_points = _coerce_float(course.get("grade_points"))
        if grade_points is None and unit_points is not None and unit_points > 0:
            grade_points = unit_points

        status = course.get("status")
        if isinstance(status, str):
            status = status.strip().lower()
        if status not in {"completed", "in_progress", "planned", "completed_not_passed"}:
            status = _derive_status(grade, comp_units, att_units)

        valid.append(
            {
                "quarter": str(course.get("quarter")).strip(),
                "course_code": _compact_whitespace(str(course.get("course_code")).upper()),
                "course_title": _compact_whitespace(str(course.get("course_title"))),
                "units": att_units,
                "att_units": att_units,
                "comp_units": comp_units,
                "gpa_units": gpa_units,
                "unit_points": unit_points,
                "grade": grade,
                "grade_points": grade_points,
                "status": status,
            }
        )
    cleaned["courses"] = valid
    return cleaned


def parse_transcript(pdf_bytes: bytes) -> dict:
    transcript_text = _pdf_to_markdown(pdf_bytes)
    local_result = _filter_invalid_courses(_parse_markdown(transcript_text))
    local_result["parser_strategy_used"] = "local"

    use_gemini = os.getenv("TRANSCRIPT_USE_GEMINI_FALLBACK", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    gemini_primary = os.getenv("TRANSCRIPT_GEMINI_PRIMARY", "1").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    llm_result = None
    if use_gemini:
        # Gemini-first by default for better OCR/layout resilience.
        if gemini_primary or _needs_fallback(local_result):
            llm_result = _parse_with_gemini(transcript_text)
            if llm_result:
                llm_result = _filter_invalid_courses(llm_result)
                llm_result["parser_strategy_used"] = "gemini"

    if llm_result and _score_parse(llm_result) >= _score_parse(local_result):
        return llm_result

    if llm_result and gemini_primary and _score_parse(llm_result) >= 8:
        return llm_result

    return local_result
