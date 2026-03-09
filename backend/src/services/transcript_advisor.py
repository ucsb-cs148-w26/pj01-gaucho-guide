import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .prereq_graph import normalize_course_code


PREREQ_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cmpsc_prereqs.json"

PASSING_GRADES = {"A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "P", "S"}
IN_PROGRESS_GRADES = {"IP", "I"}
FAILING_GRADES = {"F", "NP", "U", "D", "D+", "D-"}

STATUS_COMPLETED = "completed"
STATUS_IN_PROGRESS = "in_progress"
STATUS_PLANNED = "planned"
STATUS_NOT_PASSED = "completed_not_passed"


def _safe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _derive_status(grade: str | None, comp_units: float | None, att_units: float | None) -> str:
    g = grade.strip().upper() if isinstance(grade, str) else ""

    if comp_units is not None:
        if comp_units > 0:
            if g in FAILING_GRADES:
                return STATUS_NOT_PASSED
            return STATUS_COMPLETED
        if comp_units == 0:
            if g in IN_PROGRESS_GRADES:
                return STATUS_IN_PROGRESS
            if att_units is not None and att_units > 0:
                return STATUS_IN_PROGRESS
            return STATUS_PLANNED

    if g in IN_PROGRESS_GRADES:
        return STATUS_IN_PROGRESS
    if g in FAILING_GRADES:
        return STATUS_NOT_PASSED
    if g in PASSING_GRADES:
        return STATUS_COMPLETED
    return STATUS_IN_PROGRESS if (att_units is not None and att_units > 0) else STATUS_PLANNED


def _course_sort_key(course_code: str) -> tuple[str, int, str]:
    code = normalize_course_code(course_code)
    m = re.match(r"^([A-Z]+)\s+(\d+)([A-Z0-9]*)$", code)
    if not m:
        return (code, 99999, "")
    return (m.group(1), int(m.group(2)), m.group(3))


def _course_number(course_code: str) -> int | None:
    m = re.match(r"^[A-Z]+\s+(\d+)", normalize_course_code(course_code))
    if not m:
        return None
    return int(m.group(1))


def _is_explicit_course_code(token: str) -> bool:
    return bool(re.match(r"^[A-Z]{1,6}(?:\s+[A-Z]{1,6})?\s+\d+[A-Z0-9]*$", token))


def _normalize_prereq_token(token: str, last_subject: str | None) -> str | None:
    t = token.strip().upper()
    t = re.sub(r"^(OR|AND)\s+", "", t).strip()
    if not t:
        return None

    # e.g. "2A" paired after "MATH 3A" -> "MATH 2A"
    if re.match(r"^\d+[A-Z0-9]*$", t) and last_subject:
        return normalize_course_code(f"{last_subject} {t}")

    # e.g. "CS130A" without space
    t = re.sub(r"^([A-Z]+)(\d)", r"\1 \2", t)
    t = re.sub(r"\s+", " ", t).strip()

    if _is_explicit_course_code(t):
        return normalize_course_code(t)
    return None


def _prereq_groups(prereqs: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []
    last_subject = None

    for raw in prereqs:
        if not isinstance(raw, str):
            continue
        stripped = raw.strip()
        if not stripped:
            continue

        is_or = bool(re.match(r"^OR\s+", stripped, re.IGNORECASE))
        cleaned = re.sub(r"^(OR|AND)\s+", "", stripped, flags=re.IGNORECASE).strip()
        normalized = _normalize_prereq_token(cleaned, last_subject)
        if not normalized:
            continue

        last_subject = normalized.split()[0]
        if is_or and groups:
            groups[-1].append(normalized)
        else:
            groups.append([normalized])

    return groups


@lru_cache(maxsize=1)
def _load_prereq_data() -> dict:
    with open(PREREQ_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _eligible_courses(completed_set: set[str], excluded_set: set[str]) -> list[str]:
    data = _load_prereq_data()
    eligible: list[str] = []

    for course_code, details in data.items():
        normalized_course = normalize_course_code(course_code)
        if normalized_course in excluded_set:
            continue

        prereq_list = details.get("prereq_courses", [])
        groups = _prereq_groups(prereq_list if isinstance(prereq_list, list) else [])
        is_eligible = all(any(option in completed_set for option in group) for group in groups)
        if is_eligible:
            eligible.append(normalized_course)

    eligible.sort(key=_course_sort_key)
    return eligible


def build_transcript_advising_context(transcript_data: dict) -> dict:
    completed_set: set[str] = set()
    in_progress_set: set[str] = set()
    not_passed_set: set[str] = set()

    all_course_rows = transcript_data.get("courses", [])
    if not isinstance(all_course_rows, list):
        all_course_rows = []

    for row in all_course_rows:
        if not isinstance(row, dict):
            continue

        raw_code = row.get("course_code")
        if not isinstance(raw_code, str) or not raw_code.strip():
            continue
        code = normalize_course_code(raw_code)

        grade_raw = row.get("grade")
        grade = grade_raw.strip().upper() if isinstance(grade_raw, str) else None
        att_units = _safe_float(row.get("att_units", row.get("units")))
        comp_units = _safe_float(row.get("comp_units"))

        status = row.get("status")
        if isinstance(status, str):
            status = status.strip().lower()
        if status not in {STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_PLANNED, STATUS_NOT_PASSED}:
            status = _derive_status(grade, comp_units, att_units)

        if status == STATUS_COMPLETED:
            completed_set.add(code)
        elif status in {STATUS_IN_PROGRESS, STATUS_PLANNED}:
            in_progress_set.add(code)
        elif status == STATUS_NOT_PASSED:
            not_passed_set.add(code)

    # Completed overrides other statuses for repeated attempts.
    in_progress_set -= completed_set
    not_passed_set -= completed_set

    excluded_from_recs = completed_set | in_progress_set
    eligible_next = _eligible_courses(completed_set, excluded_from_recs)

    # If the student is already in upper-division CMPSC, avoid noisy lower-division recommendations.
    has_upper_division_cs = any(
        (code.startswith("CMPSC ") and (_course_number(code) or 0) >= 100)
        for code in (completed_set | in_progress_set)
    )
    if has_upper_division_cs:
        eligible_next = [
            code
            for code in eligible_next
            if not code.startswith("CMPSC ") or ((_course_number(code) or 0) >= 100)
        ]

    completed_courses = sorted(completed_set, key=_course_sort_key)
    in_progress_courses = sorted(in_progress_set, key=_course_sort_key)
    not_passed_courses = sorted(not_passed_set, key=_course_sort_key)

    completed_cs = [c for c in completed_courses if c.startswith("CMPSC ")]
    in_progress_cs = [c for c in in_progress_courses if c.startswith("CMPSC ")]
    eligible_cs = [c for c in eligible_next if c.startswith("CMPSC ")]

    return {
        "major": transcript_data.get("major"),
        "cumulative_gpa": transcript_data.get("cumulative_gpa"),
        "parser_strategy_used": transcript_data.get("parser_strategy_used"),
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "not_passed_courses": not_passed_courses,
        "completed_cs_courses": completed_cs,
        "in_progress_cs_courses": in_progress_cs,
        "eligible_next_courses": eligible_next,
        "eligible_next_cs_courses": eligible_cs,
    }
