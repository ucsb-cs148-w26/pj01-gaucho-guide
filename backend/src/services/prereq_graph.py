import base64
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cmpsc_prereqs.json"
FOUNDATION_NODE = "NON-CS FOUNDATION"

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
        cmpsc_alias = f"CMPSC {compact}"
        if cmpsc_alias in known_courses:
            return cmpsc_alias, True

    return cleaned, False


def _course_sort_key(course: str) -> tuple[int, int, str]:
    if course == FOUNDATION_NODE:
        return (-1, -1, course)

    normalized = normalize_course_code(course)
    m = re.match(r"^CMPSC\s+(\d+)([A-Z]?)$", normalized)
    if not m:
        return (9999, 9999, normalized)
    number = int(m.group(1))
    suffix = m.group(2) or ""
    suffix_rank = ord(suffix) if suffix else 0
    return (number, suffix_rank, normalized)


def _compute_levels(nodes: set[str], edges: set[tuple[str, str]]) -> dict[str, int]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    indegree = {node: 0 for node in nodes}

    for source, target in edges:
        if source not in indegree:
            indegree[source] = 0
        if target not in indegree:
            indegree[target] = 0
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1

    queue = deque(sorted((n for n, d in indegree.items() if d == 0), key=_course_sort_key))
    depth = {node: 0 for node in indegree}
    visited = 0

    while queue:
        node = queue.popleft()
        visited += 1
        for neighbor in sorted(adjacency[node], key=_course_sort_key):
            depth[neighbor] = max(depth[neighbor], depth[node] + 1)
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if visited < len(indegree):
        for node in indegree:
            depth.setdefault(node, 0)

    return depth


def build_mermaid_markup(completed_courses: Iterable[str] | None = None) -> str:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    course_data: dict[str, dict] = {}
    for raw_course, details in raw_data.items():
        if not isinstance(raw_course, str) or not isinstance(details, dict):
            continue
        course_data[normalize_course_code(raw_course)] = details

    completed = {
        normalize_course_code(code)
        for code in (completed_courses or [])
        if isinstance(code, str) and code.strip()
    }
    known_courses = set(course_data.keys())
    remaining_courses = sorted(
        [course for course in known_courses if course not in completed],
        key=_course_sort_key,
    )
    remaining_set = set(remaining_courses)

    if not remaining_courses:
        return ""

    nodes: set[str] = set(remaining_courses)
    edges: set[tuple[str, str]] = set()
    available_now: set[str] = set()
    needs_foundation_only: set[str] = set()

    for course in remaining_courses:
        details = course_data.get(course, {})
        prereqs = details.get("prereq_courses", [])
        has_internal_blocker = False
        has_external_blocker = False

        for prereq in prereqs:
            resolved, is_internal = _resolve_prereq_label(prereq, known_courses)
            if not resolved:
                continue

            resolved_norm = normalize_course_code(resolved)
            if resolved_norm in completed:
                continue

            if is_internal and resolved_norm in remaining_set:
                nodes.add(resolved_norm)
                edges.add((resolved_norm, course))
                has_internal_blocker = True
            elif not is_internal:
                has_external_blocker = True

        if not has_internal_blocker and not has_external_blocker:
            available_now.add(course)
        if has_external_blocker and not has_internal_blocker:
            needs_foundation_only.add(course)

    if needs_foundation_only:
        nodes.add(FOUNDATION_NODE)
        for course in needs_foundation_only:
            edges.add((FOUNDATION_NODE, course))

    levels = _compute_levels(nodes, edges)
    grouped_levels: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        grouped_levels[levels.get(node, 0)].append(node)

    node_id_map = {node: _node_id(node) for node in nodes}

    mermaid_markup = [
        "%%{init: {'theme': 'base', 'flowchart': {'curve': 'linear', 'nodeSpacing': 48, 'rankSpacing': 82}}}%%",
        "flowchart LR",
        "    classDef course fill:#f8fbff,stroke:#1f4b82,stroke-width:1.2px,color:#0b1f35;",
        "    classDef ready fill:#e8f7ee,stroke:#2e8b57,stroke-width:1.4px,color:#0f5132;",
        "    classDef foundation fill:#fff8e6,stroke:#b27a00,stroke-width:1.2px,color:#5f3f00;",
    ]

    for level in sorted(grouped_levels):
        mermaid_markup.append(f'    subgraph Tier_{level}["Tier {level + 1}"]')
        mermaid_markup.append("        direction TB")
        for node in sorted(grouped_levels[level], key=_course_sort_key):
            mermaid_markup.append(f'        {node_id_map[node]}["{node}"]')
        mermaid_markup.append("    end")

    for source, target in sorted(
        edges,
        key=lambda edge: (_course_sort_key(edge[0]), _course_sort_key(edge[1])),
    ):
        mermaid_markup.append(f"    {node_id_map[source]} --> {node_id_map[target]}")

    for node in sorted(nodes, key=_course_sort_key):
        node_id = node_id_map[node]
        if node == FOUNDATION_NODE:
            mermaid_markup.append(f"    class {node_id} foundation;")
        elif node in available_now:
            mermaid_markup.append(f"    class {node_id} ready;")
        else:
            mermaid_markup.append(f"    class {node_id} course;")

    return "\n".join(mermaid_markup) + "\n"


def mermaid_image_url(mermaid_markup: str) -> str:
    graph_bytes = mermaid_markup.encode("utf-8")
    encoded = base64.urlsafe_b64encode(graph_bytes).decode("ascii")
    return f"https://mermaid.ink/svg/{encoded}?bgColor=ffffff"


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
    return (
        mermaid_image_url(markup),
        "Flowchart generated successfully. Green nodes are available with current prerequisites.",
    )
