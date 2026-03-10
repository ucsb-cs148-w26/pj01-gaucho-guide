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


def _resolve_prereq_label(prereq: str, known_courses: set[str]) -> tuple[str | None, bool]:
    if not isinstance(prereq, str):
        return None, False

    cleaned = _clean_prereq_label(prereq)
    if not cleaned:
        return None, False

    normalized = normalize_course_code(cleaned)
    if normalized in known_courses:
        return normalized, True

    compact = cleaned.upper()
    compact = re.sub(r"^(CMPSC|CS)\s*", "", compact).strip()
    if re.fullmatch(r"\d+[A-Z]?", compact):
        alias = f"CMPSC {compact}"
        if alias in known_courses:
            return alias, True

    return normalized, False


def _course_sort_key(course: str) -> tuple[int, int, str]:
    normalized = normalize_course_code(course)
    m = re.match(r"^CMPSC\s+(\d+)([A-Z]?)$", normalized)
    if not m:
        return (9999, 9999, normalized)
    number = int(m.group(1))
    suffix = m.group(2) or ""
    suffix_rank = ord(suffix) if suffix else 0
    return (number, suffix_rank, normalized)


def _compute_subset_levels(
    subset_courses: list[str], edges: set[tuple[str, str]]
) -> dict[str, int]:
    indegree = {course: 0 for course in subset_courses}
    outgoing: dict[str, set[str]] = {course: set() for course in subset_courses}

    for source, target in edges:
        if source not in indegree or target not in indegree:
            continue
        if target in outgoing[source]:
            continue
        outgoing[source].add(target)
        indegree[target] += 1

    queue = sorted([course for course, degree in indegree.items() if degree == 0], key=_course_sort_key)
    levels = {course: 0 for course in subset_courses}

    while queue:
        node = queue.pop(0)
        for neighbor in sorted(outgoing[node], key=_course_sort_key):
            levels[neighbor] = max(levels[neighbor], levels[node] + 1)
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return levels


def _is_cmpsc_0_to_199(course_code: str) -> bool:
    normalized = normalize_course_code(course_code)
    m = re.fullmatch(r"CMPSC (\d{1,3})([A-Z]?)", normalized)
    if not m:
        return False
    number = int(m.group(1))
    return 0 <= number <= 199


def _prereq_sort_key(course: str) -> tuple[int, int, int, str]:
    normalized = normalize_course_code(course)
    m = re.match(r"^CMPSC\s+(\d+)([A-Z]?)$", normalized)
    if m:
        number = int(m.group(1))
        suffix = m.group(2) or ""
        suffix_rank = ord(suffix) if suffix else 0
        return (0, number, suffix_rank, normalized)
    return (1, 9999, 9999, normalized)


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


def build_upper_division_flowchart_data(completed_courses: Iterable[str] | None = None) -> dict:
    """
    Returns frontend-friendly flowchart data for CMPSC courses in the 0-199 range.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    data: dict[str, dict] = {}
    for course, details in raw_data.items():
        if not isinstance(course, str) or not isinstance(details, dict):
            continue
        data[normalize_course_code(course)] = details

    completed = {
        normalize_course_code(code)
        for code in (completed_courses or [])
        if isinstance(code, str) and code.strip()
    }
    known_courses = set(data.keys())

    target_courses = sorted(
        [course for course in known_courses if _is_cmpsc_0_to_199(course)],
        key=_course_sort_key,
    )
    target_remaining = [course for course in target_courses if course not in completed]
    target_remaining_set = set(target_remaining)

    if not target_remaining:
        return {
            "nodes": [],
            "edges": [],
            "tiers": [],
            "summary": {
                "remaining_cmpsc_0_199_courses": 0,
                "remaining_upper_division_courses": 0,
                "eligible_now": 0,
            },
        }

    edges: set[tuple[str, str]] = set()
    node_meta: dict[str, dict] = {}

    for course in target_remaining:
        prereq_rows = data.get(course, {}).get("prereq_courses", [])
        remaining_prereqs: set[str] = set()

        for prereq in prereq_rows:
            resolved, is_internal = _resolve_prereq_label(prereq, known_courses)
            if not resolved:
                continue

            resolved_norm = normalize_course_code(resolved)
            if resolved_norm in completed:
                continue

            remaining_prereqs.add(resolved_norm)

            if is_internal and resolved_norm in target_remaining_set:
                edges.add((resolved_norm, course))

        unmet_count = len(remaining_prereqs)
        node_meta[course] = {
            "remaining_prereqs": sorted(remaining_prereqs, key=_prereq_sort_key),
            "unmet_prereq_count": unmet_count,
            "eligible_now": unmet_count == 0,
        }

    levels = _compute_subset_levels(target_remaining, edges)
    max_level = max((levels.get(course, 0) for course in target_remaining), default=0)

    tiers: list[list[str]] = []
    for level in range(max_level + 1):
        tier_nodes = sorted(
            [course for course in target_remaining if levels.get(course, 0) == level],
            key=_course_sort_key,
        )
        if tier_nodes:
            tiers.append(tier_nodes)

    nodes = []
    for course in sorted(target_remaining, key=lambda c: (levels.get(c, 0), _course_sort_key(c))):
        meta = node_meta.get(course, {})
        nodes.append(
            {
                "id": course,
                "label": course,
                "tier": levels.get(course, 0),
                "eligible_now": bool(meta.get("eligible_now")),
                "unmet_prereq_count": int(meta.get("unmet_prereq_count", 0)),
                "remaining_prereqs": meta.get("remaining_prereqs", []),
            }
        )

    edge_list = [
        {"from": source, "to": target}
        for source, target in sorted(
            edges,
            key=lambda edge: (_course_sort_key(edge[0]), _course_sort_key(edge[1])),
        )
    ]

    eligible_now_count = sum(1 for node in nodes if node["eligible_now"])

    return {
        "nodes": nodes,
        "edges": edge_list,
        "tiers": tiers,
        "summary": {
            "remaining_cmpsc_0_199_courses": len(target_remaining),
            "remaining_upper_division_courses": len(target_remaining),
            "eligible_now": eligible_now_count,
        },
    }
